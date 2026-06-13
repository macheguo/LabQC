import { ref } from 'vue'

const BASE = import.meta.env.BASE_URL

export function fetchLicenseStatus() {
  return fetch(`${BASE}license/status`).then(r => r.json())
}

export function activateLicense(token) {
  return fetch(`${BASE}license/activate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token }),
  }).then(r => r.json())
}
