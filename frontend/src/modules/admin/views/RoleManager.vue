<template>
  <div class="admin-panel">
    
    <div class="header-section">
      <div>
        <h1>Admin Control Panel</h1>
        <p>Pusat kendali akses, pengguna, dan modul sistem.</p>
      </div>
      <div class="user-status">
        <span class="badge superuser">SUPERUSER ACCESS</span>
      </div>
    </div>

    <div class="tabs">
      <button :class="{ active: activeTab === 'roles' }" @click="activeTab = 'roles'">
        🛡️ Roles & Permissions
      </button>
      <button :class="{ active: activeTab === 'users' }" @click="activeTab = 'users'">
        👥 Users Management
      </button>
      <button :class="{ active: activeTab === 'modules' }" @click="activeTab = 'modules'">
        📦 System Modules
      </button>
    </div>

    <div v-if="activeTab === 'roles'" class="panel-content grid-layout">
      
      <div class="card role-list">
        <div class="card-header">
          <h3>Daftar Role</h3>
          <button @click="openModal('addRole')" class="btn-small">+ Role Baru</button>
        </div>
        
        <div v-if="isLoading" class="p-20 text-center text-muted">Loading...</div>
        
        <ul v-else>
          <li 
            v-for="role in roles" 
            :key="role.id" 
            @click="selectRole(role)"
            :class="{ active: selectedRole?.id === role.id }"
          >
            <div class="role-item">
              <span class="role-name">{{ role.name }}</span>
              <span class="role-desc" v-if="role.description">{{ role.description }}</span>
            </div>
            <span class="arrow">›</span>
          </li>
        </ul>
      </div>

      <div class="card permission-matrix">
        <div v-if="selectedRole">
          
          <div class="matrix-header">
            <div>
              <h3>Akses: {{ selectedRole.name }}</h3>
              <p>Centang akses yang diinginkan, lalu klik Simpan.</p>
            </div>
            
            <div class="header-actions">
              <button @click="deleteRole(selectedRole.id)" class="btn-danger-outline mr-2">Hapus Role</button>
              
              <button 
                v-if="hasUnsavedChanges" 
                @click="saveCurrentRolePermissions" 
                class="btn-primary" 
                :disabled="isSaving"
              >
                {{ isSaving ? 'Menyimpan...' : '💾 SIMPAN PERUBAHAN' }}
              </button>
              <span v-else class="status-clean">✓ Data Tersimpan</span>
            </div>
          </div>
          
          <div class="table-responsive">
            <table class="matrix-table">
              <thead>
                <tr>
                  <th>Modul</th>
                  <th class="text-center">Read</th>
                  <th class="text-center">Create</th>
                  <th class="text-center">Update</th>
                  <th class="text-center">Delete</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="mod in modules" :key="mod.id">
                  <td class="module-name">
                    <strong>{{ mod.name }}</strong>
                    <div class="code-badge">{{ mod.code }}</div>
                  </td>
                  
                  <td class="text-center" v-if="getPermission(selectedRole.id, mod.id)">
                    <input type="checkbox" v-model="getPermission(selectedRole.id, mod.id).can_read" @change="markDirty">
                  </td>
                  <td class="text-center" v-if="getPermission(selectedRole.id, mod.id)">
                    <input type="checkbox" v-model="getPermission(selectedRole.id, mod.id).can_create" @change="markDirty">
                  </td>
                  <td class="text-center" v-if="getPermission(selectedRole.id, mod.id)">
                    <input type="checkbox" v-model="getPermission(selectedRole.id, mod.id).can_update" @change="markDirty">
                  </td>
                  <td class="text-center" v-if="getPermission(selectedRole.id, mod.id)">
                    <input type="checkbox" v-model="getPermission(selectedRole.id, mod.id).can_delete" @change="markDirty">
                  </td>

                  <td v-if="!getPermission(selectedRole.id, mod.id)" colspan="4" class="text-center text-muted">
                    <small>Belum disinkronisasi</small>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="info-footer">
            <button @click="syncMatrix" class="btn-link">⚠️ Checkbox tidak muncul? Klik di sini untuk Sync Database</button>
          </div>

        </div>
        
        <div v-else class="empty-state">
          <div class="empty-icon">🛡️</div>
          <p>Pilih Role di sebelah kiri untuk mengatur izin akses.</p>
        </div>
      </div>
    </div>

    <div v-if="activeTab === 'users'" class="panel-content">
      <div class="card">
        <div class="card-header">
          <h3>Daftar Pengguna</h3>
          <button @click="openModal('addUser')" class="btn-primary">+ User Baru</button>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>User Info</th>
              <th>Status</th>
              <th>Role Saat Ini</th>
              <th>Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>
                <div class="user-row">
                  <div class="avatar-sm">{{ user.username.charAt(0).toUpperCase() }}</div>
                  <div>
                    <div class="username">{{ user.username }}</div>
                    <div class="email">{{ user.email || 'No Email' }}</div>
                  </div>
                </div>
              </td>
              <td>
                <span :class="['badge', user.is_active ? 'success' : 'danger']">
                  {{ user.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td>
                <select class="role-select" @change="assignRole(user, $event)" :disabled="user.username === 'admin'">
                  <option value="">-- No Role --</option>
                  <option v-for="role in roles" :key="role.id" :value="role.id" :selected="user.user_roles.length > 0 && user.user_roles[0].role === role.id">
                    {{ role.name }}
                  </option>
                </select>
              </td>
              <td>
                <button v-if="user.username !== 'admin'" @click="deleteUser(user.id)" class="btn-icon-danger">🗑️</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="activeTab === 'modules'" class="panel-content">
      <div class="card">
        <div class="card-header">
          <h3>Daftar Modul Sistem</h3>
          <button @click="openModal('addModule')" class="btn-primary">+ Modul Baru</button>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>Nama Modul</th>
              <th>Kode Sistem</th>
              <th>Aksi</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="mod in modules" :key="mod.id">
              <td><strong>{{ mod.name }}</strong></td>
              <td><span class="code-badge">{{ mod.code }}</span></td>
              <td><button @click="deleteModule(mod.id)" class="btn-icon-danger">🗑️</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="modal.isOpen" class="modal-overlay">
      <div class="modal-card">
        <h3>{{ modal.title }}</h3>
        <div v-if="modal.type === 'addRole'">
          <div class="form-group"><label>Nama Role</label><input v-model="form.roleName" /></div>
          <div class="form-group"><label>Deskripsi</label><input v-model="form.roleDesc" /></div>
        </div>
        <div v-if="modal.type === 'addModule'">
          <div class="form-group"><label>Nama Modul</label><input v-model="form.moduleName" /></div>
          <div class="form-group"><label>Kode Modul</label><input v-model="form.moduleCode" /></div>
        </div>
        <div v-if="modal.type === 'addUser'">
          <div class="form-group"><label>Username</label><input v-model="form.username" /></div>
          <div class="form-group"><label>Email</label><input type="email" v-model="form.email" /></div>
          <div class="form-group"><label>Password</label><input type="password" v-model="form.password" /></div>
        </div>
        <div class="modal-actions">
          <button @click="modal.isOpen = false" class="btn-secondary">Batal</button>
          <button @click="handleModalSubmit" class="btn-primary">Simpan</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000/api';

// STATE
const activeTab = ref('roles');
const isLoading = ref(false);
const isSaving = ref(false);
const hasUnsavedChanges = ref(false);

const roles = ref<any[]>([]);
const users = ref<any[]>([]);
const modules = ref<any[]>([]);
const allPermissions = ref<any[]>([]); 

const selectedRole = ref<any>(null);

// Modal & Form State
const modal = reactive({ isOpen: false, type: '', title: '' });
const form = reactive({ roleName: '', roleDesc: '', moduleName: '', moduleCode: '', username: '', email: '', password: '' });

// --- INIT DATA ---
const initData = async () => {
  isLoading.value = true;
  try {
    const [resRoles, resUsers, resMods, resPerms] = await Promise.all([
      axios.get(`${API_URL}/roles/`),
      axios.get(`${API_URL}/users/`),
      axios.get(`${API_URL}/system-modules/`),
      axios.get(`${API_URL}/role-permissions/`) 
    ]);
    roles.value = resRoles.data;
    users.value = resUsers.data;
    modules.value = resMods.data;
    allPermissions.value = resPerms.data;
  } catch (e) {
    console.error(e);
  } finally {
    isLoading.value = false;
  }
};

onMounted(initData);

// --- ROLE SELECTION & EDITING ---

const selectRole = (role: any) => {
  // Jika ada perubahan belum disimpan, tanya user dulu
  if (hasUnsavedChanges.value) {
    if (!confirm("Anda memiliki perubahan yang belum disimpan. Yakin ingin pindah role? Perubahan akan hilang.")) return;
  }
  
  selectedRole.value = role;
  hasUnsavedChanges.value = false; // Reset flag saat ganti role
};

// Helper untuk mengambil object permission dari state global
// Ini kunci agar "Master Detail" bekerja tanpa fetch berulang
const getPermission = (roleId: number, moduleId: number) => {
  return allPermissions.value.find(p => p.role === roleId && p.module === moduleId);
};

// Tandai ada perubahan (untuk memunculkan tombol Simpan)
const markDirty = () => {
  hasUnsavedChanges.value = true;
};

// --- SAVE ACTION (BATCH UPDATE) ---
const saveCurrentRolePermissions = async () => {
  if (!selectedRole.value) return;
  
  isSaving.value = true;
  try {
    // 1. Ambil hanya permission milik role yang sedang dipilih
    const permissionsToUpdate = allPermissions.value.filter(p => p.role === selectedRole.value.id);
    
    // 2. Kirim ke Backend (Bulk Update)
    await axios.post(`${API_URL}/role-permissions/bulk-update/`, permissionsToUpdate);
    
    alert("Perubahan berhasil disimpan!");
    hasUnsavedChanges.value = false;
  } catch (e) {
    console.error(e);
    alert("Gagal menyimpan perubahan.");
  } finally {
    isSaving.value = false;
  }
};

// --- SYNC MATRIX (UTILITY) ---
// Jika checkbox tidak muncul, panggil ini untuk generate record di DB
const syncMatrix = async () => {
  try {
    const res = await axios.post(`${API_URL}/role-permissions/sync-matrix/`);
    await initData();
    alert(res.data.message);
  } catch (e) { alert("Gagal sinkronisasi."); }
};

// --- CRUD LAINNYA ---
const deleteRole = async (id: number) => {
  if(!confirm("Yakin hapus role ini?")) return;
  await axios.delete(`${API_URL}/roles/${id}/`);
  selectedRole.value = null;
  initData();
};

const assignRole = async (user: any, event: any) => {
  const newRoleId = event.target.value;
  try {
    if (user.user_roles.length > 0) await axios.delete(`${API_URL}/user-roles/${user.user_roles[0].id}/`);
    if (newRoleId) await axios.post(`${API_URL}/user-roles/`, { user: user.id, role: newRoleId });
    const res = await axios.get(`${API_URL}/users/`);
    users.value = res.data;
    alert("Role user diperbarui.");
  } catch (e) { alert("Gagal update role user."); }
};

const deleteUser = async (id: number) => {
  if(!confirm("Hapus user?")) return;
  await axios.delete(`${API_URL}/users/${id}/`);
  initData();
};

const deleteModule = async (id: number) => {
  if(!confirm("Hapus modul?")) return;
  await axios.delete(`${API_URL}/system-modules/${id}/`);
  initData();
};

// --- MODAL HANDLING ---
const openModal = (type: string) => {
  modal.type = type; modal.isOpen = true;
  form.roleName = ''; form.roleDesc = ''; form.moduleName = ''; form.moduleCode = ''; form.username = ''; form.password = '';
  if(type === 'addRole') modal.title = "Tambah Role Baru";
  if(type === 'addModule') modal.title = "Tambah Modul Sistem";
  if(type === 'addUser') modal.title = "Tambah User Baru";
};

const handleModalSubmit = async () => {
  try {
    if (modal.type === 'addRole') {
      if(!form.roleName) return alert("Nama role wajib");
      await axios.post(`${API_URL}/roles/`, { name: form.roleName, description: form.roleDesc });
    } else if (modal.type === 'addModule') {
      if(!form.moduleName) return alert("Data modul wajib");
      await axios.post(`${API_URL}/system-modules/`, { name: form.moduleName, code: form.moduleCode });
    } else if (modal.type === 'addUser') {
      await axios.post(`${API_URL}/users/`, { username: form.username, email: form.email, password: form.password });
    }
    modal.isOpen = false;
    initData();
    // Jika menambah modul baru, kita auto-sync permission agar checkbox langsung muncul
    if (modal.type === 'addModule' || modal.type === 'addRole') {
      await axios.post(`${API_URL}/role-permissions/sync-matrix/`);
      initData();
    }
  } catch (e: any) {
    const msg = e.response?.data ? JSON.stringify(e.response.data) : "Gagal menyimpan";
    alert(msg);
  }
};
</script>

<style scoped>
.admin-panel { max-width: 1400px; margin: 0 auto; padding-bottom: 50px; }

/* HEADER */
.header-section { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; padding-bottom: 20px; border-bottom: 1px solid var(--border-color); }
.header-section h1 { margin: 0; font-size: 1.8rem; color: var(--text-primary); }
.badge.superuser { background: #000; color: #fff; padding: 5px 10px; font-weight: bold; border-radius: 4px; font-size: 0.7rem; }

/* TABS */
.tabs { display: flex; gap: 10px; margin-bottom: 20px; }
.tabs button { padding: 12px 24px; background: transparent; border: 1px solid transparent; border-radius: 8px; font-weight: 600; cursor: pointer; color: var(--text-secondary); transition: all 0.2s; }
.tabs button.active { background: white; color: var(--primary-color); border-color: var(--border-color); box-shadow: var(--shadow-sm); }
.tabs button:hover:not(.active) { background: rgba(0,0,0,0.03); }

/* GRID LAYOUT (Master Detail) */
.grid-layout { display: grid; grid-template-columns: 300px 1fr; gap: 24px; align-items: start; }
.card { background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border-color); overflow: hidden; box-shadow: var(--shadow-sm); }
.card-header { padding: 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); }
.card-header h3 { margin: 0; font-size: 1.1rem; }

/* ROLE LIST */
.role-list ul { list-style: none; padding: 0; margin: 0; max-height: 600px; overflow-y: auto; }
.role-list li { padding: 16px 20px; cursor: pointer; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; transition: 0.2s; }
.role-list li:hover { background: #f8fafc; }
.role-list li.active { background: #eff6ff; border-left: 4px solid var(--primary-color); }
.role-name { font-weight: 600; display: block; color: var(--text-primary); }
.role-desc { font-size: 0.8rem; color: var(--text-secondary); }

/* PERMISSION DETAILS */
.matrix-header { padding: 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); background: #fafafa; }
.header-actions { display: flex; align-items: center; gap: 10px; }
.status-clean { color: #10b981; font-weight: 700; font-size: 0.9rem; }

.table-responsive { width: 100%; overflow-x: auto; }
.matrix-table { width: 100%; border-collapse: collapse; }
.matrix-table th { background: #f8fafc; padding: 12px; text-align: left; font-size: 0.85rem; color: #64748b; border-bottom: 1px solid var(--border-color); }
.matrix-table td { padding: 12px; border-bottom: 1px solid var(--border-color); vertical-align: middle; }
.module-name strong { display: block; color: var(--text-primary); }
.code-badge { font-family: monospace; font-size: 0.75rem; background: #e2e8f0; padding: 2px 6px; border-radius: 4px; color: #475569; display: inline-block; margin-top: 4px; }
.text-center { text-align: center; }
.text-muted { color: #94a3b8; }
input[type="checkbox"] { width: 18px; height: 18px; cursor: pointer; accent-color: var(--primary-color); }

/* UTILS */
.btn-primary { background: var(--primary-color); color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: 600; }
.btn-primary:disabled { opacity: 0.7; cursor: not-allowed; }
.btn-small { background: #f1f5f9; color: #334155; border: 1px solid #cbd5e1; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 0.8rem; font-weight: 600; }
.btn-danger-outline { background: white; color: #ef4444; border: 1px solid #ef4444; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 0.8rem; }
.btn-secondary { background: #94a3b8; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; margin-right: 10px; }
.btn-link { background: none; border: none; color: var(--primary-color); cursor: pointer; text-decoration: underline; font-size: 0.85rem; }
.btn-icon-danger { background: transparent; border: none; cursor: pointer; font-size: 1.1rem; opacity: 0.7; }

.empty-state { padding: 60px; text-align: center; color: var(--text-secondary); }
.empty-icon { font-size: 3rem; margin-bottom: 10px; opacity: 0.5; }
.info-footer { padding: 10px; text-align: center; background: #fffbeb; border-top: 1px solid #fcd34d; font-size: 0.85rem; color: #92400e; }
.p-20 { padding: 20px; }
.mr-2 { margin-right: 8px; }

/* DATA TABLE (USERS/MODULES) */
.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td { padding: 14px 16px; text-align: left; border-bottom: 1px solid var(--border-color); }
.data-table th { background: #f8fafc; }
.user-row { display: flex; align-items: center; gap: 12px; }
.avatar-sm { width: 36px; height: 36px; background: #cbd5e1; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; }
.role-select { padding: 8px; border-radius: 6px; border: 1px solid var(--border-color); }
.badge { padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
.badge.success { background: #dcfce7; color: #166534; }
.badge.danger { background: #fee2e2; color: #991b1b; }

/* MODAL */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; backdrop-filter: blur(2px); }
.modal-card { background: white; padding: 30px; border-radius: 12px; width: 400px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); }
.modal-actions { text-align: right; margin-top: 20px; }
.form-group { margin-bottom: 15px; }
.form-group label { display: block; margin-bottom: 5px; font-weight: 600; font-size: 0.9rem; }
.form-group input { width: 100%; padding: 10px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; }
</style>