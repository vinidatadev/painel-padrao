import { createApp } from 'vue'
import App from './App.vue'
import { PublicClientApplication } from '@azure/msal-browser'
import { msalConfig } from './authConfig'
import { setMsalGetter } from './api'

const msalInstance = new PublicClientApplication(msalConfig)

msalInstance.initialize().then(() => {
  // Registra o getter para que api.js possa adquirir tokens silenciosamente
  setMsalGetter(() => msalInstance)

  const app = createApp(App)
  app.provide('msal', msalInstance)
  app.mount('#app')
})
