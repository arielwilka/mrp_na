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
import VinMasterPage from '../modules/vin_record/views/VinMasterPage.vue'; 

// [BARU] Product Module
import ProductMasterPage from '../modules/product/views/ProductMasterPage.vue';

// Battery Record Module
import BatteryQCPage from '../modules/battery_record/views/BatteryQCPage.vue';
import BatteryHistoryPage from '../modules/battery_record/views/BatteryHistoryPage.vue';

// Admin Module
import LabelDesigner from '../modules/admin/views/LabelDesigner.vue';
import RoleManager from '../modules/admin/views/RoleManager.vue';

import RuleList from '../modules/traceability/views/RuleList.vue';
import RuleForm from '../modules/traceability/views/RuleForm.vue';
import PartList from '../modules/traceability/views/PartList.vue';
import PartForm from '../modules/traceability/views/PartForm.vue';
import BOMList from '../modules/traceability/views/BOMList.vue';
import BOMForm from '../modules/traceability/views/BOMForm.vue';
import QCStation from '../modules/qc/views/QCStation.vue';
import PartTemplate from '../modules/traceability/views/PartTemplate.vue';
import QCList from '../modules/qc/views/QCList.vue';
// --- DEFINISI META DATA ---
declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean;
    requiresGuest?: boolean;
    requiresSuperuser?: boolean;
    module?: string; // Shorthand module name untuk permission check
    requiresModule?: string;    
    requiresPermission?: 'read' | 'create' | 'delete'; 
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

      // --- [BARU] MODUL PRODUCT MASTER ---
      {
        path: 'product-master', // URL: /product-master
        name: 'ProductMaster',
        component: ProductMasterPage,
        // Meta: module 'product_master' (Pastikan permission ini ada di backend/store)
        meta: { module: 'product_master', requiresPermission: 'read' }
      },
      {
        path: 'traceability',
        component: EmptyRouterView, // Agar bisa punya anak
        children: [
          // 1. RULES ENGINE
          {
            path: 'rules',
            name: 'RuleList',
            component: RuleList,
            meta: { module: 'traceability', requiresPermission: 'read' }
          },
          {
            path: 'rules/create',
            name: 'RuleCreate',
            component: RuleForm,
            meta: { module: 'traceability', requiresPermission: 'create' }
          },
          {
            path: 'rules/:id/edit',
            name: 'RuleEdit',
            component: RuleForm,
            props: true,
            meta: { module: 'traceability', requiresPermission: 'create' }
          },

          // 2. PART MASTER
          {
            path: 'parts',
            name: 'PartList',
            component: PartList,
            meta: { module: 'traceability', requiresPermission: 'read' }
          },
          {
            path: 'parts/create',
            name: 'PartCreate',
            component: PartForm,
            meta: { module: 'traceability', requiresPermission: 'create' }
          },
          {
            path: 'parts/:id/edit',
            name: 'PartEdit',
            component: PartForm,
            props: true,
            meta: { module: 'traceability', requiresPermission: 'create' }
          },
          {
            path: 'parts/:id/template',
            name: 'PartTemplate',
            component: PartTemplate,
            props: true,
            meta: { module: 'traceability', requiresPermission: 'create', title: 'Setup QC Parameters' }
          },

          // 3. BOM CONFIG
          {
            path: 'bom',
            name: 'BOMList',
            component: BOMList,
            meta: { module: 'traceability', requiresPermission: 'read' }
          },
          {
            path: 'bom/create',
            name: 'BOMCreate',
            component: BOMForm,
            meta: { module: 'traceability', requiresPermission: 'create' }
          },
          {
            path: 'bom/:id/edit',
            name: 'BOMEdit',
            component: BOMForm,
            props: true,
            meta: { module: 'traceability', requiresPermission: 'create' }
          }
        ]
      },
      {
        path: 'qc',
        component: EmptyRouterView, // Gunakan wrapper agar URL rapi (/qc/station)
        children: [
          {
            path: 'station', // URL: /qc/station
            name: 'QCStation',
            component: QCStation,
            meta: { 
              module: 'qc', // Sesuaikan dengan nama app di backend
              requiresPermission: 'create', // Operator butuh akses create/write untuk submit
              title: 'QC Workstation' 
            }
          },
          {
            path: 'history', // URL: /qc/history
            name: 'QCList',
            component: QCList,
            meta: { module: 'qc', requiresPermission: 'read', title: 'Riwayat QC' }
          }
          // Jika nanti Anda buat halaman history:
          /*
          {
            path: 'history',
            name: 'QCHistory',
            component: QCHistory,
            meta: { module: 'qc', requiresPermission: 'read' }
          }
          */
        ]
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
          // Master Konfigurasi VIN (Prefix, Year Code)
          {
            path: 'master', // URL: /vin-record/master
            name: 'VinMaster',
            component: VinMasterPage,
            meta: { module: 'vin_master', requiresPermission: 'read' }
          }
        ]
      },
      
      // --- MODUL BATTERY RECORD ---
      {
        path: 'battery-qc',
        component: EmptyRouterView, 
        children: [
          {
            path: '', // URL: /battery-qc
            name: 'BatteryQC',
            component: BatteryQCPage,
            meta: { 
                module: 'battery_record', 
                requiresPermission: 'read', 
                title: 'Battery Quality Control' 
            }
          },
          {
            path: 'list', // URL: /battery-qc/list
            name: 'BatteryList',
            component: BatteryHistoryPage,
            meta: { 
                module: 'battery_record', 
                requiresPermission: 'read',  
                title: 'Riwayat QC Battery'  
            }
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
    return next('/');
  }

  // 4. Cek Akses Modul Dynamic
  const requiredModule = to.meta.module || to.meta.requiresModule;
  
  if (requiredModule) {
    const action = to.meta.requiresPermission || 'read';
    
    // Cek ke Pinia Store
    if (!authStore.can(requiredModule, action)) {
      alert(`⛔ AKSES DITOLAK\n\nAnda tidak memiliki izin '${action}' untuk modul '${requiredModule}'.`);
      return next('/');
    }
  }

  next();
});

export default router;