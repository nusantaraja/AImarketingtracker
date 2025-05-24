# Panduan Deployment Aplikasi AI Suara Marketing Tracker di Streamlit Cloud

Dokumen ini berisi panduan langkah demi langkah untuk men-deploy aplikasi AI Suara Marketing Tracker di Streamlit Cloud.

## Prasyarat

1. Akun GitHub
2. Akun Streamlit Cloud (dapat dibuat gratis di [streamlit.io/cloud](https://streamlit.io/cloud))

## Langkah-langkah Deployment

### 1. Persiapkan Repository GitHub

1. Buat repository baru di GitHub
2. Push kode aplikasi ke repository tersebut dengan perintah:
   ```bash
   git remote add origin https://github.com/username/ai-marketing-tracker.git
   git branch -M main
   git push -u origin main
   ```

### 2. Deploy di Streamlit Cloud

1. Login ke [Streamlit Cloud](https://streamlit.io/cloud)
2. Klik tombol "New app"
3. Pilih repository GitHub yang berisi aplikasi AI Marketing Tracker
4. Pada bagian "Main file path", masukkan: `app.py`
5. Klik "Deploy"

### 3. Konfigurasi Tambahan (Opsional)

Jika diperlukan, Anda dapat menambahkan secrets di Streamlit Cloud:
1. Pada halaman aplikasi di Streamlit Cloud, klik "Settings"
2. Scroll ke bagian "Secrets"
3. Tambahkan secrets yang diperlukan (misalnya, untuk kredensial database eksternal)

## Penggunaan Aplikasi

Setelah deployment berhasil, Anda akan mendapatkan URL publik untuk aplikasi Anda. Berikut adalah informasi login default:

- **Superadmin**:
  - Username: admin
  - Password: admin123

- **Marketing Team**:
  - Dapat ditambahkan melalui menu "Manajemen Pengguna" oleh superadmin

## Pemeliharaan Aplikasi

Untuk memperbarui aplikasi yang sudah di-deploy:
1. Lakukan perubahan pada kode lokal
2. Commit dan push perubahan ke GitHub
3. Streamlit Cloud akan otomatis men-deploy ulang aplikasi

## Backup Data

Aplikasi menyimpan data dalam file YAML di direktori `data/`. Untuk memastikan data tidak hilang:
1. Gunakan fitur backup yang tersedia di aplikasi
2. Secara berkala, download file-file YAML dari direktori `data/`

## Troubleshooting

Jika mengalami masalah saat deployment:
1. Periksa log error di Streamlit Cloud
2. Pastikan semua dependensi tercantum di `requirements.txt`
3. Verifikasi struktur direktori aplikasi sesuai dengan yang diharapkan

## Kontak

Jika memerlukan bantuan lebih lanjut, silakan hubungi tim pengembang di [email@example.com]
