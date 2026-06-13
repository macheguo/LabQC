<script setup>
import { ref, onMounted, computed } from 'vue'
import {
  FlaskConical, Plus, RefreshCw, BarChart3, Building2, Edit3,
  CheckCircle, AlertTriangle, FileSpreadsheet, Users, Beaker,
  Settings, Upload, Download, Send, ExternalLink
} from 'lucide-vue-next'
import * as api from '../api/eqaApi'

// ── State ──────────────────────────────────────────────────────────────
const role = ref('organizer')
const programs = ref([])
const institutions = ref([])
const loading = ref(false)
const msg = ref('')

const showSettings = ref(false)
const showInst = ref(false)
const showNewProgram = ref(false)

// Program detail
const expanded = ref(null)
const detailTab = ref('stats')
const detailData = ref(null)

// Forms
const newProg = ref({ name: '', program_type: '定量', start_date: '', end_date: '' })
const newInst = ref({ name: '', address: '', contact_name: '', contact_phone: '' })
const newSample = ref({ sample_code: '', item_name: '', unit: '', target_value: 0, target_sd: 0 })
const newPart = ref({ institution_id: '', lab_code: '' })
const newResult = ref({ participant_id: '', sample_id: '', reported_value: 0, method: '', instrument: '' })

// Settings
const settingsForm = ref({ role: 'organizer', org_name: '', portal_enabled: '否', portal_access: '', remote_api_url: '', api_key: '' })

// Import / Export
const importFile = ref(null)
const importResult = ref(null)
const exportInst = ref('')

// ── Lifecycle ──────────────────────────────────────────────────────────
onMounted(async () => {
  await loadSettings()
  await loadAll()
})

async function loadSettings() {
  try {
    const s = await api.fetchSettings()
    role.value = s.role
    settingsForm.value = { ...s }
  } catch (e) { /* ignore */ }
}

async function loadAll() {
  loading.value = true
  try {
    const [p, i] = await Promise.all([api.fetchPrograms(), api.fetchInstitutions()])
    programs.value = p
    institutions.value = i
  } catch (e) { msg.value = '加载失败: ' + e.message }
  finally { loading.value = false }
}

// ── Settings ───────────────────────────────────────────────────────────
async function saveSettings() {
  try {
    await api.updateSettings(settingsForm.value)
    role.value = settingsForm.value.role
    showSettings.value = false
    msg.value = '设置已保存'
  } catch (e) { msg.value = '保存失败' }
}

function toggleRole(r) {
  role.value = r
  settingsForm.value.role = r
}

// ── Programs ───────────────────────────────────────────────────────────
async function addProgram() {
  try {
    await api.createProgram(newProg.value)
    showNewProgram.value = false
    newProg.value = { name: '', program_type: '定量', start_date: '', end_date: '' }
    msg.value = '计划已创建'
    await loadAll()
  } catch (e) { msg.value = '创建失败: ' + e.message }
}

async function toggleDetail(progId) {
  if (expanded.value === progId) { expanded.value = null; return }
  expanded.value = progId
  detailTab.value = 'stats'
  const [samples, parts, results, stats] = await Promise.all([
    api.fetchSamples(progId), api.fetchParticipants(progId),
    api.fetchResults(progId), api.fetchStats(progId)
  ])
  detailData.value = { program_id: progId, samples, participants: parts, results, stats, ...stats }
}

// ── Samples / Participants / Results ───────────────────────────────────
async function addSample() {
  await api.createSample(expanded.value, newSample.value)
  newSample.value = { sample_code: '', item_name: '', unit: '', target_value: 0, target_sd: 0 }
  msg.value = '样品已添加'
  toggleDetail(expanded.value)
}

async function addParticipant() {
  await api.createParticipant(expanded.value, newPart.value)
  newPart.value = { institution_id: '', lab_code: '' }
  msg.value = '参评机构已添加'
  toggleDetail(expanded.value)
}

async function addResult() {
  await api.createResult(expanded.value, newResult.value)
  newResult.value = { participant_id: '', sample_id: '', reported_value: 0, method: '', instrument: '' }
  msg.value = '结果已提交'
  toggleDetail(expanded.value)
}

// ── Institutions ───────────────────────────────────────────────────────
async function saveInst() {
  await api.createInstitution(newInst.value)
  newInst.value = { name: '', address: '', contact_name: '', contact_phone: '' }
  institutions.value = await api.fetchInstitutions()
  msg.value = '机构已添加'
}
async function delInst(id) {
  await api.deleteInstitution(id)
  institutions.value = await api.fetchInstitutions()
}

// ── Import ─────────────────────────────────────────────────────────────
async function doImport() {
  if (!importFile.value) return
  try {
    const r = await api.importResults(expanded.value, importFile.value)
    importResult.value = r
    msg.value = `导入: ${r.imported} 条成功, ${r.skipped} 条跳过`
    importFile.value = null
    toggleDetail(expanded.value)
  } catch (e) { msg.value = '导入失败: ' + e.message }
}

// ── Export ─────────────────────────────────────────────────────────────
async function doExport() {
  if (!exportInst.value) { msg.value = '请选择参评机构'; return }
  const rows = await api.exportResults(expanded.value, exportInst.value)
  const csv = ['机构,样品,项目,回报值,靶值,SD,Z分数,评级,方法,仪器']
  rows.forEach(r => csv.push(`${exportInst.value},${r.sample_code},${r.item_name},${r.reported_value},${r.target_value},${r.target_sd},${r.z_score ?? ''},${r.grade ?? ''},${r.method ?? ''},${r.instrument ?? ''}`))
  const blob = new Blob(['\uFEFF' + csv.join('\n')], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = `eqa_${expanded.value}_${exportInst.value}.csv`; a.click()
  msg.value = `已导出 ${rows.length} 条`
}

// ── Helpers ────────────────────────────────────────────────────────────
function getInstName(pid) {
  const p = detailData.value?.participants?.find(x => x.id === pid)
  return p ? p.institution_name : pid
}
function getSampleCode(sid) {
  const s = detailData.value?.samples?.find(x => x.id === sid)
  return s ? s.sample_code : sid
}
function gradeClass(g) { return g === '满意' ? 'grade-ok' : g === '可疑' ? 'grade-warn' : 'grade-bad' }

const portalUrl = computed(() => {
  if (!settingsForm.value) return ''
  const access = settingsForm.value.portal_access || ''
  return `${window.location.origin}/labqc/eqa/portal/${expanded.value}?access=${access}`
})
</script>

<template>
<div class="eqa-page">

  <!-- ═══ HEADER ═══ -->
  <div class="eqa-header">
    <div class="eqa-title-row">
      <div class="eqa-title">
        <FlaskConical :size="22" />
        <h1>室间质评</h1>
        <span class="role-badge" :class="role">{{ role === 'organizer' ? '📡 组织者' : '🏥 参与者' }}</span>
        <span class="eqa-summary">{{ programs.length }} 计划 · {{ institutions.length }} 机构</span>
      </div>
      <div class="eqa-actions">
        <button class="btn-icon" @click="showSettings = true" title="EQA 设置"><Settings :size="18" /></button>
        <button class="btn-outline" @click="showInst = true"><Building2 :size="14" /> 机构管理</button>
        <button class="btn-primary" @click="showNewProgram = true"><Plus :size="16" /> 新建计划</button>
      </div>
    </div>
  </div>

  <div v-if="msg" class="eqa-toast" @click="msg = ''">{{ msg }}</div>

  <!-- ═══ PROGRAMS TABLE ═══ -->
  <div class="eqa-table-wrap">
    <table class="eqa-table">
      <thead>
        <tr>
          <th class="col-name">计划名称</th>
          <th class="col-type">类型</th>
          <th class="col-date">周期</th>
          <th class="col-num">样品</th>
          <th class="col-num">机构</th>
          <th class="col-stat">状态</th>
          <th class="col-op" v-if="role === 'organizer'">接收</th>
          <th class="col-op" v-if="role === 'participant'">操作</th>
          <th class="col-expand"></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in programs" :key="p.id" :class="{ expanded: expanded === p.id }" @click="toggleDetail(p.id)">
          <td class="col-name"><span class="prog-name">{{ p.name }}</span></td>
          <td class="col-type">{{ p.program_type }}</td>
          <td class="col-date">{{ p.start_date || '—' }} ~ {{ p.end_date || '—' }}</td>
          <td class="col-num">{{ detailData?.program_id === p.id ? detailData.samples?.length || '—' : '—' }}</td>
          <td class="col-num">{{ detailData?.program_id === p.id ? detailData.participants?.length || '—' : '—' }}</td>
          <td class="col-stat"><span class="status-tag" :class="p.status === '进行中' ? 'active' : 'done'">{{ p.status }}</span></td>
          <td class="col-op" v-if="role === 'organizer'" @click.stop>
            <button class="btn-sm" @click="expanded = p.id"><Upload :size="12" /> 导入</button>
          </td>
          <td class="col-op" v-if="role === 'participant'" @click.stop>
            <button class="btn-sm" @click="expanded = p.id"><Send :size="12" /> 提交</button>
          </td>
          <td class="col-expand"><span class="expand-arrow">{{ expanded === p.id ? '▼' : '▶' }}</span></td>
        </tr>
      </tbody>
    </table>
    <div v-if="programs.length === 0" class="empty">暂无室间质评计划</div>
  </div>

  <!-- ═══ EXPANDED DETAIL ═══ -->
  <div v-if="expanded && detailData" class="detail-panel">
    <div class="detail-head">
      <span class="detail-title">{{ detailData.stats?.program?.name || '计划详情' }}</span>
      <span class="detail-summary">
        <Beaker :size="14" /> 样品 {{ detailData.samples?.length || 0 }}
        <Users :size="14" /> 机构 {{ detailData.participants?.length || 0 }}
        <FileSpreadsheet :size="14" /> 结果 {{ detailData.results?.length || 0 }}
        <BarChart3 :size="14" /> 统计 {{ detailData.stats?.institution_summary?.length || 0 }} 机构
      </span>
    </div>

    <!-- Tabs -->
    <div class="detail-tabs">
      <button :class="{ active: detailTab === 'stats' }" @click="detailTab = 'stats'">📊 样品统计</button>
      <button :class="{ active: detailTab === 'participants' }" @click="detailTab = 'participants'">🏥 参评机构</button>
      <button :class="{ active: detailTab === 'results' }" @click="detailTab = 'results'">📝 检测结果</button>
      <button v-if="role === 'organizer'" :class="{ active: detailTab === 'import' }" @click="detailTab = 'import'">📥 导入</button>
      <button v-if="role === 'participant'" :class="{ active: detailTab === 'export' }" @click="detailTab = 'export'">📤 导出</button>
      <div class="tab-right">
        <button class="btn-sm" @click="expanded = null">收起 ✕</button>
      </div>
    </div>

    <!-- Tab: Stats -->
    <div v-if="detailTab === 'stats'" class="tab-body">
      <div v-for="s in detailData.stats?.sample_stats" :key="s.sample_id" class="sample-card">
        <div class="sample-head">
          <strong>{{ s.sample_code }}</strong> {{ s.item_name }}
          <span class="target">靶值 {{ s.target_value }}±{{ s.target_sd }}</span>
          <span class="sample-stat">N={{ s.n }} 均值={{ s.mean }} SD={{ s.sd }} CV={{ s.cv }}%</span>
        </div>
        <table class="sub-table">
          <thead>
            <tr><th>参评机构</th><th>回报值</th><th>Z-分数</th><th>评级</th><th>方法</th><th>仪器</th></tr>
          </thead>
          <tbody>
            <tr v-for="r in s.results" :key="r.id">
              <td>{{ r.institution_name }}</td>
              <td>{{ r.reported_value }}</td>
              <td :class="{ 'z-warn': Math.abs(r.z_score || 0) > 2, 'z-bad': Math.abs(r.z_score || 0) >= 3 }">{{ r.z_score }}</td>
              <td><span class="grade-tag" :class="gradeClass(r.grade)">{{ r.grade }}</span></td>
              <td>{{ r.method || '—' }}</td>
              <td>{{ r.instrument || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Summary -->
      <h4>各机构统计</h4>
      <table class="sub-table">
        <thead>
          <tr><th>参评机构</th><th>总项</th><th>满意</th><th>可疑</th><th>不满意</th><th>满意率</th></tr>
        </thead>
        <tbody>
          <tr v-for="s in detailData.stats?.institution_summary" :key="s.institution_name">
            <td>{{ s.institution_name }}</td>
            <td>{{ s.total }}</td>
            <td>{{ s.satisfactory }}</td>
            <td>{{ s.questionable }}</td>
            <td>{{ s.unsatisfactory }}</td>
            <td :class="s.pass_rate === 100 ? 'pass-full' : s.pass_rate >= 80 ? 'pass-ok' : 'pass-bad'">{{ s.pass_rate }}%</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Tab: Participants -->
    <div v-if="detailTab === 'participants'" class="tab-body">
      <table class="sub-table">
        <thead><tr><th>参评机构</th><th>实验室编号</th><th>状态</th></tr></thead>
        <tbody>
          <tr v-for="p in detailData.participants" :key="p.id">
            <td>{{ p.institution_name }}</td>
            <td>{{ p.lab_code || '—' }}</td>
            <td>{{ p.status }}</td>
          </tr>
        </tbody>
      </table>
      <h4>添加参评机构</h4>
      <div class="inline-form">
        <select v-model="newPart.institution_id">
          <option value="">— 选择机构 —</option>
          <option v-for="i in institutions" :key="i.id" :value="i.id">{{ i.name }}</option>
        </select>
        <input v-model="newPart.lab_code" placeholder="实验室编号（可选）" />
        <button class="btn-primary btn-sm" @click="addParticipant">添加</button>
      </div>
    </div>

    <!-- Tab: Results -->
    <div v-if="detailTab === 'results'" class="tab-body">
      <table class="sub-table">
        <thead>
          <tr><th>机构</th><th>样品</th><th>回报值</th><th>Z</th><th>评级</th><th>方法</th><th>仪器</th></tr>
        </thead>
        <tbody>
          <tr v-for="r in detailData.results" :key="r.id">
            <td>{{ r.institution_name }}</td>
            <td>{{ getSampleCode(r.sample_id) }}</td>
            <td>{{ r.reported_value }}</td>
            <td :class="{ 'z-warn': Math.abs(r.z_score || 0) > 2, 'z-bad': Math.abs(r.z_score || 0) >= 3 }">{{ r.z_score }}</td>
            <td><span class="grade-tag" :class="gradeClass(r.grade)">{{ r.grade || '—' }}</span></td>
            <td>{{ r.method || '—' }}</td>
            <td>{{ r.instrument || '—' }}</td>
          </tr>
        </tbody>
      </table>
      <h4>录入检测结果</h4>
      <div class="inline-form">
        <select v-model="newResult.participant_id">
          <option value="">— 参评机构 —</option>
          <option v-for="p in detailData.participants" :key="p.id" :value="p.id">{{ p.institution_name }}</option>
        </select>
        <select v-model="newResult.sample_id">
          <option value="">— 质评样品 —</option>
          <option v-for="s in detailData.samples" :key="s.id" :value="s.id">{{ s.sample_code }} {{ s.item_name }}</option>
        </select>
        <input v-model.number="newResult.reported_value" type="number" step="any" placeholder="回报值" />
        <input v-model="newResult.method" placeholder="方法" />
        <input v-model="newResult.instrument" placeholder="仪器" />
        <button class="btn-primary btn-sm" @click="addResult">录入</button>
      </div>
    </div>

    <!-- Tab: Import (organizer only) -->
    <div v-if="detailTab === 'import' && role === 'organizer' && settingsForm" class="tab-body">
      <h4>CSV 批量导入结果</h4>
      <p class="text-muted">CSV 列: institution_name, sample_code, reported_value, method, instrument<br>（支持中文列名：机构名称, 样品编号, 回报值, 方法, 仪器）</p>
      <div class="import-box">
        <input type="file" accept=".csv" @change="e => importFile = e.target.files[0]" />
        <button class="btn-primary btn-sm" :disabled="!importFile" @click="doImport">📥 导入</button>
      </div>
      <div v-if="importResult" class="import-result">
        ✅ 导入 {{ importResult.imported }} / 跳过 {{ importResult.skipped }}
        <div v-if="importResult.errors?.length" class="import-errors">
          <div v-for="(e, i) in importResult.errors" :key="i">⚠ {{ e }}</div>
        </div>
      </div>

      <h4 style="margin-top: 24px">参评门户</h4>
      <p class="text-muted">参评机构可访问此链接自主填报结果</p>
      <div class="portal-box">
        <code>{{ portalUrl }}</code>
        <div class="portal-info">
          访问码: <strong>{{ (settingsForm && settingsForm.portal_access) || '（未设置）' }}</strong> &nbsp;|&nbsp;
          状态: <span :class="(settingsForm && settingsForm.portal_enabled === '是') ? 'on' : 'off'">{{ (settingsForm && settingsForm.portal_enabled === '是') ? '✅ 已启用' : '❌ 未启用' }}</span>
        </div>
        <p class="text-muted" style="margin-top: 8px">启用/设置访问码：请点击右上角 ⚙ 设置</p>
      </div>
    </div>

    <!-- Tab: Export (participant only) -->
    <div v-if="detailTab === 'export' && role === 'participant'" class="tab-body">
      <h4>导出检测结果</h4>
      <div class="import-box">
        <select v-model="exportInst">
          <option value="">— 选择本机构 —</option>
          <option v-for="i in institutions" :key="i.id" :value="i.name">{{ i.name }}</option>
        </select>
        <button class="btn-primary btn-sm" :disabled="!exportInst" @click="doExport">📤 导出 CSV</button>
      </div>

      <h4 style="margin-top: 24px">远程提交</h4>
      <p class="text-muted">将结果提交至远端组织者 API</p>
      <div class="import-box">
        <input :value="settingsForm.remote_api_url" disabled placeholder="请在设置中配置远程API地址" />
        <button class="btn-outline btn-sm" :disabled="!settingsForm.remote_api_url">📡 提交全部</button>
      </div>
      <p class="text-muted" style="margin-top: 8px">配置远程地址：请点击右上角 ⚙ 设置</p>
    </div>
  </div>

  <!-- ═══ MODAL: New Program ═══ -->
  <div v-if="showNewProgram" class="modal-overlay" @click.self="showNewProgram = false">
    <div class="modal">
      <h3>新建室间质评计划</h3>
      <label>计划名称 <input v-model="newProg.name" placeholder="如：2026年第一次室间质评（生化）" /></label>
      <label>类型
        <select v-model="newProg.program_type">
          <option>定量</option><option>定性</option>
        </select>
      </label>
      <label>开始日期 <input v-model="newProg.start_date" type="date" /></label>
      <label>结束日期 <input v-model="newProg.end_date" type="date" /></label>
      <div class="modal-btns">
        <button class="btn-outline" @click="showNewProgram = false">取消</button>
        <button class="btn-primary" @click="addProgram">创建</button>
      </div>
    </div>
  </div>

  <!-- ═══ MODAL: Settings ═══ -->
  <div v-if="showSettings" class="modal-overlay" @click.self="showSettings = false">
    <div class="modal">
      <h3>⚙ EQA 设置</h3>

      <label>软件角色</label>
      <div class="role-toggle">
        <button :class="{ active: settingsForm.role === 'organizer' }" @click="toggleRole('organizer')">📡 组织者（接收端）</button>
        <button :class="{ active: settingsForm.role === 'participant' }" @click="toggleRole('participant')">🏥 参与者（发送端）</button>
      </div>

      <template v-if="settingsForm.role === 'organizer'">
        <label>组织名称 <input v-model="settingsForm.org_name" placeholder="如：省临检中心" /></label>
        <label>参评门户
          <select v-model="settingsForm.portal_enabled">
            <option value="否">关闭</option>
            <option value="是">启用</option>
          </select>
        </label>
        <label>访问码 <input v-model="settingsForm.portal_access" placeholder="参评机构访问口令" /></label>
      </template>

      <template v-if="settingsForm.role === 'participant'">
        <label>远端 API 地址 <input v-model="settingsForm.remote_api_url" placeholder="http://org.example.com/api/eqa" /></label>
        <label>API Key <input v-model="settingsForm.api_key" placeholder="远端认证密钥" /></label>
      </template>

      <div class="modal-btns">
        <button class="btn-outline" @click="showSettings = false">取消</button>
        <button class="btn-primary" @click="saveSettings">保存设置</button>
      </div>
    </div>
  </div>

  <!-- ═══ MODAL: Institution Management ═══ -->
  <div v-if="showInst" class="modal-overlay" @click.self="showInst = false">
    <div class="modal wide">
      <h3>🏥 机构管理</h3>
      <table class="sub-table">
        <thead><tr><th>机构名称</th><th>地址</th><th>联系人</th><th>电话</th><th></th></tr></thead>
        <tbody>
          <tr v-for="i in institutions" :key="i.id">
            <td>{{ i.name }}</td><td>{{ i.address || '—' }}</td><td>{{ i.contact_name || '—' }}</td><td>{{ i.contact_phone || '—' }}</td>
            <td><button class="btn-sm btn-danger" @click="delInst(i.id)">删除</button></td>
          </tr>
        </tbody>
      </table>
      <h4 style="margin-top: 16px">新增机构</h4>
      <div class="inline-form">
        <input v-model="newInst.name" placeholder="机构名称 *" />
        <input v-model="newInst.address" placeholder="地址" />
        <input v-model="newInst.contact_name" placeholder="联系人" />
        <input v-model="newInst.contact_phone" placeholder="电话" />
        <button class="btn-primary btn-sm" @click="saveInst" :disabled="!newInst.name">添加</button>
      </div>
      <div class="modal-btns"><button class="btn-outline" @click="showInst = false">关闭</button></div>
    </div>
  </div>
</div>
</template>

<style scoped>
.eqa-page { max-width: 1100px; margin: 0 auto; padding: 24px; }

/* ── Header ──────────────────────────────────────────────────────────── */
.eqa-header { margin-bottom: 16px; }
.eqa-title-row { display: flex; align-items: center; justify-content: space-between; }
.eqa-title { display: flex; align-items: center; gap: 10px; }
.eqa-title h1 { font-size: 20px; font-weight: 700; margin: 0; }
.role-badge { font-size: 12px; padding: 2px 10px; border-radius: 12px; font-weight: 600; }
.role-badge.organizer { background: #dbeafe; color: #1d4ed8; }
.role-badge.participant { background: #dcfce7; color: #15803d; }
.eqa-summary { color: #888; font-size: 13px; margin-left: 8px; }
.eqa-actions { display: flex; gap: 8px; }

/* ── Buttons ─────────────────────────────────────────────────────────── */
.btn-primary { background: #2563eb; color: #fff; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; display: inline-flex; align-items: center; gap: 4px; }
.btn-primary:hover { background: #1d4ed8; }
.btn-outline { background: #fff; color: #555; border: 1px solid #d1d5db; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; display: inline-flex; align-items: center; gap: 4px; }
.btn-outline:hover { background: #f9fafb; }
.btn-icon { background: none; border: 1px solid #e5e7eb; padding: 8px; border-radius: 6px; cursor: pointer; color: #555; }
.btn-icon:hover { background: #f3f4f6; }
.btn-sm { background: #f3f4f6; border: 1px solid #d1d5db; padding: 4px 10px; border-radius: 4px; cursor: pointer; font-size: 12px; display: inline-flex; align-items: center; gap: 3px; }
.btn-sm:hover { background: #e5e7eb; }
.btn-danger { color: #dc2626; }
.btn-primary:disabled, .btn-sm:disabled { opacity: 0.5; cursor: not-allowed; }

/* ── Table ───────────────────────────────────────────────────────────── */
.eqa-table-wrap { background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden; }
.eqa-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.eqa-table th { background: #f9fafb; padding: 10px 12px; text-align: left; font-weight: 600; color: #555; border-bottom: 1px solid #e5e7eb; }
.eqa-table td { padding: 10px 12px; border-bottom: 1px solid #f3f4f6; cursor: pointer; }
.eqa-table tr:hover { background: #fafbff; }
.eqa-table tr.expanded { background: #f0f4ff; }
.col-name { width: 35%; } .col-type { width: 8%; } .col-date { width: 18%; }
.col-num { width: 7%; text-align: center; } .col-stat { width: 8%; } .col-op { width: 9%; } .col-expand { width: 4%; text-align: center; }
.prog-name { font-weight: 600; color: #1f2937; }
.expand-arrow { color: #9ca3af; font-size: 10px; }
.status-tag { font-size: 11px; padding: 2px 8px; border-radius: 8px; }
.status-tag.active { background: #dcfce7; color: #15803d; }
.status-tag.done { background: #f3f4f6; color: #6b7280; }
.empty { padding: 40px; text-align: center; color: #999; }

/* ── Detail Panel ────────────────────────────────────────────────────── */
.detail-panel { margin-top: 4px; background: #fff; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 8px 8px; }
.detail-head { padding: 12px 16px; border-bottom: 1px solid #f3f4f6; display: flex; align-items: center; gap: 16px; }
.detail-title { font-weight: 700; font-size: 15px; }
.detail-summary { color: #888; font-size: 12px; display: flex; gap: 12px; align-items: center; }
.detail-tabs { display: flex; gap: 2px; padding: 8px 16px; border-bottom: 1px solid #e5e7eb; background: #fafafa; }
.detail-tabs button { background: none; border: none; padding: 6px 14px; font-size: 13px; cursor: pointer; border-radius: 4px; color: #555; }
.detail-tabs button:hover { background: #e5e7eb; }
.detail-tabs button.active { background: #fff; color: #2563eb; font-weight: 600; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.tab-right { margin-left: auto; }
.tab-body { padding: 16px; }

/* ── Sample Card ─────────────────────────────────────────────────────── */
.sample-card { margin-bottom: 16px; border: 1px solid #e5e7eb; border-radius: 6px; overflow: hidden; }
.sample-head { padding: 10px 14px; background: #f9fafb; display: flex; align-items: center; gap: 12px; font-size: 13px; }
.sample-head strong { font-size: 14px; }
.target { color: #2563eb; font-weight: 600; margin-left: 4px; }
.sample-stat { color: #888; margin-left: auto; font-size: 12px; }

/* ── Sub Table ───────────────────────────────────────────────────────── */
.sub-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.sub-table th { background: #f9fafb; padding: 8px 12px; text-align: left; font-weight: 600; color: #666; border-bottom: 1px solid #e5e7eb; }
.sub-table td { padding: 8px 12px; border-bottom: 1px solid #f3f4f6; }
.sub-table tr:hover { background: #fafbff; }

/* ── Grade tags ──────────────────────────────────────────────────────── */
.grade-tag { font-size: 11px; padding: 2px 8px; border-radius: 8px; font-weight: 600; }
.grade-ok { background: #dcfce7; color: #15803d; }
.grade-warn { background: #fef3c7; color: #b45309; }
.grade-bad { background: #fecaca; color: #dc2626; }
.z-warn { color: #d97706; font-weight: 700; }
.z-bad { color: #dc2626; font-weight: 700; }
.pass-full { color: #15803d; font-weight: 700; }
.pass-ok { color: #2563eb; }
.pass-bad { color: #dc2626; font-weight: 700; }

/* ── Forms ───────────────────────────────────────────────────────────── */
.inline-form { display: flex; gap: 8px; margin-top: 12px; align-items: center; flex-wrap: wrap; }
.inline-form input, .inline-form select { padding: 6px 10px; border: 1px solid #d1d5db; border-radius: 4px; font-size: 13px; }
.inline-form input[type="number"] { width: 90px; }

/* ── Modals ──────────────────────────────────────────────────────────── */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { background: #fff; padding: 24px; border-radius: 10px; min-width: 380px; max-width: 560px; box-shadow: 0 10px 40px rgba(0,0,0,0.15); }
.modal.wide { max-width: 720px; }
.modal h3 { margin: 0 0 16px; font-size: 16px; }
.modal label { display: block; font-size: 13px; color: #555; margin-bottom: 10px; }
.modal label input, .modal label select { display: block; width: 100%; margin-top: 4px; padding: 7px 10px; border: 1px solid #d1d5db; border-radius: 4px; font-size: 13px; box-sizing: border-box; }
.modal-btns { display: flex; gap: 8px; justify-content: flex-end; margin-top: 16px; }

/* ── Role Toggle ─────────────────────────────────────────────────────── */
.role-toggle { display: flex; gap: 6px; margin-bottom: 14px; }
.role-toggle button { flex: 1; padding: 8px; border: 1px solid #d1d5db; border-radius: 6px; background: #fff; cursor: pointer; font-size: 13px; }
.role-toggle button.active { background: #2563eb; color: #fff; border-color: #2563eb; }

/* ── Import / Export / Portal ────────────────────────────────────────── */
.import-box { display: flex; gap: 8px; align-items: center; margin-top: 8px; }
.import-box select, .import-box input { padding: 6px 10px; border: 1px solid #d1d5db; border-radius: 4px; font-size: 13px; }
.import-result { margin-top: 12px; padding: 10px; background: #f0fdf4; border-radius: 6px; font-size: 13px; }
.import-errors { margin-top: 8px; color: #dc2626; font-size: 12px; }
.portal-box { margin-top: 8px; padding: 12px; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 6px; }
.portal-box code { font-size: 12px; word-break: break-all; display: block; margin-bottom: 8px; }
.portal-info { font-size: 12px; color: #666; }
.portal-info .on { color: #15803d; } .portal-info .off { color: #dc2626; }
.text-muted { color: #888; font-size: 12px; margin: 4px 0; }

h4 { font-size: 14px; font-weight: 600; margin: 16px 0 8px; color: #374151; }

/* ── Toast ───────────────────────────────────────────────────────────── */
.eqa-toast { position: fixed; top: 16px; right: 16px; padding: 10px 18px; background: #1f2937; color: #fff; border-radius: 8px; font-size: 13px; z-index: 200; cursor: pointer; }
</style>
