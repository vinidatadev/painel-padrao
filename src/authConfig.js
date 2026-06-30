const clientId = import.meta.env.VITE_AZURE_CLIENT_ID
const tenantId = import.meta.env.VITE_AZURE_TENANT_ID
const redirectUri = import.meta.env.VITE_AZURE_REDIRECT_URI

if (!clientId || !tenantId || !redirectUri) {
  throw new Error('Variáveis VITE_AZURE_CLIENT_ID, VITE_AZURE_TENANT_ID e VITE_AZURE_REDIRECT_URI são obrigatórias no .env')
}

export const msalConfig = {
  auth: {
    clientId,
    authority: `https://login.microsoftonline.com/${tenantId}`,
    redirectUri
  },
  cache: {
    cacheLocation: 'sessionStorage',
    storeAuthStateInCookie: false
  }
}

export const loginRequest = {
  scopes: ['User.Read']
}
