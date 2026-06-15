# Codebase Discrepancies

Issues discovered while mapping the system architecture on 2026-06-15. These are
mismatches between the frontend's expectations and the backend implementation as
currently checked in.

## 1. Frontend calls API endpoints that the backend does not define

`client/src/api.js` issues requests to two endpoint groups that have **no matching
route handlers** in `server/main.py` (which ends at line 309 with only the read
endpoints, `spending/*`, and `reports/*`):

### `/api/tasks` — full CRUD
- `getTasks()` &rarr; `GET /api/tasks`
- `createTask()` &rarr; `POST /api/tasks`
- `deleteTask(taskId)` &rarr; `DELETE /api/tasks/{taskId}`
- `toggleTask(taskId)` &rarr; `PATCH /api/tasks/{taskId}`

Consumed by `client/src/components/TasksModal.vue`.

### `/api/purchase-orders`
- `createPurchaseOrder(data)` &rarr; `POST /api/purchase-orders`
- `getPurchaseOrderByBacklogItem(backlogItemId)` &rarr; `GET /api/purchase-orders/{backlogItemId}`

Note: a `CreatePurchaseOrderRequest` Pydantic model **is** defined in `main.py`
(lines 115-121), and `purchase_orders.json` data **is** loaded, but no route uses
them. This suggests the backend implementation was started but the routes were
never wired up.

**Impact:** Any UI action that creates/reads tasks or purchase orders will fail
with a 404 against the current backend.

**Possible explanations (unconfirmed):**
- The handlers live in a file other than the `main.py` that was reviewed.
- The frontend was built ahead of the backend.
- Routes were removed/lost from `main.py`.

**Suggested next step:** Confirm whether these handlers exist anywhere; if not,
implement them following the existing endpoint + Pydantic pattern.

---

## 2. `total_backlog_items` ignores active filters

In `GET /api/dashboard/summary` (`server/main.py:200`), `total_backlog_items` is
computed from the unfiltered global `backlog_items` list, while every other metric
in the same response respects the warehouse/category/status/month filters. The
backlog count therefore stays constant regardless of the selected filters, which
is likely inconsistent with user expectations for a filtered dashboard.

---

## 3. Documentation vs. data: stated time range

`server/mock_data.py` docstring states "All data is from September 2025", but the
backend's quarter handling (`QUARTER_MAP`) and `filter_by_month` support the full
`2025-01` through `2025-12` range, and the reports endpoints bucket orders across
all four quarters of 2025. The docstring appears stale relative to the actual data
span. (Worth verifying against the JSON contents.)
