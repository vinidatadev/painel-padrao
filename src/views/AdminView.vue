<template>
  <div class="admin-page">
    <div class="page-header">
      <h2>Usuários</h2>
      <button class="btn btn-primary" @click="openCreate">+ Novo Usuário</button>
    </div>

    <div v-if="errorMsg" class="alert-error" role="alert">{{ errorMsg }}</div>
    <div v-if="loading" class="state-msg">Carregando...</div>

    <div v-else class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Nome</th>
            <th>E-mail</th>
            <th>Provedor</th>
            <th>Role</th>
            <th>Status</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id">
            <td>{{ u.name }}</td>
            <td class="muted">{{ u.email }}</td>
            <td><span class="badge" :class="u.auth_provider">{{ u.auth_provider }}</span></td>
            <td><span class="badge" :class="u.role">{{ u.role }}</span></td>
            <td>
              <span class="badge" :class="u.is_active ? 'active' : 'inactive'">
                {{ u.is_active ? 'Ativo' : 'Inativo' }}
              </span>
            </td>
            <td class="actions">
              <button class="btn-icon" title="Editar" @click="openEdit(u)">✎</button>
              <button class="btn-icon danger" title="Remover" @click="removeUser(u.id)">✕</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal criar/editar -->
    <div v-if="modal" class="modal-overlay" @click.self="modal = null">
      <div class="modal">
        <h3>{{ modal.id ? 'Editar Usuário' : 'Novo Usuário' }}</h3>
        <form @submit.prevent="saveUser">
          <label>Nome
            <input v-model="modal.name" required />
          </label>
          <label v-if="!modal.id">E-mail
            <input v-model="modal.email" type="email" required />
          </label>
          <label v-if="!modal.id">Provedor
            <select v-model="modal.auth_provider">
              <option value="local">E-mail/senha</option>
              <option value="microsoft">Microsoft</option>
            </select>
          </label>
          <label v-if="!modal.id && modal.auth_provider === 'local'">Senha
            <input v-model="modal.password" type="password" required />
          </label>
          <label>Role
            <select v-model="modal.role">
              <option value="user">user</option>
              <option value="admin">admin</option>
            </select>
          </label>
          <label v-if="modal.id" class="checkbox-label">
            <input type="checkbox" v-model="modal.is_active" />
            Ativo
          </label>
          <div class="modal-actions">
            <button class="btn btn-primary" type="submit" :disabled="saving">
              {{ saving ? 'Salvando...' : 'Salvar' }}
            </button>
            <button class="btn btn-ghost" type="button" @click="modal = null">Cancelar</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'

const users    = ref([])
const loading  = ref(true)
const saving   = ref(false)
const errorMsg = ref('')
const modal    = ref(null)

onMounted(fetchUsers)

async function fetchUsers() {
  loading.value = true
  try {
    users.value = await api.users.list()
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    loading.value = false
  }
}

function openCreate() {
  modal.value = { name: '', email: '', auth_provider: 'local', role: 'user', password: '' }
}

function openEdit(u) {
  modal.value = { ...u }
}

async function saveUser() {
  saving.value = true
  errorMsg.value = ''
  try {
    if (modal.value.id) {
      const { name, role, is_active, password } = modal.value
      const updated = await api.users.update(modal.value.id, {
        name, role, is_active,
        ...(password ? { password } : {})
      })
      const idx = users.value.findIndex(u => u.id === updated.id)
      if (idx !== -1) users.value[idx] = updated
    } else {
      const created = await api.users.create(modal.value)
      users.value.push(created)
    }
    modal.value = null
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    saving.value = false
  }
}

async function removeUser(id) {
  if (!confirm('Remover este usuário?')) return
  try {
    await api.users.remove(id)
    users.value = users.value.filter(u => u.id !== id)
  } catch (e) {
    errorMsg.value = e.message
  }
}
</script>

<style scoped>
.admin-page { padding: 0; }

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.page-header h2 { font-size: 1.4rem; color: #1a1a2e; }

.table-wrapper { background: #fff; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,.06); overflow: hidden; }
table { width: 100%; border-collapse: collapse; }
thead { background: #f8f9fb; }
th { text-align: left; padding: .9rem 1.2rem; font-size: .8rem; text-transform: uppercase; color: #888; letter-spacing: .5px; border-bottom: 1px solid #eee; }
td { padding: .9rem 1.2rem; border-bottom: 1px solid #f0f0f0; font-size: .9rem; color: #333; }
tr:last-child td { border-bottom: none; }
.muted { color: #888; font-size: .85rem; }

.badge { display: inline-block; padding: .2rem .6rem; border-radius: 20px; font-size: .75rem; font-weight: 600; }
.badge.microsoft { background: #e3f0fb; color: #0078d4; }
.badge.local      { background: #f0f0f0; color: #555; }
.badge.admin      { background: #fce8ff; color: #8b00c9; }
.badge.user       { background: #e8f5e9; color: #2e7d32; }
.badge.active     { background: #d1e7dd; color: #0a5c36; }
.badge.inactive   { background: #fde8e8; color: #c0392b; }

.actions { display: flex; gap: .4rem; }
.btn-icon { background: none; border: 1px solid #ddd; border-radius: 6px; width: 32px; height: 32px; cursor: pointer; font-size: .9rem; display: flex; align-items: center; justify-content: center; transition: all .2s; }
.btn-icon:hover { background: #f0f7ff; border-color: #0078d4; color: #0078d4; }
.btn-icon.danger:hover { background: #fff0f0; border-color: #e74c3c; color: #e74c3c; }

.alert-error { background: #fff0f0; border: 1px solid #fcc; color: #c0392b; border-radius: 8px; padding: .75rem 1rem; margin-bottom: 1rem; font-size: .9rem; }
.state-msg { text-align: center; padding: 3rem; color: #aaa; background: #fff; border-radius: 10px; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.4); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { background: #fff; border-radius: 12px; padding: 2rem; width: 100%; max-width: 420px; box-shadow: 0 8px 32px rgba(0,0,0,.15); }
.modal h3 { font-size: 1.2rem; color: #1a1a2e; margin-bottom: 1.25rem; }
.modal form { display: flex; flex-direction: column; gap: .9rem; }
.modal label { display: flex; flex-direction: column; gap: .3rem; font-size: .85rem; color: #555; font-weight: 500; }
.modal input, .modal select { padding: .6rem .9rem; border: 1px solid #ddd; border-radius: 6px; font-size: .95rem; outline: none; }
.modal input:focus, .modal select:focus { border-color: #0078d4; }
.checkbox-label { flex-direction: row !important; align-items: center; gap: .5rem !important; }
.modal-actions { display: flex; gap: .5rem; margin-top: .25rem; }

.btn { padding: .55rem 1.2rem; border: none; border-radius: 6px; cursor: pointer; font-size: .9rem; font-weight: 500; transition: opacity .2s; }
.btn:hover:not(:disabled) { opacity: .85; }
.btn:disabled { opacity: .5; cursor: not-allowed; }
.btn-primary { background: #0078d4; color: #fff; }
.btn-ghost { background: transparent; color: #666; }
</style>
