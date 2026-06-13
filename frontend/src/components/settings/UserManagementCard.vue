<template>
  <div class="card">
    <h2 class="card-title">用户管理</h2>
    <p class="card-desc">管理系统登录用户。仅管理员可见。</p>

    <!-- Add user form -->
    <div v-if="showAddForm" class="add-form">
      <h4>添加用户</h4>
      <div class="form-row">
        <input v-model="newUser.username" class="form-input" placeholder="用户名" style="width:140px"/>
        <input v-model="newUser.password" type="password" class="form-input" placeholder="密码" style="width:140px"/>
        <input v-model="newUser.display_name" class="form-input" placeholder="显示名称（可选）" style="width:160px"/>
        <label class="checkbox-label">
          <input type="checkbox" v-model="newUser.is_admin"/> 管理员
        </label>
        <button class="btn-sm btn-primary" @click="handleAdd" :disabled="!newUser.username||!newUser.password">添加</button>
        <button class="btn-sm btn-outline" @click="showAddForm=false">取消</button>
      </div>
    </div>

    <button v-else class="btn-sm btn-primary" @click="showAddForm=true" style="margin-bottom:12px">+ 添加用户</button>

    <!-- User list table -->
    <table v-if="users.length" class="user-table">
      <thead>
        <tr>
          <th>用户名</th>
          <th>显示名</th>
          <th>角色</th>
          <th>状态</th>
          <th>最后登录</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="u in users" :key="u.username" :class="{ inactive: !u.is_active }">
          <td><strong>{{ u.username }}</strong></td>
          <td>
            <template v-if="editing === u.username">
              <input v-model="editForm.display_name" class="table-input" style="width:100px"/>
            </template>
            <template v-else>{{ u.display_name || '-' }}</template>
          </td>
          <td>
            <template v-if="editing === u.username">
              <label class="checkbox-label">
                <input type="checkbox" v-model="editForm.is_admin"/> 管理员
              </label>
            </template>
            <template v-else>{{ u.is_admin ? '管理员' : '普通用户' }}</template>
          </td>
          <td>
            <span :class="u.is_active ? 'badge-active' : 'badge-inactive'">{{ u.is_active ? '启用' : '禁用' }}</span>
          </td>
          <td class="time-cell">{{ u.last_login ? u.last_login.slice(0,16).replace('T',' ') : '-' }}</td>
          <td>
            <template v-if="editing === u.username">
              <button class="btn-xs btn-primary" @click="handleSave(u.username)">保存</button>
              <button class="btn-xs btn-outline" @click="editing=''">取消</button>
            </template>
            <template v-else>
              <button class="btn-xs btn-outline" @click="startEdit(u)">编辑</button>
              <button v-if="u.username !== currentUser" class="btn-xs btn-outline" @click="handleResetPwd(u.username)">重置密码</button>
              <button v-if="u.username !== currentUser" class="btn-xs btn-danger" @click="handleDelete(u.username)">删除</button>
            </template>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-else-if="!loading" class="empty-state">暂无用户</div>
    <div v-if="loading" class="loading-text">加载中...</div>
    <div v-if="error" class="error-msg">{{ error }}</div>
    <div v-if="success" class="success-msg">{{ success }}</div>

    <!-- Reset password modal -->
    <div v-if="resetPwdUser" class="modal-overlay" @click.self="resetPwdUser=''">
      <div class="modal-box">
        <h4>重置 {{ resetPwdUser }} 密码</h4>
        <input v-model="newPassword" type="password" class="form-input" placeholder="新密码" style="width:100%;margin:8px 0"/>
        <div class="form-row" style="justify-content:flex-end;gap:8px">
          <button class="btn-sm btn-outline" @click="resetPwdUser=''; newPassword=''">取消</button>
          <button class="btn-sm btn-primary" :disabled="!newPassword" @click="doResetPwd">确认重置</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const currentUser = ref('')
const users = ref([])
const loading = ref(false)
const error = ref('')
const success = ref('')
const showAddForm = ref(false)
const editing = ref('')
const resetPwdUser = ref('')
const newPassword = ref('')

const newUser = ref({ username: '', password: '', display_name: '', is_admin: false })
const editForm = ref({ display_name: '', is_admin: false })

const token = () => localStorage.getItem('labqc_token') || ''
const api = (path, opts = {}) => {
  const sep = path.includes('?') ? '&' : '?'
  return fetch(`/labqc/auth${path}${sep}token=${encodeURIComponent(token())}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  }).then(r => {
    if (!r.ok) return r.json().then(d => Promise.reject(d.detail || '请求失败'))
    return r.json().catch(() => ({}))
  })
}

async function loadUsers() {
  loading.value = true
  try {
    users.value = await api('/users')
    currentUser.value = JSON.parse(localStorage.getItem('labqc_user') || '{}').username || ''
  } catch (e) {
    error.value = typeof e === 'string' ? e : e.message
  } finally {
    loading.value = false
  }
}

async function handleAdd() {
  error.value = ''; success.value = ''
  try {
    await api('/users', { method: 'POST', body: JSON.stringify(newUser.value) })
    success.value = `用户 ${newUser.value.username} 已创建`
    showAddForm.value = false
    newUser.value = { username: '', password: '', display_name: '', is_admin: false }
    await loadUsers()
    setTimeout(() => success.value = '', 3000)
  } catch (e) { error.value = typeof e === 'string' ? e : e.message }
}

function startEdit(u) {
  editing.value = u.username
  editForm.value = { display_name: u.display_name || '', is_admin: u.is_admin }
}

async function handleSave(username) {
  error.value = ''; success.value = ''
  try {
    await api(`/users/${encodeURIComponent(username)}`, { method: 'PUT', body: JSON.stringify(editForm.value) })
    editing.value = ''
    await loadUsers()
    success.value = '已保存'
    setTimeout(() => success.value = '', 3000)
  } catch (e) { error.value = typeof e === 'string' ? e : e.message }
}

async function handleDelete(username) {
  if (!confirm(`确定删除用户 ${username}？此操作不可撤销。`)) return
  error.value = ''; success.value = ''
  try {
    await api(`/users/${encodeURIComponent(username)}`, { method: 'DELETE' })
    success.value = `用户 ${username} 已删除`
    await loadUsers()
    setTimeout(() => success.value = '', 3000)
  } catch (e) { error.value = typeof e === 'string' ? e : e.message }
}

async function handleResetPwd(username) {
  resetPwdUser.value = username
  newPassword.value = ''
}

async function doResetPwd() {
  error.value = ''; success.value = ''
  try {
    await api(`/users/${encodeURIComponent(resetPwdUser.value)}/reset-password`, {
      method: 'POST', body: JSON.stringify({ new_password: newPassword.value }),
    })
    success.value = `${resetPwdUser.value} 密码已重置`
    resetPwdUser.value = ''
    newPassword.value = ''
    setTimeout(() => success.value = '', 3000)
  } catch (e) { error.value = typeof e === 'string' ? e : e.message }
}

onMounted(loadUsers)
</script>

<style scoped>
.card { background: var(--bg-surface-1); border: 1px solid var(--border-subtle); border-radius: 10px; padding: 24px; }
.card-title { font-size: 16px; font-weight: 600; margin: 0 0 4px; color: var(--text-primary); }
.card-desc { font-size: 13px; color: var(--text-muted); margin: 0 0 16px; }

.add-form { background: var(--bg-surface-2); border-radius: 8px; padding: 14px; margin-bottom: 14px; }
.add-form h4 { margin: 0 0 10px; font-size: 13px; color: var(--text-secondary); }

.form-row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.form-input { height: 32px; padding: 0 10px; border-radius: 6px; border: 1px solid var(--border-subtle); background: var(--bg-surface-2); color: var(--text-primary); font-size: 13px; }
.checkbox-label { font-size: 12px; color: var(--text-secondary); display: flex; align-items: center; gap: 4px; white-space: nowrap; }

.user-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.user-table th { text-align: left; padding: 8px 6px; border-bottom: 2px solid var(--border-subtle); color: var(--text-muted); font-weight: 600; }
.user-table td { padding: 8px 6px; border-bottom: 1px solid var(--border-subtle); }
.user-table tr.inactive td { opacity: 0.5; }
.time-cell { font-size: 12px; color: var(--text-muted); }

.table-input { height: 28px; padding: 0 6px; border-radius: 4px; border: 1px solid var(--border-subtle); background: var(--bg-surface); color: var(--text-primary); font-size: 13px; }

.btn-xs { font-size: 11px; padding: 3px 8px; border-radius: 4px; border: none; cursor: pointer; margin-right: 4px; }
.btn-sm { font-size: 12px; padding: 5px 12px; border-radius: 6px; border: none; cursor: pointer; }
.btn-primary { background: #1a3a5c; color: #fff; }
.btn-primary:hover { background: #152e4a; }
.btn-outline { background: none; border: 1px solid var(--border-subtle); color: var(--text-secondary); }
.btn-outline:hover { background: var(--bg-surface-2); }
.btn-danger { background: none; border: 1px solid #f28b82; color: #c62828; }
.btn-danger:hover { background: #fce8e6; }

.badge-active { font-size: 11px; padding: 2px 8px; border-radius: 10px; background: #e8f5e9; color: #2e7d32; }
.badge-inactive { font-size: 11px; padding: 2px 8px; border-radius: 10px; background: #f5f5f5; color: #9e9e9e; }

.loading-text, .empty-state { font-size: 13px; color: var(--text-muted); padding: 12px 0; }
.error-msg { font-size: 12px; color: #c62828; margin-top: 8px; }
.success-msg { font-size: 12px; color: #2e7d32; margin-top: 8px; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal-box { background: var(--bg-surface-1); border-radius: 10px; padding: 20px; width: 320px; max-width: 90vw; }
.modal-box h4 { margin: 0 0 4px; font-size: 14px; }
</style>
