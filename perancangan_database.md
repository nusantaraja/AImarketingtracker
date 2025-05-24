# Perancangan Struktur Database dan Fitur Aplikasi

## Struktur Database

Untuk aplikasi monitoring aktivitas pemasaran AI Suara, kita akan menggunakan pendekatan penyimpanan berbasis file YAML yang disinkronkan dengan GitHub. Struktur database akan terdiri dari beberapa file YAML yang menyimpan data berbeda:

### 1. Database Pengguna (`users.yaml`)

```yaml
users:
  - username: admin
    password_hash: $2b$12$...  # Hash bcrypt dari password
    name: "Admin Utama"
    role: "superadmin"
    email: "admin@example.com"
    created_at: "2025-05-24 13:00:00"
    
  - username: marketing1
    password_hash: $2b$12$...  # Hash bcrypt dari password
    name: "Marketing Satu"
    role: "marketing"
    email: "marketing1@example.com"
    created_at: "2025-05-24 13:30:00"
```

### 2. Database Aktivitas Pemasaran (`marketing_activities.yaml`)

```yaml
activities:
  - id: "act-001"
    marketer_username: "marketing1"
    prospect_name: "PT Teknologi Maju"
    prospect_location: "Jakarta Selatan"
    contact_person: "Budi Santoso"
    contact_position: "IT Manager"
    contact_phone: "08123456789"
    contact_email: "budi@teknologimaju.com"
    activity_date: "2025-05-20 10:00:00"
    activity_type: "Presentasi"
    description: "Presentasi fitur AI Suara untuk sistem call center"
    status: "dalam_proses"
    created_at: "2025-05-19 15:30:00"
    updated_at: "2025-05-20 14:00:00"
    
  - id: "act-002"
    marketer_username: "marketing2"
    prospect_name: "CV Mitra Sejahtera"
    prospect_location: "Bandung"
    contact_person: "Siti Aminah"
    contact_position: "Direktur"
    contact_phone: "08789012345"
    contact_email: "siti@mitrasejahtera.com"
    activity_date: "2025-05-21 13:30:00"
    activity_type: "Demo Produk"
    description: "Demo AI Suara untuk sistem pengumuman internal"
    status: "baru"
    created_at: "2025-05-18 09:15:00"
    updated_at: "2025-05-18 09:15:00"
```

### 3. Database Progress/Follow-up (`followups.yaml`)

```yaml
followups:
  - id: "fu-001"
    activity_id: "act-001"
    marketer_username: "marketing1"
    followup_date: "2025-05-22 11:00:00"
    notes: "Klien tertarik dengan fitur pengenalan suara otomatis"
    next_action: "Menyiapkan proposal harga"
    next_followup_date: "2025-05-25 14:00:00"
    interest_level: 4  # Skala 1-5
    status_update: "dalam_proses"
    created_at: "2025-05-22 13:45:00"
    
  - id: "fu-002"
    activity_id: "act-001"
    marketer_username: "marketing1"
    followup_date: "2025-05-25 14:30:00"
    notes: "Proposal telah dikirim, klien sedang mempertimbangkan"
    next_action: "Menghubungi kembali untuk konfirmasi"
    next_followup_date: "2025-05-28 10:00:00"
    interest_level: 4  # Skala 1-5
    status_update: "dalam_proses"
    created_at: "2025-05-25 16:20:00"
```

### 4. Database Konfigurasi Aplikasi (`config.yaml`)

```yaml
app_settings:
  app_name: "AI Suara Marketing Tracker"
  version: "1.0.0"
  theme: "light"
  date_format: "%Y-%m-%d %H:%M:%S"
  
notification_settings:
  enable_email: false
  enable_reminder: true
  reminder_days_before: 1
```

## Skema Data

### 1. Skema Pengguna
- **username**: String (primary key) - Nama pengguna untuk login
- **password_hash**: String - Hash bcrypt dari password
- **name**: String - Nama lengkap pengguna
- **role**: String - Peran pengguna ("superadmin" atau "marketing")
- **email**: String - Alamat email pengguna
- **created_at**: Datetime - Waktu pembuatan akun

### 2. Skema Aktivitas Pemasaran
- **id**: String (primary key) - ID unik aktivitas
- **marketer_username**: String (foreign key) - Username marketing yang melakukan aktivitas
- **prospect_name**: String - Nama prospek/perusahaan
- **prospect_location**: String - Lokasi prospek
- **contact_person**: String - Nama kontak person
- **contact_position**: String - Jabatan kontak person
- **contact_phone**: String - Nomor telepon kontak
- **contact_email**: String - Email kontak
- **activity_date**: Datetime - Tanggal dan waktu aktivitas
- **activity_type**: String - Jenis aktivitas (Presentasi, Demo, Follow-up call, dll)
- **description**: String - Deskripsi aktivitas
- **status**: String - Status prospek ("baru", "dalam_proses", "berhasil", "gagal")
- **created_at**: Datetime - Waktu pencatatan aktivitas
- **updated_at**: Datetime - Waktu pembaruan terakhir

### 3. Skema Progress/Follow-up
- **id**: String (primary key) - ID unik follow-up
- **activity_id**: String (foreign key) - ID aktivitas yang di-follow-up
- **marketer_username**: String (foreign key) - Username marketing yang melakukan follow-up
- **followup_date**: Datetime - Tanggal dan waktu follow-up
- **notes**: String - Catatan hasil follow-up
- **next_action**: String - Rencana tindak lanjut berikutnya
- **next_followup_date**: Datetime - Jadwal follow-up berikutnya
- **interest_level**: Integer - Tingkat ketertarikan prospek (skala 1-5)
- **status_update**: String - Pembaruan status prospek
- **created_at**: Datetime - Waktu pencatatan follow-up

## Definisi Hak Akses

### Superadmin
- Melihat seluruh data aktivitas pemasaran dari semua marketing
- Melihat seluruh data follow-up dari semua marketing
- Menambah, mengedit, dan menghapus data pengguna
- Mengakses dashboard analitik komprehensif
- Mengekspor data ke format CSV/Excel
- Mengubah konfigurasi aplikasi
- Melihat log aktivitas pengguna

### Marketing Team
- Melihat data aktivitas pemasaran miliknya sendiri
- Menambah dan mengedit data aktivitas pemasaran miliknya sendiri
- Melihat data follow-up untuk aktivitas pemasaran miliknya sendiri
- Menambah dan mengedit data follow-up untuk aktivitas pemasaran miliknya sendiri
- Melihat dashboard analitik terbatas untuk data miliknya sendiri
- Mengekspor data miliknya sendiri ke format CSV/Excel
- Mengubah profil dan password miliknya sendiri

## Struktur Fitur Aplikasi

### 1. Sistem Autentikasi
- Halaman login dengan validasi username dan password
- Enkripsi password menggunakan bcrypt
- Manajemen sesi menggunakan Streamlit session state
- Halaman reset password (opsional)

### 2. Dashboard
- **Dashboard Superadmin**:
  - Ringkasan jumlah aktivitas pemasaran per marketing
  - Grafik tren aktivitas pemasaran per waktu
  - Distribusi status prospek (baru, dalam proses, berhasil, gagal)
  - Peta lokasi prospek
  - Daftar follow-up yang akan datang
  - Performa marketing team (konversi, jumlah prospek, dll)

- **Dashboard Marketing**:
  - Ringkasan aktivitas pemasaran pribadi
  - Grafik tren aktivitas pemasaran pribadi per waktu
  - Distribusi status prospek pribadi
  - Daftar follow-up pribadi yang akan datang

### 3. Manajemen Aktivitas Pemasaran
- Form input aktivitas pemasaran baru
- Daftar aktivitas pemasaran dengan filter dan pencarian
- Halaman detail aktivitas pemasaran
- Form edit aktivitas pemasaran

### 4. Manajemen Follow-up
- Form input follow-up baru
- Daftar follow-up dengan filter dan pencarian
- Timeline follow-up untuk setiap aktivitas pemasaran
- Pengingat follow-up yang akan datang

### 5. Manajemen Pengguna (Superadmin)
- Form tambah pengguna baru
- Daftar pengguna dengan filter dan pencarian
- Form edit pengguna
- Fitur reset password

### 6. Ekspor dan Impor Data
- Ekspor data ke format CSV/Excel
- Impor data dari file CSV/Excel (opsional)

### 7. Pengaturan Aplikasi (Superadmin)
- Konfigurasi umum aplikasi
- Pengaturan notifikasi
- Manajemen backup data

## Kesimpulan

Perancangan struktur database dan fitur aplikasi monitoring aktivitas pemasaran AI Suara telah disusun dengan mempertimbangkan kebutuhan pengguna dan persyaratan teknis. Struktur database berbasis file YAML dengan sinkronisasi GitHub dipilih untuk memudahkan deployment di Streamlit. Skema data dirancang untuk mendukung pencatatan aktivitas pemasaran, follow-up, dan manajemen pengguna dengan hak akses yang berbeda untuk superadmin dan marketing team. Fitur-fitur aplikasi dirancang untuk memberikan pengalaman pengguna yang optimal dengan dashboard yang informatif, form input yang intuitif, dan visualisasi data yang menarik.
