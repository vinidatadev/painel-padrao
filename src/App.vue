<template>
  <LoginView v-if="!user" @logged-in="onLogin" />
  <TasksView v-else :user="user" @logout="onLogout" />
</template>

<script setup>
import { ref, inject, onMounted } from 'vue'
import LoginView from './views/LoginView.vue'
import TasksView from './views/TasksView.vue'

const msal = inject('msal')
const user = ref(null)

onMounted(async () => {
  // Trata retorno de redirect (caso use loginRedirect no futuro)
  await msal.handleRedirectPromise()
  const accounts = msal.getAllAccounts()
  if (accounts.length > 0) user.value = accounts[0]
})

function onLogin(account) {
  user.value = account
}

async function onLogout() {
  await msal.logoutPopup()
  user.value = null
}
</script>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', system-ui, sans-serif; }
</style>
