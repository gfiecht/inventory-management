"""
Tests for the restocking submitted-orders API endpoints.
"""
import pytest

import main


@pytest.fixture
def reset_submitted_orders(monkeypatch):
    """Isolate tests that mutate submitted orders.

    Snapshots the in-memory list and stubs out the JSON persistence so tests
    don't write to disk, then restores the original contents afterwards.
    """
    original = list(main.submitted_orders)
    monkeypatch.setattr(main, "save_submitted_orders", lambda orders: None)
    yield
    main.submitted_orders.clear()
    main.submitted_orders.extend(original)


@pytest.fixture
def sample_restock_item():
    """A single valid restocking order item."""
    return {
        "sku": "WDG-001",
        "name": "Industrial Widget Type A",
        "quantity": 150,
        "unit_cost": 45.0,
        "warehouse": "San Francisco"
    }


class TestDemandForecastEnrichment:
    """The demand forecast now carries restocking cost/location fields."""

    def test_demand_has_unit_cost_and_warehouse(self, client):
        """Every demand forecast exposes unit_cost and warehouse."""
        response = client.get("/api/demand")
        assert response.status_code == 200

        data = response.json()
        assert len(data) > 0

        for forecast in data:
            assert "unit_cost" in forecast
            assert "warehouse" in forecast
            assert isinstance(forecast["unit_cost"], (int, float))
            assert forecast["unit_cost"] >= 0
            assert forecast["warehouse"] in ["San Francisco", "London", "Tokyo"]


class TestGetSubmittedOrders:
    """Test suite for GET /api/submitted-orders."""

    def test_get_submitted_orders_returns_list(self, client):
        """The endpoint returns a list."""
        response = client.get("/api/submitted-orders")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestCreateSubmittedOrder:
    """Test suite for POST /api/submitted-orders."""

    def test_create_submitted_order_success(self, client, reset_submitted_orders, sample_restock_item):
        """A valid restocking order is created with computed fields."""
        payload = {"items": [sample_restock_item], "budget": 100000}
        response = client.post("/api/submitted-orders", json=payload)
        assert response.status_code == 201

        order = response.json()
        assert order["status"] == "Submitted"
        assert order["order_number"].startswith("RST-")
        assert order["budget"] == 100000
        # 150 * 45.0
        assert abs(order["total_value"] - 6750.0) < 0.01
        # San Francisco lead time
        assert order["lead_time_days"] == 7
        assert "T" in order["order_date"]
        assert "T" in order["expected_delivery"]
        assert len(order["items"]) == 1
        assert order["items"][0]["sku"] == "WDG-001"

    def test_total_value_matches_items(self, client, reset_submitted_orders):
        """total_value is the sum of quantity * unit_cost across items."""
        payload = {
            "items": [
                {"sku": "GSK-203", "name": "High-Temperature Gasket",
                 "quantity": 100, "unit_cost": 12.25, "warehouse": "Tokyo"},
                {"sku": "FLT-405", "name": "Oil Filter Cartridge",
                 "quantity": 150, "unit_cost": 9.75, "warehouse": "San Francisco"},
            ],
            "budget": 50000
        }
        response = client.post("/api/submitted-orders", json=payload)
        assert response.status_code == 201

        order = response.json()
        expected = 100 * 12.25 + 150 * 9.75
        assert abs(order["total_value"] - expected) < 0.01

    def test_lead_time_is_max_across_warehouses(self, client, reset_submitted_orders):
        """Lead time is the longest among the order's warehouses."""
        payload = {
            "items": [
                {"sku": "FLT-405", "name": "Oil Filter Cartridge",
                 "quantity": 10, "unit_cost": 9.75, "warehouse": "San Francisco"},  # 7
                {"sku": "GSK-203", "name": "High-Temperature Gasket",
                 "quantity": 10, "unit_cost": 12.25, "warehouse": "Tokyo"},  # 18
            ],
            "budget": 50000
        }
        response = client.post("/api/submitted-orders", json=payload)
        assert response.status_code == 201
        assert response.json()["lead_time_days"] == 18

    def test_created_order_appears_in_get(self, client, reset_submitted_orders, sample_restock_item):
        """A submitted order is returned by the GET endpoint."""
        before = len(client.get("/api/submitted-orders").json())

        payload = {"items": [sample_restock_item], "budget": 100000}
        created = client.post("/api/submitted-orders", json=payload).json()

        after = client.get("/api/submitted-orders").json()
        assert len(after) == before + 1
        assert any(o["order_number"] == created["order_number"] for o in after)

    def test_create_over_budget_rejected(self, client, reset_submitted_orders, sample_restock_item):
        """An order whose total exceeds the budget is rejected with 400."""
        payload = {"items": [sample_restock_item], "budget": 1000}  # total 6750 > 1000
        response = client.post("/api/submitted-orders", json=payload)
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data
        assert "budget" in data["detail"].lower()

    def test_create_empty_items_rejected(self, client, reset_submitted_orders):
        """An order with no items is rejected with 400."""
        payload = {"items": [], "budget": 100000}
        response = client.post("/api/submitted-orders", json=payload)
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data
        assert "at least one" in data["detail"].lower()

    def test_create_missing_field_validation(self, client, reset_submitted_orders):
        """A malformed item payload fails Pydantic validation with 422."""
        payload = {"items": [{"sku": "WDG-001", "name": "Industrial Widget Type A"}], "budget": 100000}
        response = client.post("/api/submitted-orders", json=payload)
        assert response.status_code == 422
