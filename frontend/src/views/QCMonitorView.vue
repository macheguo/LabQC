<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { X } from 'lucide-vue-next'
import PageHeader from '@/components/shared/PageHeader.vue'
import ExportButton from '@/components/shared/ExportButton.vue'
import FileDropZone from '@/components/upload/FileDropZone.vue'
import LJChart from '@/components/charts/LJChart.vue'
import ViolationTable from '@/components/tables/ViolationTable.vue'
import RunSummaryTable from '@/components/tables/RunSummaryTable.vue'
import { Button } from '@/components/ui/button'
import { useQcStore } from '@/stores/qcStore'
import { printReport } from '@/utils/printReport'

const { t } = useI18n()
const store = useQcStore()

// --- Instrument/experiment type config ---
const instrumentTypes = [
  {
    id: 'rt-pcr',
    label: t('qc.rtPcr'),
    instruments: ['QuantStudio 5', 'QuantStudio 7', 'Bio-Rad CFX96', 'Bio-Rad CFX Connect', 'Roche LightCycler 480', 'Cepheid GeneXpert', 'Other'],
    assays: ['SARS-CoV-2', 'HIV-1 RNA', 'HBV DNA', 'HCV RNA', 'TB/MTB', 'Influenza A/B', 'HPV', 'Other'],
    showChannel: true,
  },
  {
    id: 'chemistry',
    label: t('qc.clinicalChemistry'),
    instruments: ['Cobas c501', 'Cobas c701', 'Vitros 5600', 'Architect c8000', 'AU5800', 'Other'],
    assays: ['Glucose', 'Creatinine', 'BUN', 'Total Cholesterol', 'HDL', 'LDL', 'Triglycerides', 'ALT', 'AST', 'ALP', 'Bilirubin', 'HbA1c', 'Other'],
    showChannel: false,
  },
  {
    id: 'hematology',
    label: t('qc.hematology'),
    instruments: ['Sysmex XN-1000', 'Sysmex XN-2000', 'Beckman Coulter DxH 800', 'Mindray BC-6800', 'Other'],
    assays: ['CBC (WBC)', 'CBC (RBC)', 'Hemoglobin', 'Hematocrit', 'Platelet Count', 'MCV', 'MCH', 'MCHC', 'Other'],
    showChannel: false,
  },
  {
    id: 'immunoassay',
    label: t('qc.immunoassay'),
    instruments: ['Cobas e801', 'Cobas e601', 'Architect i2000', 'Vitros ECi', 'Liaison XL', 'Other'],
    assays: ['TSH', 'FT4', 'FT3', 'Troponin I', 'CK-MB', 'BNP', 'PSA', 'CEA', 'CA-125', 'AFP', 'Ferritin', 'Vitamin D', 'Other'],
    showChannel: false,
  },
  {
    id: 'coagulation',
    label: t('qc.coagulation'),
    instruments: ['Sysmex CS-5100', 'Sysmex CS-2500', 'Stago STA-R Max', 'ACL TOP', 'Other'],
    assays: ['PT/INR', 'APTT', 'Fibrinogen', 'D-Dimer', 'Other'],
    showChannel: false,
  },
  {
    id: 'other',
    label: t('qc.otherCustom'),
    instruments: [],
    assays: [],
    showChannel: false,
  },
]

const selectedType = ref('')
const selectedInstrument = ref('')
const customInstrument = ref('')
const selectedAssay = ref('')
const customAssay = ref('')
const channel = ref('')
const reagentLotId = ref('')
const controlLotId = ref('')

const selectedFile = ref(null)
const uploadStatus = ref('idle')
const runsLoading = ref(false)

// Error toast
const errorMsg = ref('')
const showError = ref(false)

// Column mapping
const showColumnMapping = ref(false)
const colValue = ref('')
const colLevel = ref('')
const colMean = ref('')
const colSD = ref('')
const colTarget = ref('')

const currentConfig = computed(() => instrumentTypes.find(t => t.id === selectedType.value) || null)
const instrumentOptions = computed(() => currentConfig.value?.instruments || [])
const assayOptions = computed(() => currentConfig.value?.assays || [])
const showChannel = computed(() => currentConfig.value?.showChannel ?? false)

const effectiveInstrument = computed(() => {
  if (selectedInstrument.value === 'Other') return customInstrument.value || 'Other'
  return selectedInstrument.value || 'Unknown'
})

const effectiveAssay = computed(() => {
  if (selectedAssay.value === 'Other') return customAssay.value || 'Other'
  return selectedAssay.value || 'Unknown'
})

// Reset dependent fields and clear results when type changes
watch(selectedType, () => {
  selectedInstrument.value = ''
  customInstrument.value = ''
  selectedAssay.value = ''
  customAssay.value = ''
  channel.value = ''
  selectedFile.value = null
  uploadStatus.value = 'idle'
  showColumnMapping.value = false
  dismissError()
  store.clearAnalysis()
})

function onFileSelected(file) {
  selectedFile.value = file
  uploadStatus.value = 'idle'
  showColumnMapping.value = false
  dismissError()
  store.clearAnalysis()
}

function showErrorToast(msg) {
  errorMsg.value = msg
  showError.value = true
}

function dismissError() {
  errorMsg.value = ''
  showError.value = false
}

async function handleUpload() {
  if (!selectedFile.value) return
  dismissError()

  const metadata = {
    instrument: effectiveInstrument.value,
    assay: effectiveAssay.value,
  }
  if (channel.value) metadata.channel = channel.value
  if (reagentLotId.value) metadata.reagent_lot_id = reagentLotId.value
  if (controlLotId.value) metadata.control_lot_id = controlLotId.value

  uploadStatus.value = 'uploading'

  try {
    const run = await store.upload(selectedFile.value, metadata)
    uploadStatus.value = 'parsing'
    await store.analyze(run.id)
    uploadStatus.value = 'complete'
    loadRuns()
  } catch (e) {
    uploadStatus.value = 'error'
    const msg = e.message || t('parser.unsupportedFormat')
    showErrorToast(msg)
    if (msg.toLowerCase().includes('no data points could be parsed')) {
      showColumnMapping.value = true
    }
  }
}

async function retryUploadWithMapping() {
  if (!selectedFile.value) return
  dismissError()

  const mapping = {}
  if (colValue.value) mapping.value = colValue.value
  if (colLevel.value) mapping.level = colLevel.value
  if (colMean.value) mapping.mean = colMean.value
  if (colSD.value) mapping.sd = colSD.value
  if (colTarget.value) mapping.target = colTarget.value

  const metadata = {
    instrument: effectiveInstrument.value,
    assay: effectiveAssay.value,
    column_mapping: JSON.stringify(mapping),
  }
  if (channel.value) metadata.channel = channel.value
  if (reagentLotId.value) metadata.reagent_lot_id = reagentLotId.value
  if (controlLotId.value) metadata.control_lot_id = controlLotId.value

  uploadStatus.value = 'uploading'

  try {
    const run = await store.upload(selectedFile.value, metadata)
    showColumnMapping.value = false
    uploadStatus.value = 'parsing'
    await store.analyze(run.id)
    uploadStatus.value = 'complete'
    loadRuns()
  } catch (e) {
    uploadStatus.value = 'error'
    showErrorToast(e.message || t('parser.unsupportedFormat'))
  }
}

const chartData = computed(() => {
  const result = store.analysisResult
  if (!result || !result.evaluated_points || result.evaluated_points.length === 0) return null
  return {
    data_points: result.evaluated_points,
    mean: result.summary_stats?.mean ?? null,
    sd: result.summary_stats?.sd ?? null,
  }
})

const violations = computed(() => {
  const result = store.analysisResult
  if (!result) return []
  return result.violations || []
})

async function loadRuns() {
  runsLoading.value = true
  try { await store.loadRuns() } finally { runsLoading.value = false }
}

function handleSelectRun(runId) {
  store.loadRunDetail(runId)
}

async function handleDeleteRun(runId) {
  try {
    await store.removeRun(runId)
    loadRuns()
  } catch (e) {
    showErrorToast(e.message || t('shared.error'))
  }
}

function handleExport() {
  printReport({
    title: t('qc.title'),
    subtitle: `${effectiveAssay.value} | ${effectiveInstrument.value}`,
  })
}

onMounted(() => { loadRuns() })
</script>

<template>
  <div class="view">
    <PageHeader :title="t('qc.title')" :subtitle="t('qc.subtitle')">
      <template #actions>
        <ExportButton @export="handleExport" />
      </template>
    </PageHeader>

    <div class="view__body">
      <!-- Error Toast -->
      <Teleport to="body">
        <Transition name="toast">
          <div v-if="showError" class="error-toast">
            <span class="error-toast__text">{{ errorMsg }}</span>
            <button class="error-toast__close" @click="dismissError">
              <X :size="16" :stroke-width="2" />
            </button>
          </div>
        </Transition>
      </Teleport>

      <!-- Upload Section -->
      <section class="section">
        <h2 class="section__title">{{ t('qc.uploadSection') }}</h2>

        <div class="upload-card">
          <!-- Step 1: Experiment type -->
          <div class="upload-row">
            <div class="field">
              <label class="field__label">{{ t('qc.experimentType') }}</label>
              <select v-model="selectedType" class="field__select">
                <option value="" disabled>{{ t('qc.experimentType') }}...</option>
                <option v-for="opt in instrumentTypes" :key="opt.id" :value="opt.id">{{ opt.label }}</option>
              </select>
            </div>

            <div v-if="currentConfig" class="field">
              <label class="field__label">{{ t('qc.instrument') }}</label>
              <select v-if="instrumentOptions.length" v-model="selectedInstrument" class="field__select">
                <option value="" disabled>{{ t('qc.instrument') }}...</option>
                <option v-for="i in instrumentOptions" :key="i" :value="i">{{ i }}</option>
              </select>
              <input v-else v-model="customInstrument" class="field__input" :placeholder="t('qc.instrument')" />
            </div>

            <div v-if="currentConfig" class="field">
              <label class="field__label">{{ t('qc.assay') }}</label>
              <select v-if="assayOptions.length" v-model="selectedAssay" class="field__select">
                <option value="" disabled>{{ t('qc.assay') }}...</option>
                <option v-for="a in assayOptions" :key="a" :value="a">{{ a }}</option>
              </select>
              <input v-else v-model="customAssay" class="field__input" :placeholder="t('qc.assay')" />
            </div>
          </div>

          <!-- Step 2: Optional fields -->
          <div v-if="currentConfig" class="upload-row">
            <div v-if="showChannel" class="field">
              <label class="field__label">{{ t('qc.channel') }}</label>
              <input v-model="channel" class="field__input" placeholder="e.g. FAM" />
            </div>
            <div class="field">
              <label class="field__label">{{ t('qc.reagentLot') }}</label>
              <input v-model="reagentLotId" class="field__input" placeholder="Lot #" />
            </div>
            <div class="field">
              <label class="field__label">{{ t('qc.controlLot') }}</label>
              <input v-model="controlLotId" class="field__input" placeholder="Lot #" />
            </div>
          </div>

          <!-- Step 3: Upload button + File picker -->
          <div class="upload-row upload-row--file">
            <Button
              :disabled="!selectedFile || !selectedType || uploadStatus === 'uploading' || uploadStatus === 'parsing'"
              @click="handleUpload"
            >
              {{ uploadStatus === 'uploading' ? t('qc.uploading') : uploadStatus === 'parsing' ? t('shared.loading') : t('qc.upload') }}
            </Button>
            <FileDropZone @file-selected="onFileSelected" />
          </div>
        </div>
      </section>

      <!-- Column Mapping Fallback -->
      <section v-if="showColumnMapping" class="section">
        <div class="column-mapping">
          <h3 class="column-mapping__title">{{ t('parser.invalidColumnMapping') }}</h3>
          <p class="mapping-hint">{{ t('parser.noDataPoints') }}</p>
          <div class="mapping-grid">
            <div class="field">
              <label class="field__label">{{ t('qc.assay') }} *</label>
              <input v-model="colValue" class="field__input" placeholder="e.g. Cq, Value, Result" />
            </div>
            <div class="field">
              <label class="field__label">{{ t('qc.assay') }}</label>
              <input v-model="colLevel" class="field__input" placeholder="e.g. Level, Sample" />
            </div>
            <div class="field">
              <label class="field__label">{{ t('qc.mean') }} ({{ t('shared.save') }})</label>
              <input v-model="colMean" class="field__input" placeholder="e.g. Mean" />
            </div>
            <div class="field">
              <label class="field__label">{{ t('qc.sd') }} ({{ t('shared.save') }})</label>
              <input v-model="colSD" class="field__input" placeholder="e.g. SD" />
            </div>
          </div>
          <Button :disabled="!colValue" @click="retryUploadWithMapping">{{ t('qc.upload') }}</Button>
        </div>
      </section>

      <!-- LJ Chart -->
      <section v-if="chartData" class="section">
        <h2 class="section__title">{{ t('qc.ljChart') }}</h2>
        <div class="section__content">
          <LJChart :data-points="chartData.data_points || []" :mean="chartData.mean" :sd="chartData.sd" />
        </div>
      </section>

      <section v-else-if="store.loading && uploadStatus === 'parsing'" class="section">
        <h2 class="section__title">{{ t('qc.ljChart') }}</h2>
        <div class="skeleton skeleton--chart" />
      </section>

      <!-- Violations -->
      <section v-if="store.analysisResult" class="section">
        <h2 class="section__title">{{ t('qc.violationDetails') }}</h2>
        <div class="section__content">
          <ViolationTable :violations="violations" />
        </div>
      </section>

      <!-- Run History -->
      <section class="section no-print">
        <h2 class="section__title">{{ t('qc.runHistory') }}</h2>
        <div class="section__content">
          <template v-if="runsLoading && store.runs.length === 0">
            <div class="skeleton skeleton--table" />
          </template>
          <template v-else>
            <RunSummaryTable :runs="store.runs" @select-run="handleSelectRun" @delete-run="handleDeleteRun" />
          </template>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.view {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.view__body {
  flex: 1;
  overflow-y: auto;
  padding: 0 28px 40px;
}

.section { padding-top: 24px; }

.section__title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.section__content {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  overflow: hidden;
}

/* Upload card */
.upload-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.upload-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: flex-end;
}

.upload-row--file {
  align-items: center;
  gap: 12px;
}

/* Compact fields */
.field {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 140px;
  flex: 1;
  max-width: 220px;
}

.field__label {
  font-size: 11px;
  font-weight: 500;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.field__input {
  height: 32px;
  padding: 0 10px;
  font-size: 13px;
  color: var(--text-primary);
  background: var(--bg-surface-2);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  outline: none;
  font-family: inherit;
  transition: border-color 0.15s;
}

.field__input:focus { border-color: var(--border-strong); }
.field__input::placeholder { color: var(--text-muted); }

.field__select {
  height: 32px;
  padding: 0 28px 0 10px;
  font-size: 13px;
  color: var(--text-primary);
  background: var(--bg-surface-2);
  border: 1px solid var(--border-subtle);
  border-radius: 6px;
  outline: none;
  font-family: inherit;
  -webkit-appearance: none;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23666' stroke-width='2'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 8px center;
}

.field__select:focus { border-color: var(--border-strong); }

/* Column mapping fallback */
.column-mapping {
  background: var(--bg-surface);
  border: 1px solid var(--border-warning);
  border-radius: 8px;
  padding: 20px;
}

.column-mapping__title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-warning);
  margin-bottom: 8px;
}

.mapping-hint {
  color: var(--text-muted);
  font-size: 13px;
  margin-bottom: 16px;
}

.mapping-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

/* Error toast */
.error-toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  background: var(--color-danger);
  color: white;
  padding: 12px 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 1000;
  box-shadow: 0 8px 24px rgba(0,0,0,0.3);
  max-width: 420px;
}

.error-toast__text { font-size: 13px; flex: 1; }
.error-toast__close {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  opacity: 0.7;
}

.error-toast__close:hover { opacity: 1; }

.toast-enter-active, .toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(12px); }

.skeleton {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  animation: pulse 1.5s ease-in-out infinite;
}

.skeleton--table { height: 200px; }
.skeleton--chart { height: 300px; }

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@media print {
  .no-print { display: none; }
}
</style>
