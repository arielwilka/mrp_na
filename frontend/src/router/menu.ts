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
  
  // 2. TRACEABILITY (Dipisah menjadi menu utama sendiri)
  {
    label: 'Traceability Config',
    icon: '🔗',
    // Sekarang dia ada di Level 1, anak-anaknya di Level 2 (Aman)
    children: [
        { 
             label: 'Rules Engine', 
             to: '/traceability/rules', 
             icon: '📏',
             moduleName: 'traceability' 
        },
        { 
             label: 'Part Master', 
             to: '/traceability/parts', 
             icon: '⚙️',
             moduleName: 'traceability' 
        },
        { 
             label: 'BOM Versioning', 
             to: '/traceability/bom', 
             icon: '📑',
             moduleName: 'traceability' 
        },
    ]
  },
  // 3. QUALITY CONTROL (TRANSAKSI) - [UPDATED]
  {
    label: 'Quality Control',
    icon: '✅',
    children: [
        {
            label: 'QC Workstation',  // Halaman Operator
            to: '/qc/station',
            icon: '🛡️',
            // Module name 'qc' sesuai dengan backend app dan permission
            moduleName: 'qc' 
        },
        {
            label: 'Riwayat QC',
            to: '/qc/history',
            icon: '📜',
            moduleName: 'qc'
        }
        // (Opsional: Jika nanti Anda buat halaman history log QC)
        /*
        {
            label: 'Inspection History',
            to: '/qc/history',
            icon: '📜',
            moduleName: 'qc'
        }
        */
    ]
  },
  
  // --- MODUL VIN (Combined Group) ---
  {
    label: 'VIN Administration', // Ganti nama jadi lebih umum
    icon: '🚗',
    // PENTING: Jangan pasang moduleName di sini agar parent selalu muncul
    // (atau Sidebar logic Anda harus pintar mengecek 'jika salah satu anak visible')
    children: [
      {
        label: 'VIN Generation', // Operasional
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
  {
    label: 'Quality Control',
    icon: '✅',
    // Parent tidak perlu moduleName, karena Sidebar Anda otomatis
    // menyembunyikan parent jika semua children ter-filter (hidden).
    children: [
        {
            label: 'Battery Check',
            to: '/battery-qc',
            icon: '🔋',
            // Menu ini hanya muncul jika user punya izin 'battery_record.read'
            moduleName: 'battery_record' 
        },
        {
            label: 'Riwayat QC',
            to: '/battery-qc/list',
            icon: '📜',
            moduleName: 'battery_record'
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