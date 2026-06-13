/** Auth API — login, logout, session check. */

const BASE = '/labqc/auth'

export function login(username, password) {
  return fetch(`${BASE}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  }).then(r => {
    if (!r.ok) return r.json().then(d => Promise.reject(d.detail || '登录失败'))
    return r.json()
  })
}

export function logout(token) {
  return fetch(`${BASE}/logout`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token }),
  })
}

export function getMe(token) {
  return fetch(`${BASE}/me?token=${encodeURIComponent(token)}`).then(r => {
    if (!r.ok) return Promise.reject('会话已过期')
    return r.json()
  })
}
