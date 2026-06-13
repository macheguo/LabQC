<template>
  <div class="login-page">
    <div class="login-card">
      <div class="logo">
        <svg width="64" height="64" viewBox="0 0 64 64">
          <rect width="64" height="64" rx="14" fill="#1a3a5c"/>
          <text x="32" y="42" text-anchor="middle" fill="white" font-size="24" font-weight="700" font-family="sans-serif">LQ</text>
        </svg>
      </div>
      <h2>{{ $t('login.title') }}</h2>
      <p class="sub">{{ $t('login.subtitle') }}</p>

      <form @submit.prevent="handleLogin">
        <div class="field">
          <label>{{ $t('login.username') }}</label>
          <input
            v-model="username"
            type="text"
            :placeholder="$t('login.usernamePlaceholder')"
            autocomplete="username"
            required
          />
        </div>
        <div class="field">
          <label>{{ $t('login.password') }}</label>
          <input
            v-model="password"
            type="password"
            :placeholder="$t('login.passwordPlaceholder')"
            autocomplete="current-password"
            required
          />
        </div>

        <p v-if="error" class="error">{{ error }}</p>

        <button type="submit" :disabled="loading" class="btn-login">
          {{ loading ? $t('login.loggingIn') : $t('login.loginBtn') }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import * as authApi from '../api/authApi.js'

const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    const res = await authApi.login(username.value, password.value)
    localStorage.setItem('labqc_token', res.token)
    localStorage.setItem('labqc_user', JSON.stringify({
      username: res.username,
      display_name: res.display_name,
      is_admin: res.is_admin,
    }))
    const to = router.currentRoute.value.query.redirect || '/'
    router.push(to)
  } catch (e) {
    error.value = typeof e === 'string' ? e : (e.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e9ecf1;
}

.login-card {
  background: #fff;
  border: 1px solid #dde0e4;
  border-radius: 10px;
  padding: 40px 36px;
  width: 380px;
  max-width: 90vw;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.login-card .logo {
  margin-bottom: 12px;
}

.login-card h2 {
  margin: 0 0 4px;
  color: #1a3a5c;
  font-size: 22px;
}

.login-card .sub {
  margin: 0 0 24px;
  color: #8894a4;
  font-size: 13px;
}

.field {
  text-align: left;
  margin-bottom: 16px;
}

.field label {
  display: block;
  margin-bottom: 6px;
  font-size: 13px;
  color: #445;
  font-weight: 500;
}

.field input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d0d5dc;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
  outline: none;
  transition: border-color 0.15s;
}

.field input:focus {
  border-color: #1a3a5c;
}

.error {
  color: #d32f2f;
  font-size: 13px;
  margin: -4px 0 12px;
}

.btn-login {
  width: 100%;
  padding: 10px 0;
  background: #1a3a5c;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 15px;
  cursor: pointer;
  font-weight: 500;
}

.btn-login:hover {
  background: #152e4a;
}

.btn-login:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
