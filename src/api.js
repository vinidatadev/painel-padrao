const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

let _getMsal = null

export function setMsalGetter(fn) { _getMsal = fn }

// Token local (login email/senha) guardado em sessionStorage
const LOCAL_TOKEN_KEY = 'local_token'

export function saveLocalToken(token) {
  sessionStorage.setItem(LOCAL_TOKEN_KEY, token)
}
export function clearLocalToken() {
  sessionStorage.removeItem(LOCAL_TOKEN_KEY)
}

async function getToken() {
  // Prioridade: token local > token Azure
  const local = sessionStorage.getItem(LOCAL_TOKEN_KEY)
  if (local) return local

  const msal = _getMsal?.()
  if (!msal) throw new Error('Usuário não autenticado')

  const accounts = msal.getAllAccounts()
  if (!accounts.length) throw new Error('Usuário não autenticado')

  const response = await msal.acquireTokenSilent({
    scopes: ['User.Read'],
    account: accounts[0]
  })
  return response.idToken
}

function parseError(err) {
  // Pydantic retorna { detail: [ {loc, msg, type}, ... ] } em erros de validação
  if (Array.isArray(err.detail)) {
    return err.detail.map(e => e.msg).join(', ')
  }
  return err.detail || 'Erro desconhecido'
}

async function request(method, path, body = null) {
  const token = await getToken()

  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: body ? JSON.stringify(body) : undefined
  })

  if (res.status === 204) return null
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Erro desconhecido' }))
    throw new Error(parseError(err))
  }
  return res.json()
}

export const api = {
  auth: {
    login:  (email, password) =>
      fetch(`${BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      }).then(async res => {
        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: 'Erro desconhecido' }))
          throw new Error(parseError(err))
        }
        return res.json()
      }),
    setup: (email, name, password) =>
      fetch(`${BASE_URL}/api/auth/setup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, name, password })
      }).then(async res => {
        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: 'Erro desconhecido' }))
          throw new Error(parseError(err))
        }
        return res.json()
      })
  },
  tasks: {
    list:   ()              => request('GET',    '/api/tasks/'),
    create: (title)         => request('POST',   '/api/tasks/',      { title }),
    update: (id, payload)   => request('PATCH',  `/api/tasks/${id}`, payload),
    remove: (id)            => request('DELETE', `/api/tasks/${id}`)
  },
  users: {
    list:   ()              => request('GET',    '/api/users/'),
    create: (data)          => request('POST',   '/api/users/',      data),
    update: (id, data)      => request('PATCH',  `/api/users/${id}`, data),
    remove: (id)            => request('DELETE', `/api/users/${id}`)
  }
}
