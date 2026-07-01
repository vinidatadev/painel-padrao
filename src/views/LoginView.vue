<template>
  <div class="login-page">
    <div class="login-card">
      <div class="logo">todo-list-dev</div>
      <h1>Bem-vindo</h1>

      <!-- Login Microsoft -->
      <button class="btn-ms" @click="loginMicrosoft" :disabled="loading === 'ms'">
        <img
          src="https://learn.microsoft.com/en-us/azure/active-directory/develop/media/howto-add-branding-in-apps/ms-symbollockup_mssymbol_19.svg"
          alt="Microsoft"
        />
        {{ loading === 'ms' ? 'Entrando...' : 'Entrar com Microsoft' }}
      </button>

      <div class="divider"><span>ou</span></div>

      <!-- Login local -->
      <form @submit.prevent="loginLocal">
        <input
          v-model="email"
          type="email"
          placeholder="E-mail"
          autocomplete="email"
          required
        />
        <input
          v-model="password"
          type="password"
          placeholder="Senha"
          autocomplete="current-password"
          required
        />
        <button class="btn btn-primary" type="submit" :disabled="loading === 'local'">
          {{ loading === 'local' ? 'Entrando...' : 'Entrar' }}
        </button>
      </form>

      <p v-if="error" class="error" role="alert">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue'
import { loginRequest } from '../authConfig'
import { api, saveLocalToken } from '../api'

const emit = defineEmits(['logged-in'])
const msal  = inject('msal')

const loading  = ref('')   // '' | 'ms' | 'local'
const error    = ref('')
const email    = ref('')
const password = ref('')

async function loginMicrosoft() {
  loading.value = 'ms'
  error.value   = ''
  try {
    await msal.loginRedirect(loginRequest)
  } catch {
    error.value   = 'Erro ao autenticar. Tente novamente.'
    loading.value = ''
  }
}

async function loginLocal() {
  loading.value = 'local'
  error.value   = ''
  try {
    const res = await api.auth.login(email.value, password.value)
    saveLocalToken(res.access_token)
    emit('logged-in', { name: res.name, role: res.role, provider: 'local' })
  } catch (e) {
    error.value = e.message || 'Credenciais inválidas'
  } finally {
    loading.value = ''
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8edf5 100%);
}

.login-card {
  background: #fff;
  border-radius: 16px;
  padding: 3rem 2.5rem;
  box-shadow: 0 8px 32px rgba(0,0,0,.1);
  text-align: center;
  max-width: 380px;
  width: 100%;
}

.logo { font-size: 1.1rem; font-weight: 700; color: #0078d4; margin-bottom: 1.5rem; letter-spacing: .5px; }
h1 { font-size: 1.6rem; color: #1a1a2e; margin-bottom: 1.5rem; }

.btn-ms {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: .75rem;
  width: 100%;
  padding: .85rem 1.5rem;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: .95rem;
  font-weight: 500;
  cursor: pointer;
  transition: box-shadow .2s, border-color .2s;
  color: #1a1a2e;
}
.btn-ms:hover:not(:disabled) { box-shadow: 0 2px 12px rgba(0,120,212,.15); border-color: #0078d4; }
.btn-ms:disabled { opacity: .6; cursor: not-allowed; }
.btn-ms img { width: 20px; height: 20px; }

.divider {
  display: flex;
  align-items: center;
  gap: .75rem;
  margin: 1.25rem 0;
  color: #bbb;
  font-size: .85rem;
}
.divider::before,
.divider::after { content: ''; flex: 1; height: 1px; background: #eee; }

form { display: flex; flex-direction: column; gap: .75rem; }
form input {
  padding: .65rem 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: .95rem;
  outline: none;
}
form input:focus { border-color: #0078d4; }

.btn {
  padding: .75rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: .95rem;
  font-weight: 500;
  transition: opacity .2s;
}
.btn:hover:not(:disabled) { opacity: .85; }
.btn:disabled { opacity: .5; cursor: not-allowed; }
.btn-primary { background: #0078d4; color: #fff; }

.error { color: #e74c3c; font-size: .85rem; margin-top: 1rem; }
</style>
