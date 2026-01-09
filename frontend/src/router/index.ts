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

// Product Module
import ProductMasterPage from '../modules/product/views/ProductMasterPage.vue';

// Battery Record Module
import BatteryQCPage from '../modules/battery_record/views/BatteryQCPage.vue';
import BatteryHistoryPage from '../modules/battery_record/views/BatteryHistoryPage.vue';

// Admin Module
import LabelDesigner from '../modules/admin/views/LabelDesigner.vue';
import RoleManager from '../modules/admin/views/RoleManager.vue';

// Traceability Module
import RuleList from '../modules/traceability/views/RuleList.vue';
import RuleForm from '../modules/traceability/views/RuleForm.vue';
import PartList from '../modules/traceability/views/PartList.vue';
import PartForm from '../modules/traceability/views/PartForm.vue';
import BOMList from '../modules/traceability/views/BOMList.vue';
import BOMForm from '../modules/traceability/views/BOMForm.vue';
import PartTemplate from '../modules/traceability/views/PartTemplate.vue';

// QC Module
import QCStation from '../modules/qc/views/QCStation.vue';
import QCList from '../modules/qc/views/QCList.vue';

// --- [BARU] PRODUCTION MODULE ---
import WorkCenterPage from '../modules/production/views/WorkCenterPage.vue';
import RouteManagerPage from '../modules/production/views/RouteManagerPage.vue';
import ProductionPlanPage from '../modules/production/views/ProductionPlanPage.vue';
import ProductionOrderPage from '../modules/production/views/ProductionOrderPage.vue';

import StationLogin from '../modules/production/views/StationLogin.vue';
import ShopFloorInterface from '../modules/production/views/ShopFloorInterface.vue';

// --- DEFINISI META DATA ---
declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean;
    requiresGuest?: boolean;
    requiresSuperuser?: boolean;
    module?: string; 
    requiresModule?: string;    
    requiresPermission?: 'read' | 'create' | 'delete'; 
  }
}

// --- DUMMY COMPONENT ---
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
  {
    path: '/shop-floor/login',
    name: 'StationLogin',
    component: StationLogin,
    meta: { requiresAuth: true, title: 'Station Login' }
  },
  {
      path: '/shop-floor/workspace',
      name: 'ShopFloorInterface',
      component: ShopFloorInterface,
      meta: { requiresAuth: true, title: 'Operator Workspace' }
  },

  // 2. PROTECTED ROUTES
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

      // --- PRODUCT MASTER ---
      {
        path: 'product-master', 
        name: 'ProductMaster',
        component: ProductMasterPage,
        meta: { module: 'product_master', requiresPermission: 'read' }
      },

      // --- TRACEABILITY ---
      {
        path: 'traceability',
        component: EmptyRouterView,
        children: [
          // Rules
          { path: 'rules', name: 'RuleList', component: RuleList, meta: { module: 'traceability', requiresPermission: 'read' } },
          { path: 'rules/create', name: 'RuleCreate', component: RuleForm, meta: { module: 'traceability', requiresPermission: 'create' } },
          { path: 'rules/:id/edit', name: 'RuleEdit', component: RuleForm, props: true, meta: { module: 'traceability', requiresPermission: 'create' } },
          // Parts
          { path: 'parts', name: 'PartList', component: PartList, meta: { module: 'traceability', requiresPermission: 'read' } },
          { path: 'parts/create', name: 'PartCreate', component: PartForm, meta: { module: 'traceability', requiresPermission: 'create' } },
          { path: 'parts/:id/edit', name: 'PartEdit', component: PartForm, props: true, meta: { module: 'traceability', requiresPermission: 'create' } },
          { path: 'parts/:id/template', name: 'PartTemplate', component: PartTemplate, props: true, meta: { module: 'traceability', requiresPermission: 'create' } },
          // BOM
          { path: 'bom', name: 'BOMList', component: BOMList, meta: { module: 'traceability', requiresPermission: 'read' } },
          { path: 'bom/create', name: 'BOMCreate', component: BOMForm, meta: { module: 'traceability', requiresPermission: 'create' } },
          { path: 'bom/:id/edit', name: 'BOMEdit', component: BOMForm, props: true, meta: { module: 'traceability', requiresPermission: 'create' } }
        ]
      },

      // --- [BARU] PRODUCTION SYSTEM (ENGINEERING) ---
      {
        path: 'production',
        component: EmptyRouterView,
        children: [
            {
                path: 'layout', // URL: /production/layout
                name: 'ProdLayout',
                component: WorkCenterPage,
                meta: { module: 'production_master', requiresPermission: 'read' }
            },
            {
                path: 'routes', // URL: /production/routes
                name: 'ProdRoutes',
                component: RouteManagerPage,
                meta: { module: 'production_master', requiresPermission: 'read' }
            },
            { 
            path: 'plans', // URL: /production/plans
            name: 'ProdPlans', 
            component: ProductionPlanPage, 
            meta: { module: 'production_ppic', requiresPermission: 'read' } 
        },
        { 
            path: 'orders', // URL: /production/orders
            name: 'ProdOrders', 
            component: ProductionOrderPage, 
            meta: { module: 'production_ppic', requiresPermission: 'create' } 
        }
        ]
      },

      // --- QUALITY CONTROL ---
      {
        path: 'qc',
        component: EmptyRouterView,
        children: [
          { path: 'station', name: 'QCStation', component: QCStation, meta: { module: 'qc', requiresPermission: 'create' } },
          { path: 'history', name: 'QCList', component: QCList, meta: { module: 'qc', requiresPermission: 'read' } }
        ]
      },

      // --- VIN RECORD ---
      {
        path: 'vin-record',
        component: EmptyRouterView, 
        children: [
          { path: '', redirect: 'list' },
          { path: 'list', name: 'VinList', component: VinListPage, meta: { module: 'vin_record', requiresPermission: 'read' } },
          { path: 'create', name: 'VinCreate', component: VinCreatePage, meta: { module: 'vin_record', requiresPermission: 'create' } },
          { path: 'master', name: 'VinMaster', component: VinMasterPage, meta: { module: 'vin_master', requiresPermission: 'read' } }
        ]
      },
      
      // --- BATTERY RECORD ---
      {
        path: 'battery-qc',
        component: EmptyRouterView, 
        children: [
          { path: '', name: 'BatteryQC', component: BatteryQCPage, meta: { module: 'battery_record', requiresPermission: 'read' } },
          { path: 'list', name: 'BatteryList', component: BatteryHistoryPage, meta: { module: 'battery_record', requiresPermission: 'read' } }
        ]
      },

      // --- ADMIN ---
      {
        path: 'admin',
        component: EmptyRouterView,
        meta: { requiresSuperuser: true },
        children: [
          { path: 'label-designer', name: 'LabelDesigner', component: LabelDesigner },
          { path: 'roles', name: 'RoleManager', component: RoleManager }
        ]
      }
    ]
  },

  // 3. CATCH ALL
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

// --- MIDDLEWARE ---
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore();

  if (to.matched.some(record => record.meta.requiresAuth) && !authStore.isAuthenticated) return next('/login');
  if (to.meta.requiresGuest && authStore.isAuthenticated) return next('/');
  if (to.matched.some(record => record.meta.requiresSuperuser) && !authStore.isSuperuser) return next('/');

  const requiredModule = to.meta.module || to.meta.requiresModule;
  if (requiredModule) {
    const action = to.meta.requiresPermission || 'read';
    if (!authStore.can(requiredModule, action)) {
      alert(`⛔ AKSES DITOLAK\n\nAnda tidak memiliki izin '${action}' untuk modul '${requiredModule}'.`);
      return next('/');
    }
  }
  next();
});

export default router;