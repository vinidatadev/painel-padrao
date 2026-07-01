/**
 * Cliente HTTP que injeta automaticamente o Bearer token do Azure
 * em todas as requisições ao backend.
 */

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

let _getMsal = null

export function setMsalGetter(fn) {
  _getMsal = fn
}

async function getToken() {
  const msal = _getMsal()
  const accounts = msal.getAllAccounts()
  if (!accounts.length) throw new Error('Usuário não autenticado')

  const response = await msal.acquireTokenSilent({
    scopes: ['User.Read'],
    account: accounts[0]
  })
  // Usa o idToken — JWT verificável emitido pelo Azure para esta aplicação
  return response.idToken
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
    throw new Error(err.detail || `Erro ${res.status}`)
  }
  return res.json()
}

export const api = {
  tasks: {
    list: ()              => request('GET',    '/api/tasks/'),
    create: (title)       => request('POST',   '/api/tasks/',        { title }),
    update: (id, payload) => request('PATCH',  `/api/tasks/${id}`,   payload),
    remove: (id)          => request('DELETE', `/api/tasks/${id}`)
  }
}
