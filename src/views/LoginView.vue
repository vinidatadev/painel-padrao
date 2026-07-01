<template>
  <div class="login-page">
    <div class="login-card">
      <div class="logo">todo-list-dev</div>
      <h1>Bem-vindo</h1>
      <p>Faça login com sua conta Microsoft para acessar suas tarefas.</p>

      <button class="btn-ms" @click="login" :disabled="loading">
        <img
          src="https://learn.microsoft.com/en-us/azure/active-directory/develop/media/howto-add-branding-in-apps/ms-symbollockup_mssymbol_19.svg"
          alt="Microsoft"
        />
        {{ loading ? 'Entrando...' : 'Entrar com Microsoft' }}
      </button>

      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue'
import { loginRequest } from '../authConfig'

const emit = defineEmits(['logged-in'])
const msal = inject('msal')
const loading = ref(false)
const error = ref('')

async function login() {
  loading.value = true
  error.value = ''
  try {
    await msal.loginRedirect(loginRequest)
  } catch (e) {
    error.value = 'Erro ao autenticar. Tente novamente.'
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
  background: linear-gradient(135deg, #f5f7fa 0%, #e8edf5 100%);
}

.login-card {
  background: #fff;
  border-radius: 16px;
  padding: 3rem 2.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 380px;
  width: 100%;
}

.logo {
  font-size: 1.1rem;
  font-weight: 700;
  color: #0078d4;
  margin-bottom: 1.5rem;
  letter-spacing: .5px;
}

h1 {
  font-size: 1.6rem;
  color: #1a1a2e;
  margin-bottom: .5rem;
}

p {
  color: #666;
  font-size: .9rem;
  margin-bottom: 2rem;
  line-height: 1.5;
}

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

.btn-ms:hover:not(:disabled) {
  box-shadow: 0 2px 12px rgba(0, 120, 212, 0.15);
  border-color: #0078d4;
}

.btn-ms:disabled {
  opacity: .6;
  cursor: not-allowed;
}

.btn-ms img {
  width: 20px;
  height: 20px;
}

.error {
  color: #e74c3c;
  font-size: .85rem;
  margin-top: 1rem;
  margin-bottom: 0;
}
</style>
