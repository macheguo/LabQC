import { throwIfError } from './helpers'

const BASE_URL = '/labqc'

// ── Institutions ──────────────────────────────────────────────────────

export async function fetchInstitutions() {
  const res = await fetch(`${BASE_URL}/eqa/institutions`)
  await throwIfError(res, '无法获取机构列表')
  return res.json()
}

export async function createInstitution(data) {
  const res = await fetch(`${BASE_URL}/eqa/institutions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  await throwIfError(res, '无法创建机构')
  return res.json()
}

export async function updateInstitution(id, data) {
  const res = await fetch(`${BASE_URL}/eqa/institutions/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  await throwIfError(res, '无法更新机构')
  return res.json()
}

export async function deleteInstitution(id) {
  const res = await fetch(`${BASE_URL}/eqa/institutions/${id}`, {
    method: 'DELETE',
  })
  await throwIfError(res, '无法删除机构')
}

// ── Programs ───────────────────────────────────────────────────────────

export async function fetchPrograms() {
  const res = await fetch(`${BASE_URL}/eqa/programs`)
  await throwIfError(res, '无法获取室间质评计划')
  return res.json()
}

export async function fetchProgram(id) {
  const res = await fetch(`${BASE_URL}/eqa/programs/${id}`)
  await throwIfError(res, '无法获取计划详情')
  return res.json()
}

export async function createProgram(data) {
  const res = await fetch(`${BASE_URL}/eqa/programs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  await throwIfError(res, '无法创建计划')
  return res.json()
}

export async function updateProgram(id, data) {
  const res = await fetch(`${BASE_URL}/eqa/programs/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  await throwIfError(res, '无法更新计划')
  return res.json()
}

// ── Samples ────────────────────────────────────────────────────────────

export async function fetchSamples(programId) {
  const res = await fetch(`${BASE_URL}/eqa/programs/${programId}/samples`)
  await throwIfError(res, '无法获取样品')
  return res.json()
}

export async function createSample(programId, data) {
  const res = await fetch(`${BASE_URL}/eqa/programs/${programId}/samples`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  await throwIfError(res, '无法创建样品')
  return res.json()
}

// ── Participants ───────────────────────────────────────────────────────

export async function fetchParticipants(programId) {
  const res = await fetch(`${BASE_URL}/eqa/programs/${programId}/participants`)
  await throwIfError(res, '无法获取参与机构')
  return res.json()
}

export async function createParticipant(programId, data) {
  const res = await fetch(`${BASE_URL}/eqa/programs/${programId}/participants`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  await throwIfError(res, '无法添加参与机构')
  return res.json()
}

// ── Results ────────────────────────────────────────────────────────────

export async function fetchResults(programId) {
  const res = await fetch(`${BASE_URL}/eqa/programs/${programId}/results`)
  await throwIfError(res, '无法获取结果')
  return res.json()
}

export async function createResult(programId, data) {
  const res = await fetch(`${BASE_URL}/eqa/programs/${programId}/results`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  await throwIfError(res, '无法提交结果')
  return res.json()
}

// ── Stats ──────────────────────────────────────────────────────────────

export async function fetchStats(programId) {
  const res = await fetch(`${BASE_URL}/eqa/programs/${programId}/stats`)
  await throwIfError(res, '无法获取统计数据')
  return res.json()
}

// ── Settings ───────────────────────────────────────────────────────────

export async function fetchSettings() {
  const res = await fetch(`${BASE_URL}/eqa/settings`)
  await throwIfError(res, '无法获取设置')
  return res.json()
}

export async function updateSettings(data) {
  const res = await fetch(`${BASE_URL}/eqa/settings`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  await throwIfError(res, '无法更新设置')
  return res.json()
}

// ── Import / Export ────────────────────────────────────────────────────

export async function importResults(programId, file) {
  const fd = new FormData()
  fd.append('file', file)
  const res = await fetch(`${BASE_URL}/eqa/programs/${programId}/import`, {
    method: 'POST',
    body: fd,
  })
  await throwIfError(res, '导入失败')
  return res.json()
}

export async function exportResults(programId, institution) {
  const res = await fetch(
    `${BASE_URL}/eqa/programs/${programId}/export?institution=${encodeURIComponent(institution)}`
  )
  await throwIfError(res, '导出失败')
  return res.json()
}

// ── Portal ─────────────────────────────────────────────────────────────

export async function fetchPortal(programId, access) {
  const res = await fetch(`${BASE_URL}/eqa/portal/${programId}?access=${encodeURIComponent(access)}`)
  await throwIfError(res, '无法访问门户')
  return res.json()
}

export async function submitPortal(programId, access, data) {
  const res = await fetch(`${BASE_URL}/eqa/portal/${programId}/submit?access=${encodeURIComponent(access)}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  await throwIfError(res, '提交失败')
  return res.json()
}
