import { throwIfError } from './helpers'

const BASE_URL = '/labqc'

// ── AI Config ──────────────────────────────────────────────

export async function getAiConfig() {
  const res = await fetch(`${BASE_URL}/settings/ai-config`)
  await throwIfError(res, 'Failed to load AI config')
  return res.json()
}

export async function setApiKey(apiKey) {
  const res = await fetch(`${BASE_URL}/settings/api-key`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ api_key: apiKey }),
  })
  await throwIfError(res, 'Failed to save API key')
}

export async function removeApiKey() {
  const res = await fetch(`${BASE_URL}/settings/api-key`, { method: 'DELETE' })
  await throwIfError(res, 'Failed to remove API key')
}

export async function setBaseUrl(baseUrl) {
  const res = await fetch(`${BASE_URL}/settings/base-url`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ base_url: baseUrl }),
  })
  await throwIfError(res, 'Failed to save base URL')
}

export async function setModel(model) {
  const res = await fetch(`${BASE_URL}/settings/model`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model }),
  })
  await throwIfError(res, 'Failed to save model')
}

// ── Lab Profile ────────────────────────────────────────────

export async function getLabProfile() {
  const res = await fetch(`${BASE_URL}/settings/lab-profile`)
  await throwIfError(res, 'Failed to load lab profile')
  return res.json()
}

export async function updateLabProfile(profile) {
  const res = await fetch(`${BASE_URL}/settings/lab-profile`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profile),
  })
  await throwIfError(res, 'Failed to save lab profile')
}

// ── LIS Config ──────────────────────────────────────────────

export async function getLisConfig() {
  const res = await fetch(`${BASE_URL}/lis/config`)
  await throwIfError(res, 'Failed to load LIS config')
  return res.json()
}

export async function updateLisConfig(config) {
  const res = await fetch(`${BASE_URL}/lis/config`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  })
  await throwIfError(res, 'Failed to save LIS config')
  return res.json()
}

export async function testParseHl7(rawMessage) {
  const res = await fetch(`${BASE_URL}/lis/test-parse`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ raw_message: rawMessage }),
  })
  await throwIfError(res, 'Failed to test parse')
  return res.json()
}

export async function restartLisListener() {
  const res = await fetch(`${BASE_URL}/lis/restart`, { method: 'POST' })
  await throwIfError(res, 'Failed to restart listener')
  return res.json()
}

export async function getLisMessages(limit = 20) {
  const res = await fetch(`${BASE_URL}/lis/messages?limit=${limit}`)
  await throwIfError(res, 'Failed to load LIS messages')
  return res.json()
}
