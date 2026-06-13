<template>
  <div class="activate-page">
    <div class="activate-card">
      <div class="logo-row">
        <img src="@/assets/ksc-logo.svg" alt="LabQC" class="logo" />
      </div>
      <h2>{{ t('activate.title') }}</h2>
      <p class="subtitle">{{ t('activate.subtitle') }}</p>

      <!-- Already licensed: show status -->
      <div v-if="licenseValid" class="status-ok">
        <span class="icon">✅</span> {{ licenseMsg }}
      </div>

      <!-- No license: show activation form -->
      <form v-else @submit.prevent="handleActivate" class="activate-form">
        <label>{{ t('activate.label') }}</label>
        <textarea
          v-model="token"
          :placeholder="t('activate.placeholder')"
          rows="4"
          class="token-input"
          required
        ></textarea>
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? t('activate.activating') : t('activate.button') }}
        </button>
      </form>

      <p class="machine-id">Machine ID: {{ machineId }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { fetchLicenseStatus, activateLicense } from '@/api/licenseApi'

const { t } = useI18n()
const token = ref('')
const loading = ref(false)
const error = ref('')
const licenseValid = ref(false)
const licenseMsg = ref('')
const machineId = ref('')

onMounted(async () => {
  try {
    const s = await fetchLicenseStatus()
    licenseValid.value = s.valid
    licenseMsg.value = s.message
    machineId.value = s.machine_id || 'N/A'
  } catch {
    licenseValid.value = false
    licenseMsg.value = '无法连接服务'
  }
})

async function handleActivate() {
  error.value = ''
  loading.value = true
  try {
    const r = await activateLicense(token.value.trim())
    licenseValid.value = true
    licenseMsg.value = r.message
  } catch {
    error.value = '激活失败，请检查许可证密钥是否正确'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.activate-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg);
}
.activate-card {
  background: #fff;
  border: 1px solid var(--card-border, #dde0e4);
  border-radius: 10px;
  padding: 2rem;
  width: 440px;
  max-width: 90vw;
  text-align: center;
}
.logo-row { margin-bottom: 1rem; }
.logo { height: 48px; }
h2 { color: var(--theme); margin-bottom: 0.25rem; }
.subtitle { color: #666; font-size: 0.9rem; margin-bottom: 1.5rem; }
.status-ok { color: #2e7d32; font-size: 1rem; margin: 1rem 0; }
.activate-form { text-align: left; }
label { display: block; font-weight: 600; margin-bottom: 0.5rem; color: #333; }
.token-input {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-family: monospace;
  font-size: 0.8rem;
  resize: vertical;
}
.error { color: #c62828; font-size: 0.85rem; margin-top: 0.5rem; }
.btn-primary {
  margin-top: 1rem;
  width: 100%;
  padding: 0.65rem;
  background: var(--theme);
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
}
.btn-primary:disabled { opacity: 0.6; cursor: default; }
.machine-id {
  margin-top: 1.5rem;
  font-size: 0.75rem;
  color: #999;
  font-family: monospace;
}
</style>
