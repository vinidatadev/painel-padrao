<template>
  <LoginView v-if="!user" @logged-in="onLogin" />

  <div v-else class="app-shell">
    <header class="navbar">
      <div class="logo">todo-list-dev</div>
      <nav class="nav-links">
        <button :class="['nav-btn', { active: view === 'tasks' }]" @click="view = 'tasks'">Tarefas</button>
        <button v-if="user.role === 'admin'" :class="['nav-btn', { active: view === 'admin' }]" @click="view = 'admin'">
          Usuários
        </button>
      </nav>
      <div class="nav-right">
        <span class="user-info">{{ user.name }}</span>
        <button class="btn btn-outline" @click="onLogout">Sair</button>
      </div>
    </header>

    <main class="content">
      <TasksView v-if="view === 'tasks'" :user="user" />
      <AdminView v-else-if="view === 'admin' && user.role === 'admin'" />
    </main>

    <footer class="version-bar">
      front v{{ frontVersion }} · back v{{ backendVersion }}
    </footer>
  </div>
</template>

<script setup>
import { ref, inject, onMounted } from 'vue'
import LoginView from './views/LoginView.vue'
import TasksView from './views/TasksView.vue'
import AdminView from './views/AdminView.vue'
import { clearLocalToken, api } from './api'

const msal    = inject('msal')
const user    = ref(null)
const view    = ref('tasks')
const backendVersion = ref('...')

const frontVersion = __APP_VERSION__

onMounted(async () => {
  // Busca versão do backend
  fetch(import.meta.env.VITE_API_URL + '/health')
    .then(r => r.json())
    .then(d => { backendVersion.value = d.version || '?' })
    .catch(() => { backendVersion.value = 'offline' })
  // Tenta restaurar sessão local primeiro
  const localToken = sessionStorage.getItem('local_token')
  if (localToken) {
    try {
      const payload = JSON.parse(atob(localToken.split('.')[1]))
      // Verifica se o token ainda não expirou (exp em segundos)
      if (payload.exp && payload.exp * 1000 > Date.now()) {
        user.value = { name: payload.name, role: payload.role, provider: 'local' }
        return
      }
    } catch { /* token malformado */ }
    // Token expirado ou inválido — limpa
    sessionStorage.removeItem('local_token')
  }

  // Depois tenta restaurar sessão Microsoft
  const response = await msal.handleRedirectPromise()
  if (response?.account) {
    await setMicrosoftUser(response.account)
    return
  }
  const accounts = msal.getAllAccounts()
  if (accounts.length > 0) {
    await setMicrosoftUser(accounts[0])
  }
})

async function setMicrosoftUser(account) {
  // Busca role real do backend em vez de hardcodar 'user'
  try {
    const me = await api.auth.me()
    user.value = { name: me.name, role: me.role, provider: 'microsoft' }
  } catch {
    // Usuário Microsoft não cadastrado na tabela — não loga
    user.value = null
  }
}

function onLogin(account) {
  user.value = account
}

async function onLogout() {
  clearLocalToken()
  if (user.value?.provider === 'microsoft') {
    await msal.logoutRedirect()
  }
  user.value = null
}
</script>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', system-ui, sans-serif; background: #f5f7fa; }

.app-shell { min-height: 100vh; display: flex; flex-direction: column; }

.navbar {
  display: flex;
  align-items: center;
  padding: 1rem 2rem;
  background: #fff;
  border-bottom: 1px solid #e8eaf0;
  box-shadow: 0 1px 4px rgba(0,0,0,.05);
  gap: 1.5rem;
}
.logo { font-size: 1.1rem; font-weight: 700; color: #0078d4; }
.nav-links { display: flex; gap: .25rem; flex: 1; }
.nav-btn { background: none; border: none; padding: .4rem .9rem; border-radius: 6px; cursor: pointer; font-size: .9rem; color: #555; transition: background .15s, color .15s; }
.nav-btn:hover { background: #f0f7ff; color: #0078d4; }
.nav-btn.active { background: #e3f0fb; color: #0078d4; font-weight: 600; }
.nav-right { display: flex; align-items: center; gap: 1rem; }
.user-info { font-size: .85rem; color: #666; }

.content { max-width: 900px; width: 100%; margin: 2rem auto; padding: 0 1rem; }

.version-bar {
  margin-top: auto;
  padding: .5rem 2rem;
  text-align: right;
  font-size: .72rem;
  color: #bbb;
  border-top: 1px solid #eee;
  background: #fff;
}

.btn { padding: .5rem 1.2rem; border: none; border-radius: 6px; cursor: pointer; font-size: .9rem; font-weight: 500; transition: opacity .2s; }
.btn:hover { opacity: .85; }
.btn-outline { background: transparent; border: 1px solid #0078d4; color: #0078d4; }
</style>
