<script setup>
import { computed, defineAsyncComponent } from 'vue'
import { useI18n } from 'vue-i18n'
import PageHeader from '@/components/shared/PageHeader.vue'
import ExportButton from '@/components/shared/ExportButton.vue'
import SigmaInputForm from '@/components/forms/SigmaInputForm.vue'
import { useSigmaStore } from '@/stores/sigmaStore'
import { printReport } from '@/utils/printReport'

const { t } = useI18n()

const NMEDxChart = defineAsyncComponent(() =>
  import('@/components/charts/NMEDxChart.vue')
)

const sigma = useSigmaStore()

const hasResults = computed(() => sigma.results.length > 0)

function classColor(classification) {
  const map = {
    world_class: 'var(--color-success)',
    excellent: '#66BB6A',
    good: 'var(--color-warning)',
    marginal: '#FB8C00',
    unacceptable: 'var(--color-danger)',
  }
  return map[classification] || 'var(--text-muted)'
}

function classLabel(classification) {
  const map = {
    world_class: t('sigma.worldClass'),
    excellent: t('sigma.excellent'),
    good: t('sigma.good'),
    marginal: t('sigma.marginal'),
    unacceptable: t('sigma.unacceptable'),
  }
  return map[classification] || classification
}

function formatSigma(value) {
  return typeof value === 'number' ? value.toFixed(2) : '-'
}

function handleExport() {
  printReport({
    title: t('sigma.reportTitle'),
    subtitle: t('sigma.reportSubtitle', { count: sigma.results.length }),
  })
}

async function handleCalculate(inputs) {
  try {
    await sigma.calculate(inputs)
  } catch {
    // error is stored in sigma.error
  }
}
</script>

<template>
  <div class="view">
    <PageHeader :title="t('sigma.title')" :subtitle="t('sigma.subtitle')">
      <template #actions>
        <ExportButton v-if="hasResults" @export="handleExport" />
      </template>
    </PageHeader>

    <SigmaInputForm @submit="handleCalculate" />

    <!-- Loading skeleton -->
    <div v-if="sigma.loading" class="section section--loading">
      <div class="skeleton skeleton--table"></div>
    </div>

    <!-- Error -->
    <div v-else-if="sigma.error" class="section section--error">
      <p class="error-text">{{ sigma.error }}</p>
    </div>

    <!-- Results -->
    <template v-else-if="hasResults">
      <div class="section">
        <div class="section__header">
          <span class="section__title">{{ t('sigma.results') }}</span>
        </div>
        <div class="results-table-wrap">
          <table class="results-table">
            <thead>
              <tr>
                <th>{{ t('sigma.assay') }}</th>
                <th>{{ t('sigma.teaPercent') }}</th>
                <th>{{ t('sigma.biasPercent') }}</th>
                <th>{{ t('sigma.cvPercent') }}</th>
                <th>{{ t('sigma.sigmaValue') }}</th>
                <th>{{ t('sigma.classification') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in sigma.results" :key="r.assay">
                <td class="results-table__assay">{{ r.assay }}</td>
                <td class="results-table__num">{{ r.tea_percent ?? '-' }}</td>
                <td class="results-table__num">{{ r.bias_percent ?? '-' }}</td>
                <td class="results-table__num">{{ r.cv_percent ?? '-' }}</td>
                <td class="results-table__num">{{ formatSigma(r.sigma_score) }}</td>
                <td>
                  <span
                    class="classification-chip"
                    :style="{ color: classColor(r.classification), borderColor: classColor(r.classification) }"
                  >
                    {{ classLabel(r.classification) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <NMEDxChart :results="sigma.results" />

      <!-- Recommendations -->
      <div class="section">
        <div class="section__header">
          <span class="section__title">{{ t('sigma.recommendations') }}</span>
        </div>
        <div class="recommendations">
          <div
            v-for="r in sigma.results"
            :key="r.assay"
            class="recommendation"
          >
            <span class="recommendation__assay">{{ r.assay }}</span>
            <ul v-if="r.recommended_rules && r.recommended_rules.length" class="recommendation__list">
              <li v-for="(rec, i) in r.recommended_rules" :key="i">{{ rec }}</li>
            </ul>
            <p v-else class="recommendation__none">{{ t('sigma.noRecommendations') }}</p>
          </div>
        </div>
      </div>
    </template>

    <!-- Empty state -->
    <div v-else class="view__empty">
      <p class="view__empty-text">{{ t('sigma.emptyState') }}</p>
    </div>
  </div>
</template>

<style scoped>
.view {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.view__empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.view__empty-text {
  font-size: 15px;
  color: var(--text-muted);
  font-weight: 400;
}

.section {
  padding: 20px 28px;
  border-bottom: 1px solid var(--border-subtle);
}

.section--loading {
  padding: 20px 28px;
}

.section--error {
  padding: 20px 28px;
}

.section__header {
  margin-bottom: 12px;
}

.section__title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
}

.skeleton {
  border-radius: 6px;
  background: linear-gradient(
    90deg,
    var(--bg-surface-2) 25%,
    var(--bg-highlight) 50%,
    var(--bg-surface-2) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.skeleton--table {
  height: 160px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.error-text {
  font-size: 13px;
  color: var(--color-danger);
}

/* Results table */
.results-table-wrap {
  overflow-x: auto;
}

.results-table {
  width: 100%;
  border-collapse: collapse;
}

.results-table th {
  text-align: left;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
  padding: 8px 16px;
  border-bottom: 1px solid var(--border-subtle);
  white-space: nowrap;
}

.results-table td {
  font-size: 13px;
  color: var(--text-primary);
  padding: 10px 16px;
  border-bottom: 1px solid var(--border-subtle);
}

.results-table__assay {
  font-weight: 500;
}

.results-table__num {
  font-family: 'SF Mono', 'Cascadia Code', 'Fira Code', monospace;
  font-size: 12px;
}

.classification-chip {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 9999px;
  border: 1px solid;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

/* Recommendations */
.recommendations {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.recommendation {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.recommendation__assay {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.recommendation__list {
  list-style: disc;
  padding-left: 20px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.recommendation__list li {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.recommendation__none {
  font-size: 13px;
  color: var(--text-muted);
}
</style>
