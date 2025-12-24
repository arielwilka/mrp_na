export interface MenuItem {
  label: string;
  icon: string;
  to?: string;
  children?: MenuItem[];
  adminOnly?: boolean; 
  moduleName?: string; // Kunci akses (bisa di Parent atau Child)
}

export const menuItems: MenuItem[] = [
  {
    label: 'Dashboard',
    icon: '📊',
    to: '/'
  },
  
  // --- MODUL VIN (Combined Group) ---
  {
    label: 'VIN System', // Ganti nama jadi lebih umum
    icon: '🚗',
    // PENTING: Jangan pasang moduleName di sini agar parent selalu muncul
    // (atau Sidebar logic Anda harus pintar mengecek 'jika salah satu anak visible')
    children: [
      {
        label: 'Input Produksi', // Operasional
        to: '/vin-record/create',
        icon: '➕',
        moduleName: 'vin_record' // <--- Khusus Staff Produksi
      },
      {
        label: 'Data History', // Operasional
        to: '/vin-record/list',
        icon: '📋',
        moduleName: 'vin_record' // <--- Khusus Staff Produksi
      },
      {
        label: 'Master Config', // Configuration
        to: '/vin-record/master',
        icon: '⚙️',
        moduleName: 'vin_master' // <--- Khusus Engineering/IT
      }
    ]
  },

  // --- MODUL ADMIN (Superuser) ---
  {
    label: 'Administrator',
    icon: '🛡️',
    adminOnly: true, // Khusus Superuser
    children: [
      {
        label: 'User & Roles',
        to: '/admin/roles',
        icon: '👥'
      },
      {
        label: 'Label Designer',
        to: '/admin/label-designer',
        icon: '🎨'
      }
    ]
  }
];