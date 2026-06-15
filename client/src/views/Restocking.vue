<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <!-- Budget slider card -->
      <div class="card budget-card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.budgetLabel') }}</h3>
        </div>
        <div class="budget-controls">
          <div class="budget-display">
            <span class="budget-amount">{{ currencySymbol }}{{ budget.toLocaleString() }}</span>
          </div>
          <input
            type="range"
            class="budget-slider"
            v-model.number="budget"
            min="0"
            max="500000"
            step="5000"
          />
          <div class="budget-range-labels">
            <span>{{ currencySymbol }}0</span>
            <span>{{ currencySymbol }}500,000</span>
          </div>
        </div>
      </div>

      <!-- Summary stats -->
      <div class="stats-grid">
        <div class="stat-card info">
          <div class="stat-label">{{ t('restocking.selectedItems') }}</div>
          <div class="stat-value">{{ selectedCandidates.length }}</div>
        </div>
        <div class="stat-card success">
          <div class="stat-label">{{ t('restocking.selectedTotal') }}</div>
          <div class="stat-value">{{ currencySymbol }}{{ orderTotal.toLocaleString() }}</div>
        </div>
        <div class="stat-card" :class="budgetRemaining >= 0 ? '' : 'danger'">
          <div class="stat-label">{{ t('restocking.budgetRemaining') }}</div>
          <div class="stat-value">{{ currencySymbol }}{{ budgetRemaining.toLocaleString() }}</div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">{{ t('restocking.budgetUtilization') }}</div>
          <div class="stat-value">{{ budgetUtilization }}%</div>
        </div>
      </div>

      <!-- Success banner -->
      <div v-if="successMessage" class="success-banner">
        {{ successMessage }}
      </div>

      <!-- Recommendations table -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.recommendations') }}</h3>
          <button
            class="place-order-btn"
            :disabled="selectedCandidates.length === 0 || submitting"
            @click="placeOrder"
          >
            {{ submitting ? t('restocking.placingOrder') : t('restocking.placeOrder') }}
          </button>
        </div>

        <div v-if="candidates.length === 0" class="no-recommendations">
          {{ t('restocking.noRecommendations') }}
        </div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th class="col-status-indicator"></th>
                <th>{{ t('restocking.table.item') }}</th>
                <th>{{ t('restocking.table.sku') }}</th>
                <th>{{ t('restocking.table.trend') }}</th>
                <th>{{ t('restocking.table.warehouse') }}</th>
                <th class="col-number">{{ t('restocking.table.restockQty') }}</th>
                <th class="col-number">{{ t('restocking.table.unitCost') }}</th>
                <th class="col-number">{{ t('restocking.table.estCost') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="candidate in candidates"
                :key="candidate.item_sku"
                :class="candidate.selected ? 'row-selected' : 'row-dimmed'"
              >
                <td class="col-status-indicator">
                  <span v-if="candidate.selected" class="selection-dot selected-dot"></span>
                  <span v-else class="selection-dot unselected-dot"></span>
                </td>
                <td>{{ candidate.item_name }}</td>
                <td><strong>{{ candidate.item_sku }}</strong></td>
                <td>
                  <span :class="['badge', candidate.trend]">{{ candidate.trend }}</span>
                </td>
                <td>{{ candidate.warehouse }}</td>
                <td class="col-number">{{ candidate.restock_qty.toLocaleString() }}</td>
                <td class="col-number">{{ currencySymbol }}{{ candidate.unit_cost.toLocaleString() }}</td>
                <td class="col-number">
                  <strong>{{ currencySymbol }}{{ candidate.est_cost.toLocaleString() }}</strong>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'

const TREND_PRIORITY = { increasing: 0, stable: 1, decreasing: 2 }

export default {
  name: 'Restocking',
  setup() {
    const { t, currentCurrency } = useI18n()

    const currencySymbol = computed(() => currentCurrency.value === 'JPY' ? '¥' : '$')

    const forecasts = ref([])
    const loading = ref(true)
    const error = ref(null)
    const submitting = ref(false)
    const successMessage = ref(null)
    const budget = ref(100000)

    // Items with a positive gap — the raw candidate pool
    const candidates = computed(() => {
      const trendOrder = TREND_PRIORITY

      const pool = forecasts.value
        .filter(f => (f.forecasted_demand - f.current_demand) > 0)
        .map(f => {
          const restock_qty = f.forecasted_demand - f.current_demand
          const est_cost = restock_qty * f.unit_cost
          return {
            item_sku: f.item_sku,
            item_name: f.item_name,
            trend: f.trend,
            warehouse: f.warehouse,
            unit_cost: f.unit_cost,
            restock_qty,
            est_cost,
            selected: false
          }
        })

      // Sort: trend priority asc, then gap desc
      pool.sort((a, b) => {
        const trendDiff = (trendOrder[a.trend] ?? 9) - (trendOrder[b.trend] ?? 9)
        if (trendDiff !== 0) return trendDiff
        return b.restock_qty - a.restock_qty
      })

      // Greedy fill — mark selected items that fit within budget
      let running = 0
      for (const item of pool) {
        if (running + item.est_cost <= budget.value) {
          item.selected = true
          running += item.est_cost
        }
      }

      return pool
    })

    const selectedCandidates = computed(() => candidates.value.filter(c => c.selected))

    const orderTotal = computed(() =>
      selectedCandidates.value.reduce((sum, c) => sum + c.est_cost, 0)
    )

    const budgetRemaining = computed(() => budget.value - orderTotal.value)

    const budgetUtilization = computed(() => {
      if (budget.value === 0) return 0
      return Math.min(100, Math.round((orderTotal.value / budget.value) * 100))
    })

    const loadForecasts = async () => {
      loading.value = true
      error.value = null
      try {
        forecasts.value = await api.getDemandForecasts()
      } catch (err) {
        error.value = 'Failed to load demand forecasts: ' + err.message
        console.error(err)
      } finally {
        loading.value = false
      }
    }

    const placeOrder = async () => {
      if (selectedCandidates.value.length === 0 || submitting.value) return

      submitting.value = true
      successMessage.value = null
      error.value = null

      const items = selectedCandidates.value.map(c => ({
        sku: c.item_sku,
        name: c.item_name,
        quantity: c.restock_qty,
        unit_cost: c.unit_cost,
        warehouse: c.warehouse
      }))

      try {
        const result = await api.createSubmittedOrder({ items, budget: budget.value })
        successMessage.value = t('restocking.orderSuccess', { orderNumber: result.order_number })
      } catch (err) {
        error.value = t('restocking.orderError')
        console.error(err)
      } finally {
        submitting.value = false
      }
    }

    onMounted(loadForecasts)

    return {
      t,
      currencySymbol,
      forecasts,
      loading,
      error,
      submitting,
      successMessage,
      budget,
      candidates,
      selectedCandidates,
      orderTotal,
      budgetRemaining,
      budgetUtilization,
      placeOrder
    }
  }
}
</script>

<style scoped>
.budget-card {
  margin-bottom: 1.25rem;
}

.budget-controls {
  padding: 0.5rem 0;
}

.budget-display {
  margin-bottom: 1rem;
}

.budget-amount {
  font-size: 2rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.025em;
}

.budget-slider {
  width: 100%;
  height: 6px;
  appearance: none;
  -webkit-appearance: none;
  background: #e2e8f0;
  border-radius: 3px;
  outline: none;
  cursor: pointer;
  accent-color: #2563eb;
}

.budget-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #2563eb;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 1px 4px rgba(37, 99, 235, 0.4);
  transition: box-shadow 0.15s ease;
}

.budget-slider::-webkit-slider-thumb:hover {
  box-shadow: 0 1px 8px rgba(37, 99, 235, 0.6);
}

.budget-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #2563eb;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 1px 4px rgba(37, 99, 235, 0.4);
}

.budget-range-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  font-size: 0.813rem;
  color: #94a3b8;
}

.success-banner {
  background: #d1fae5;
  border: 1px solid #6ee7b7;
  color: #065f46;
  padding: 1rem 1.25rem;
  border-radius: 8px;
  margin-bottom: 1.25rem;
  font-size: 0.938rem;
  font-weight: 500;
}

.no-recommendations {
  padding: 2.5rem 1.25rem;
  text-align: center;
  color: #64748b;
  font-size: 0.938rem;
}

.place-order-btn {
  padding: 0.625rem 1.5rem;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease, opacity 0.2s ease;
}

.place-order-btn:hover:not(:disabled) {
  background: #1d4ed8;
}

.place-order-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.col-status-indicator {
  width: 32px;
  padding-left: 0.75rem;
}

.col-number {
  text-align: right;
}

.selection-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.selected-dot {
  background: #2563eb;
}

.unselected-dot {
  background: #cbd5e1;
}

.row-selected td {
  color: #0f172a;
}

.row-dimmed td {
  color: #94a3b8;
}

.row-dimmed strong {
  color: #94a3b8;
}

.row-dimmed .badge {
  opacity: 0.5;
}
</style>
