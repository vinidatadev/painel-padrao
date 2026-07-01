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
  // Trata retorno do loginRedirect
  const response = await msal.handleRedirectPromise()
  if (response?.account) {
    user.value = response.account
    return
  }
  const accounts = msal.getAllAccounts()
  if (accounts.length > 0) user.value = accounts[0]
})

function onLogin(account) {
  user.value = account
}

async function onLogout() {
  await msal.logoutRedirect()
  user.value = null
}
</script>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', system-ui, sans-serif; }
</style>
