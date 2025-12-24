import { createRouter, createWebHistory, type RouteRecordRaw, RouterView } from 'vue-router';
import { h } from 'vue';
import { useAuthStore } from '../stores/auth';

// --- LAYOUTS & VIEWS ---
import MainLayout from '../layouts/MainLayout.vue';
import Login from '../modules/auth/views/Login.vue';
import NotFound from '../views/NotFound.vue';

// Dashboard
import DashboardHome from '../modules/dashboard/views/DashboardHome.vue';

// VIN Record Module
import VinCreatePage from '../modules/vin_record/views/VinCreatePage.vue';
import VinListPage from '../modules/vin_record/views/VinListPage.vue';
// [BARU] Import halaman Master Konfigurasi
import VinMasterPage from '../modules/vin_record/views/VinMasterPage.vue'; 

// Admin Module
import LabelDesigner from '../modules/admin/views/LabelDesigner.vue';
import RoleManager from '../modules/admin/views/RoleManager.vue';

// --- DEFINISI META DATA ---
declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean;
    requiresGuest?: boolean;
    requiresSuperuser?: boolean;
    module?: string; // Shorthand module name
    requiresModule?: string;    
    requiresPermission?: 'read' | 'create'; 
  }
}

// --- DUMMY COMPONENT (SOLUSI DOUBLE LAYOUT) ---
const EmptyRouterView = { 
  render: () => h(RouterView) 
};

const routes: Array<RouteRecordRaw> = [
  // 1. PUBLIC ROUTES
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresGuest: true }
  },

  // 2. PROTECTED ROUTES (MainLayout dipanggil DI SINI SAJA)
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: DashboardHome
      },

      // --- MODUL VIN RECORD ---
      {
        path: 'vin-record',
        component: EmptyRouterView, 
        children: [
          {
            path: '', 
            redirect: 'list' 
          },
          {
            path: 'list',   // URL: /vin-record/list
            name: 'VinList',
            component: VinListPage,
            // Izin: vin_record (Operational)
            meta: { module: 'vin_record', requiresPermission: 'read' }
          },
          {
            path: 'create', // URL: /vin-record/create
            name: 'VinCreate',
            component: VinCreatePage,
            // Izin: vin_record (Operational)
            meta: { module: 'vin_record', requiresPermission: 'create' }
          },
          // [BARU] ROUTE MASTER KONFIGURASI
          {
            path: 'master', // URL: /vin-record/master
            name: 'VinMaster',
            component: VinMasterPage,
            // PENTING: Permission mengarah ke 'vin_master' (Configuration)
            // Ini memisahkan Staff Produksi vs Manager Engineering
            meta: { module: 'vin_master', requiresPermission: 'read' }
          }
        ]
      },

      // --- MODUL ADMIN (Grouping) ---
      {
        path: 'admin',
        component: EmptyRouterView,
        meta: { requiresSuperuser: true },
        children: [
          {
            path: 'label-designer', // URL: /admin/label-designer
            name: 'LabelDesigner',
            component: LabelDesigner
          },
          {
            path: 'roles',          // URL: /admin/roles
            name: 'RoleManager',
            component: RoleManager
          }
        ]
      }
    ]
  },

  // 3. CATCH ALL (404)
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// --- MIDDLEWARE / GUARD ---
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore();

  // 1. Cek Auth
  if (to.matched.some(record => record.meta.requiresAuth) && !authStore.isAuthenticated) {
    return next('/login');
  }

  // 2. Cek Guest
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    return next('/');
  }

  // 3. Cek Superuser (Recursive Check)
  if (to.matched.some(record => record.meta.requiresSuperuser) && !authStore.isSuperuser) {
    // alert("Akses Ditolak: Halaman khusus Superuser/Admin."); // Opsional: Matikan alert agar tidak annoying saat redirect
    return next('/');
  }

  // 4. Cek Akses Modul Dynamic
  // Support 'meta.module' atau 'meta.requiresModule'
  const requiredModule = to.meta.module || to.meta.requiresModule;
  
  if (requiredModule) {
    const action = to.meta.requiresPermission || 'read';
    
    // Cek ke Pinia Store
    if (!authStore.can(requiredModule, action)) {
      // Jika user mencoba akses URL Master tapi tidak punya hak akses vin_master
      alert(`⛔ AKSES DITOLAK\n\nAnda tidak memiliki izin '${action}' untuk modul '${requiredModule}'.`);
      return next('/');
    }
  }

  next();
});

export default router;