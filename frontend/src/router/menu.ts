export interface MenuItem {
  label: string;
  icon: string;
  to?: string;
  children?: MenuItem[];
  adminOnly?: boolean; 
  moduleName?: string;
}

export const menuItems: MenuItem[] = [
  {
    label: 'Dashboard',
    icon: '📊',
    to: '/'
  },
  {
    label: 'Master Data',
    icon: '🗄️',
    children: [
      {
        label: 'Product & Vehicle',
        to: '/product-master',
        icon: '📦',
        moduleName: 'product_master' 
      }
    ]
  },
  
  // TRACEABILITY
  {
    label: 'Traceability Config',
    icon: '🔗',
    children: [
        { label: 'Rules Engine', to: '/traceability/rules', icon: '📏', moduleName: 'traceability' },
        { label: 'Part Master', to: '/traceability/parts', icon: '⚙️', moduleName: 'traceability' },
        { label: 'BOM Versioning', to: '/traceability/bom', icon: '📑', moduleName: 'traceability' },
    ]
  },

  // --- [BARU] PRODUCTION ENGINEERING ---
  {
    label: 'Production Eng.',
    icon: '🏭',
    children: [
        { 
            label: 'Layout & Station', 
            to: '/production/layout', 
            icon: '📍', 
            moduleName: 'production_master' 
        },
        { 
            label: 'Route & Process', 
            to: '/production/routes', 
            icon: '🗺️', 
            moduleName: 'production_master' 
        },
    ]
  },
  {
    label: 'PPIC & Order',
    icon: '📅',
    children: [
        { 
            label: 'Monthly Plan', 
            to: '/production/plans', 
            icon: '📊', 
            moduleName: 'production_ppic' 
        },
        { 
            label: 'Daily Order (SPK)', 
            to: '/production/orders', 
            icon: '📝', 
            moduleName: 'production_ppic' 
        },
    ]
},
{
    label: 'SHOP FLOOR MODE',
    to: '/shop-floor/login',
    icon: '🏭',
    // Tidak ada moduleName khusus, atau bisa pakai 'production_operator'
},

  // QC EXECUTION
  {
    label: 'Quality Control',
    icon: '✅',
    children: [
        { label: 'QC Workstation', to: '/qc/station', icon: '🛡️', moduleName: 'qc' },
        { label: 'Riwayat QC', to: '/qc/history', icon: '📜', moduleName: 'qc' },
        // Battery QC (Legacy) digabung disini agar rapi
        { label: 'Battery Check', to: '/battery-qc', icon: '🔋', moduleName: 'battery_record' },
        { label: 'Battery History', to: '/battery-qc/list', icon: '📋', moduleName: 'battery_record' }
    ]
  },
  
  // VIN ADMINISTRATION
  {
    label: 'VIN Administration',
    icon: '🚗',
    children: [
      { label: 'VIN Generation', to: '/vin-record/create', icon: '➕', moduleName: 'vin_record' },
      { label: 'Data History', to: '/vin-record/list', icon: '📋', moduleName: 'vin_record' },
      { label: 'Master Config', to: '/vin-record/master', icon: '⚙️', moduleName: 'vin_master' }
    ]
  },

  // ADMIN
  {
    label: 'Administrator',
    icon: '🛡️',
    adminOnly: true,
    children: [
      { label: 'User & Roles', to: '/admin/roles', icon: '👥' },
      { label: 'Label Designer', to: '/admin/label-designer', icon: '🎨' }
    ]
  }
];