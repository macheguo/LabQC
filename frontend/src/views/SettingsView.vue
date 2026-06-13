<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import PageHeader from '@/components/shared/PageHeader.vue'
import StatusBadge from '@/components/shared/StatusBadge.vue'
import UserManagementCard from '@/components/settings/UserManagementCard.vue'
import { Button } from '@/components/ui/button'
import {
  getLisConfig, updateLisConfig, testParseHl7, restartLisListener, getLisMessages,
} from '@/api/settingsApi'
import {
  getAiConfig, setApiKey, removeApiKey, setBaseUrl, setModel,
} from '@/api/settingsApi'

const { t } = useI18n()

const isAdmin = computed(() => {
  try {
    const u = JSON.parse(localStorage.getItem('labqc_user') || '{}')
    return !!u.is_admin
  } catch { return false }
})

// ── LIS config state ─────────────────────────────────────────
const lisLoading = ref(false)
const lisSaving = ref(false)
const lisEnabled = ref(false)
const lisHost = ref('0.0.0.0')
const lisPort = ref(5020)
const lisStatus = ref('stopped')
const lisError = ref('')

// Test parse
const testHl7Input = ref('MSH|^~\\&|LIS|HOSPITAL|LabQC|LAB||20240601120000||ORU^R01|MSG001|P|2.3.1\rPID|1||12345||张三^张\rOBR|1|||GLU^葡萄糖\rOBX|1|NM|GLU^葡萄糖||5.6|mmol/L|3.9-6.1|N')
const testParseResult = ref(null)
const testParseError = ref('')

// Received messages
const lisMessages = ref([])

// ── AI Config state ──────────────────────────────────────────
const aiLoading = ref(false)
const aiSaving = ref(false)
const aiApiKeySet = ref(false)
const aiApiKey = ref('')
const aiBaseUrl = ref('')
const aiModel = ref('gpt-4o')
const aiError = ref('')
const aiSuccess = ref('')
const showApiKey = ref(false)

// ── Load LIS config ─────────────────────────────────────────

async function loadLisConfig() {
  lisLoading.value = true
  try {
    const cfg = await getLisConfig()
    lisEnabled.value = cfg.enabled
    lisHost.value = cfg.host
    lisPort.value = cfg.port
    lisStatus.value = cfg.status
    lisError.value = cfg.error
  } catch (e) {
    lisError.value = e.message || '加载失败'
  } finally {
    lisLoading.value = false
  }
}

async function saveLisConfig() {
  lisSaving.value = true
  lisError.value = ''
  try {
    const result = await updateLisConfig({
      enabled: lisEnabled.value,
      host: lisHost.value,
      port: lisPort.value,
    })
    lisStatus.value = result.status
    lisError.value = result.error
  } catch (e) {
    lisError.value = e.message || '保存失败'
  } finally {
    lisSaving.value = false
  }
}

async function handleTestParse() {
  testParseResult.value = null
  testParseError.value = ''
  try {
    const r = await testParseHl7(testHl7Input.value)
    if (r.success) {
      testParseResult.value = r.parsed
    } else {
      testParseError.value = r.error
    }
  } catch (e) {
    testParseError.value = e.message || '测试失败'
  }
}

async function handleRestart() {
  lisError.value = ''
  try {
    const r = await restartLisListener()
    lisStatus.value = r.status
    lisError.value = r.error
    await loadLisMessages()
  } catch (e) {
    lisError.value = e.message || '重启失败'
  }
}

async function loadLisMessages() {
  try {
    lisMessages.value = await getLisMessages(10)
  } catch {
    // silent
  }
}

const statusBadge = computed(() => {
  if (lisStatus.value === 'running') return 'pass'
  if (lisStatus.value === 'error') return 'fail'
  return 'inactive'
})

// ── Load AI config ─────────────────────────────────────────

async function loadAiConfig() {
  aiLoading.value = true
  try {
    const cfg = await getAiConfig()
    aiApiKeySet.value = cfg.api_key_set
    aiBaseUrl.value = cfg.base_url || ''
    aiModel.value = cfg.model || 'gpt-4o'
  } catch (e) {
    aiError.value = e.message || '加载失败'
  } finally {
    aiLoading.value = false
  }
}

async function saveAiConfig() {
  aiSaving.value = true
  aiError.value = ''
  aiSuccess.value = ''
  try {
    if (aiApiKey.value) {
      await setApiKey(aiApiKey.value)
      aiApiKeySet.value = true
    }
    if (aiBaseUrl.value) {
      await setBaseUrl(aiBaseUrl.value)
    }
    await setModel(aiModel.value)
    aiApiKey.value = '' // clear local copy after save
    aiSuccess.value = 'AI 配置已保存'
    setTimeout(() => { aiSuccess.value = '' }, 3000)
  } catch (e) {
    aiError.value = e.message || '保存失败'
  } finally {
    aiSaving.value = false
  }
}

async function handleClearApiKey() {
  try {
    await removeApiKey()
    aiApiKeySet.value = false
    aiApiKey.value = ''
    aiSuccess.value = 'API Key 已清除'
    setTimeout(() => { aiSuccess.value = '' }, 3000)
  } catch (e) {
    aiError.value = e.message || '清除失败'
  }
}

onMounted(() => {
  loadLisConfig()
  loadLisMessages()
  loadAiConfig()
})
</script>

<template>
  <div class="settings-page">
    <PageHeader :title="t('settings.title')" :subtitle="t('settings.subtitle')" />

    <div class="cards">
      <!-- AI Configuration Card -->
      <div class="card">
        <h2 class="card-title">AI 模型配置</h2>
        <p class="card-desc">配置大语言模型接口，用于法规助手智能问答。支持 OpenAI 兼容 API。</p>

        <div v-if="aiLoading" class="loading-text">加载中...</div>
        <template v-else>
          <!-- API Key status -->
          <div class="form-row">
            <label class="form-label">API Key</label>
            <StatusBadge :status="aiApiKeySet ? 'pass' : 'inactive'" :label="aiApiKeySet ? '已设置' : '未设置'" />
          </div>

          <!-- API Key input -->
          <div class="form-row">
            <div class="form-field" style="flex:1">
              <div class="input-with-icon">
                <input
                  :type="showApiKey ? 'text' : 'password'"
                  v-model="aiApiKey"
                  class="form-input"
                  :placeholder="aiApiKeySet ? '留空则保留当前密钥' : '输入 API Key，如 sk-...'"
                />
                <button type="button" class="toggle-vis" @click="showApiKey = !showApiKey" :title="showApiKey ? '隐藏' : '显示'">
                  {{ showApiKey ? '🙈' : '👁' }}
                </button>
              </div>
            </div>
            <Button
              variant="outline"
              size="sm"
              :disabled="!aiApiKeySet"
              @click="handleClearApiKey"
              style="white-space:nowrap;margin-left:4px"
            >
              清除密钥
            </Button>
          </div>

          <!-- Base URL -->
          <div class="form-row">
            <div class="form-field" style="flex:1">
              <label class="form-label-sm">Base URL（API 地址）</label>
              <input
                v-model="aiBaseUrl"
                class="form-input"
                placeholder="https://api.openai.com/v1（留空使用默认）"
              />
            </div>
          </div>
          <div class="url-hints">
            <span>常用地址：</span>
            <button type="button" class="hint-link" @click="aiBaseUrl = 'https://api.openai.com/v1'">OpenAI</button>
            <button type="button" class="hint-link" @click="aiBaseUrl = 'https://api.deepseek.com/v1'">DeepSeek</button>
            <button type="button" class="hint-link" @click="aiBaseUrl = 'https://dashscope.aliyuncs.com/compatible-mode/v1'">通义千问</button>
            <button type="button" class="hint-link" @click="aiBaseUrl = 'https://api.moonshot.cn/v1'">Moonshot</button>
          </div>

          <!-- Model name -->
          <div class="form-row" style="margin-top:14px">
            <div class="form-field" style="flex:1">
              <label class="form-label-sm">模型名称</label>
              <input
                v-model="aiModel"
                class="form-input"
                placeholder="如 gpt-4o、deepseek-chat、qwen-turbo"
              />
            </div>
          </div>
          <div class="url-hints">
            <span>常用模型：</span>
            <button type="button" class="hint-link" @click="aiModel = 'gpt-4o'">GPT-4o</button>
            <button type="button" class="hint-link" @click="aiModel = 'gpt-4o-mini'">GPT-4o Mini</button>
            <button type="button" class="hint-link" @click="aiModel = 'deepseek-chat'">DeepSeek V3</button>
            <button type="button" class="hint-link" @click="aiModel = 'deepseek-reasoner'">DeepSeek R1</button>
            <button type="button" class="hint-link" @click="aiModel = 'qwen-turbo'">通义千问 Turbo</button>
            <button type="button" class="hint-link" @click="aiModel = 'moonshot-v1-8k'">Moonshot</button>
          </div>

          <!-- Actions -->
          <div class="form-actions" style="margin-top:16px">
            <Button :disabled="aiSaving" @click="saveAiConfig">
              {{ aiSaving ? '保存中...' : '保存 AI 配置' }}
            </Button>
          </div>

          <!-- Status messages -->
          <div v-if="aiError" class="result-box result-box--error" style="margin-top:12px">
            {{ aiError }}
          </div>
          <div v-if="aiSuccess" class="result-box result-box--success" style="margin-top:12px">
            {{ aiSuccess }}
          </div>
        </template>
      </div>

      <!-- User Management Card -->
      <UserManagementCard v-if="isAdmin" />

      <!-- LIS Configuration Card -->
      <div class="card">
        <h2 class="card-title">{{ t('settings.lisTitle') }}</h2>
        <p class="card-desc">{{ t('settings.lisDesc') }}</p>

        <div v-if="lisLoading" class="loading-text">{{ t('settings.loading') }}</div>
        <template v-else>
          <!-- Enable toggle -->
          <div class="form-row">
            <label class="form-label">{{ t('settings.lisEnable') }}</label>
            <label class="toggle">
              <input type="checkbox" v-model="lisEnabled" />
              <span class="toggle-slider"></span>
            </label>
          </div>

          <!-- Status -->
          <div class="form-row" v-if="lisEnabled || lisStatus !== 'stopped'">
            <label class="form-label">{{ t('settings.lisStatus') }}</label>
            <StatusBadge :status="statusBadge" :label="lisStatus" />
            <span v-if="lisError" class="error-inline">{{ lisError }}</span>
          </div>

          <!-- Host & Port -->
          <div class="form-row form-row--dual">
            <div class="form-field">
              <label class="form-label-sm">{{ t('settings.lisHost') }}</label>
              <input v-model="lisHost" class="form-input" :disabled="!lisEnabled" />
            </div>
            <div class="form-field">
              <label class="form-label-sm">{{ t('settings.lisPort') }}</label>
              <input v-model.number="lisPort" type="number" class="form-input" :disabled="!lisEnabled" />
            </div>
          </div>

          <!-- Actions -->
          <div class="form-actions">
            <Button :disabled="lisSaving" @click="saveLisConfig">
              {{ lisSaving ? t('settings.saving') : t('settings.lisSave') }}
            </Button>
            <Button variant="outline" :disabled="lisStatus !== 'running'" @click="handleRestart">
              {{ t('settings.lisRestart') }}
            </Button>
          </div>

          <!-- Test Parse -->
          <div class="section-divider"></div>
          <h3 class="section-subtitle">{{ t('settings.lisTestParse') }}</h3>
          <p class="card-desc">{{ t('settings.lisTestParseDesc') }}</p>

          <textarea
            v-model="testHl7Input"
            class="form-textarea"
            rows="5"
            :placeholder="t('settings.lisTestParsePlaceholder')"
          ></textarea>
          <Button variant="outline" class="mt-2" @click="handleTestParse">
            {{ t('settings.lisTestParseBtn') }}
          </Button>

          <div v-if="testParseResult" class="result-box result-box--success">
            <p><strong>{{ t('settings.lisParseType') }}:</strong> {{ testParseResult.message_type }}</p>
            <p><strong>{{ t('settings.lisParsePatient') }}:</strong> {{ testParseResult.patient_id }} {{ testParseResult.patient_name }}</p>
            <p><strong>{{ t('settings.lisParseTest') }}:</strong> {{ testParseResult.test_code }} {{ testParseResult.test_name }}</p>
            <p><strong>{{ t('settings.lisParseResults') }}:</strong></p>
            <ul>
              <li v-for="r in testParseResult.results" :key="r.set_id">
                {{ r.code }} {{ r.name }} = {{ r.value }} {{ r.unit }}
                <span v-if="r.ref_range">({{ r.ref_range }})</span>
                <span v-if="r.abnormal" class="abnormal-flag">[{{ r.abnormal }}]</span>
              </li>
            </ul>
          </div>
          <div v-if="testParseError" class="result-box result-box--error">
            {{ testParseError }}
          </div>

          <!-- Recent messages -->
          <template v-if="lisMessages.length">
            <div class="section-divider"></div>
            <h3 class="section-subtitle">{{ t('settings.lisRecent') }}</h3>
            <div class="msg-list">
              <div v-for="m in lisMessages" :key="m.id" class="msg-item">
                <span class="msg-time">{{ m.timestamp?.slice(11,19) || '--' }}</span>
                <span class="msg-type">{{ m.message_type }}</span>
                <span class="msg-patient">{{ m.patient_id || '--' }}</span>
                <span class="msg-test">{{ m.test_name || m.test_code || '--' }}</span>
              </div>
            </div>
          </template>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings-page {
  padding: 0 28px 28px;
  overflow-y: auto;
  height: 100%;
}
.cards {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 680px;
}
.card {
  background: var(--bg-surface-1);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  padding: 24px;
}
.card-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 4px;
  color: var(--text-primary);
}
.card-desc {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0 0 16px;
}
.section-subtitle {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 4px;
  color: var(--text-primary);
}
.section-divider {
  border-top: 1px solid var(--border-subtle);
  margin: 20px 0;
}
.form-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}
.form-row--dual {
  display: flex;
  gap: 16px;
}
.form-field {
  flex: 1;
}
.form-label {
  font-size: 13px;
  color: var(--text-secondary);
  min-width: 80px;
}
.form-label-sm {
  font-size: 12px;
  color: var(--text-muted);
  display: block;
  margin-bottom: 4px;
}
.form-input {
  height: 34px;
  padding: 0 10px;
  border-radius: 6px;
  border: 1px solid var(--border-subtle);
  background: var(--bg-surface-2);
  color: var(--text-primary);
  font-size: 13px;
  font-family: monospace;
  width: 100%;
  box-sizing: border-box;
}
.form-input:disabled {
  opacity: 0.45;
}
.form-textarea {
  width: 100%;
  padding: 10px;
  border-radius: 6px;
  border: 1px solid var(--border-subtle);
  background: var(--bg-surface-2);
  color: var(--text-primary);
  font-size: 12px;
  font-family: monospace;
  box-sizing: border-box;
  resize: vertical;
}
.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 4px;
}
.error-inline {
  font-size: 12px;
  color: var(--color-danger);
}
.loading-text {
  font-size: 13px;
  color: var(--text-muted);
}
.mt-2 {
  margin-top: 8px;
}

/* ── AI config helpers ─────────────────────── */

.input-with-icon {
  position: relative;
  display: flex;
  align-items: center;
}
.input-with-icon .form-input {
  padding-right: 36px;
}
.toggle-vis {
  position: absolute;
  right: 6px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  padding: 2px 4px;
  line-height: 1;
  color: var(--text-muted);
  opacity: 0.7;
}
.toggle-vis:hover {
  opacity: 1;
}
.url-hints {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
}
.hint-link {
  background: none;
  border: 1px solid var(--border-subtle);
  border-radius: 4px;
  padding: 2px 8px;
  font-size: 12px;
  cursor: pointer;
  color: var(--color-primary, #3b82f6);
  background: color-mix(in srgb, var(--color-primary, #3b82f6) 6%, transparent);
  transition: background 0.15s;
}
.hint-link:hover {
  background: color-mix(in srgb, var(--color-primary, #3b82f6) 14%, transparent);
}

/* Toggle */
.toggle {
  display: inline-block;
  position: relative;
  width: 44px;
  height: 24px;
}
.toggle input {
  opacity: 0;
  width: 0;
  height: 0;
}
.toggle-slider {
  position: absolute;
  cursor: pointer;
  inset: 0;
  background: var(--border-subtle);
  border-radius: 24px;
  transition: background 0.2s;
}
.toggle-slider::before {
  content: '';
  position: absolute;
  width: 18px;
  height: 18px;
  left: 3px;
  top: 3px;
  background: white;
  border-radius: 50%;
  transition: transform 0.2s;
}
.toggle input:checked + .toggle-slider {
  background: var(--color-success, #22c55e);
}
.toggle input:checked + .toggle-slider::before {
  transform: translateX(20px);
}

/* Result box */
.result-box {
  margin-top: 12px;
  padding: 14px;
  border-radius: 8px;
  font-size: 13px;
}
.result-box--success {
  background: color-mix(in srgb, var(--color-success, #22c55e) 8%, transparent);
  border: 1px solid color-mix(in srgb, var(--color-success, #22c55e) 18%, transparent);
  color: var(--text-primary);
}
.result-box--error {
  background: color-mix(in srgb, var(--color-danger) 8%, transparent);
  border: 1px solid color-mix(in srgb, var(--color-danger) 18%, transparent);
  color: var(--color-danger);
}
.result-box ul {
  margin: 4px 0 0 16px;
  padding: 0;
}
.result-box li {
  margin-bottom: 2px;
}
.abnormal-flag {
  color: var(--color-danger);
  font-weight: 600;
}

/* Message list */
.msg-list {
  margin-top: 10px;
}
.msg-item {
  display: flex;
  gap: 12px;
  padding: 6px 0;
  border-bottom: 1px solid var(--border-subtle);
  font-size: 12px;
}
.msg-time {
  color: var(--text-muted);
  font-family: monospace;
  min-width: 72px;
}
.msg-type {
  color: var(--color-warning, #f59e0b);
  font-weight: 500;
  min-width: 72px;
}
.msg-patient {
  color: var(--text-secondary);
  min-width: 60px;
}
.msg-test {
  color: var(--text-primary);
}
</style>
