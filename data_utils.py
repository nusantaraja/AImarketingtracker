import os
import yaml
import shutil
import datetime

# Fungsi untuk membuat backup data
def backup_data():
    """
    Membuat backup dari seluruh file database YAML
    """
    # Direktori data dan backup
    data_dir = os.path.join(os.getcwd(), "data")
    backup_dir = os.path.join(os.getcwd(), "backup")
    
    # Buat direktori backup jika belum ada
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Timestamp untuk nama folder backup
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_folder = os.path.join(backup_dir, f"backup_{timestamp}")
    os.makedirs(backup_folder)
    
    # Salin semua file YAML ke folder backup
    for filename in os.listdir(data_dir):
        if filename.endswith(".yaml"):
            src_file = os.path.join(data_dir, filename)
            dst_file = os.path.join(backup_folder, filename)
            shutil.copy2(src_file, dst_file)
    
    return backup_folder

# Fungsi untuk memulihkan data dari backup
def restore_data(backup_folder):
    """
    Memulihkan data dari folder backup yang ditentukan
    """
    # Direktori data
    data_dir = os.path.join(os.getcwd(), "data")
    
    # Pastikan folder backup ada
    if not os.path.exists(backup_folder):
        return False, f"Folder backup {backup_folder} tidak ditemukan"
    
    # Salin semua file YAML dari folder backup ke direktori data
    for filename in os.listdir(backup_folder):
        if filename.endswith(".yaml"):
            src_file = os.path.join(backup_folder, filename)
            dst_file = os.path.join(data_dir, filename)
            shutil.copy2(src_file, dst_file)
    
    return True, "Data berhasil dipulihkan"

# Fungsi untuk ekspor data ke CSV
def export_to_csv(data, filename):
    """
    Mengekspor data ke file CSV
    """
    import pandas as pd
    
    # Konversi data ke DataFrame
    df = pd.DataFrame(data)
    
    # Simpan ke file CSV
    csv_file = os.path.join(os.getcwd(), "exports", filename)
    
    # Buat direktori exports jika belum ada
    exports_dir = os.path.join(os.getcwd(), "exports")
    if not os.path.exists(exports_dir):
        os.makedirs(exports_dir)
    
    df.to_csv(csv_file, index=False)
    
    return csv_file

# Fungsi untuk validasi integritas data
def validate_data_integrity():
    """
    Memvalidasi integritas data di seluruh file YAML
    """
    # Direktori data
    data_dir = os.path.join(os.getcwd(), "data")
    
    # Daftar file yang harus ada
    required_files = ["users.yaml", "marketing_activities.yaml", "followups.yaml", "config.yaml"]
    
    # Periksa keberadaan file
    missing_files = []
    for filename in required_files:
        file_path = os.path.join(data_dir, filename)
        if not os.path.exists(file_path):
            missing_files.append(filename)
    
    if missing_files:
        return False, f"File berikut tidak ditemukan: {', '.join(missing_files)}"
    
    # Periksa struktur data
    try:
        # Users
        users_file = os.path.join(data_dir, "users.yaml")
        with open(users_file, 'r') as file:
            users_data = yaml.safe_load(file)
        
        if not users_data or "users" not in users_data:
            return False, "Struktur data users.yaml tidak valid"
        
        # Activities
        activities_file = os.path.join(data_dir, "marketing_activities.yaml")
        with open(activities_file, 'r') as file:
            activities_data = yaml.safe_load(file)
        
        if not activities_data or "activities" not in activities_data:
            return False, "Struktur data marketing_activities.yaml tidak valid"
        
        # Followups
        followups_file = os.path.join(data_dir, "followups.yaml")
        with open(followups_file, 'r') as file:
            followups_data = yaml.safe_load(file)
        
        if not followups_data or "followups" not in followups_data:
            return False, "Struktur data followups.yaml tidak valid"
        
        # Config
        config_file = os.path.join(data_dir, "config.yaml")
        with open(config_file, 'r') as file:
            config_data = yaml.safe_load(file)
        
        if not config_data or "app_settings" not in config_data or "notification_settings" not in config_data:
            return False, "Struktur data config.yaml tidak valid"
        
        return True, "Integritas data valid"
    
    except Exception as e:
        return False, f"Error saat memvalidasi data: {str(e)}"

# Fungsi untuk sinkronisasi dengan GitHub
def prepare_for_github_sync():
    """
    Menyiapkan file-file untuk sinkronisasi dengan GitHub
    """
    # Buat file .gitignore
    gitignore_content = """
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
dist/
build/
*.egg-info/

# Virtual environments
venv/
env/
ENV/

# Local development settings
.env

# Backup files
backup/

# Streamlit specific
.streamlit/secrets.toml

# Exports
exports/
"""
    
    gitignore_file = os.path.join(os.getcwd(), ".gitignore")
    with open(gitignore_file, 'w') as file:
        file.write(gitignore_content)
    
    # Buat README.md
    readme_content = """# AI Suara Marketing Tracker

Aplikasi untuk mencatat dan memonitor aktivitas harian pemasaran AI Suara dari para Marketing.

## Fitur

- Sistem autentikasi dengan perbedaan akses antara superadmin dan marketing team
- Pencatatan aktivitas pemasaran (nama pemasar, nama prospek, lokasi)
- Pencatatan progress/follow-up
- Dashboard analitik untuk monitoring performa
- Penyimpanan data permanen
- Tampilan responsif untuk desktop dan mobile

## Cara Penggunaan

1. Clone repositori ini
2. Install dependensi dengan `pip install -r requirements.txt`
3. Jalankan aplikasi dengan `streamlit run app.py`

## Deployment

Aplikasi ini dapat di-deploy di Streamlit Cloud dengan mengikuti langkah-langkah berikut:

1. Fork repositori ini ke akun GitHub Anda
2. Buat akun di [Streamlit Cloud](https://streamlit.io/cloud)
3. Deploy aplikasi dengan menghubungkan ke repositori GitHub Anda

## Struktur Direktori

- `app.py`: File utama aplikasi Streamlit
- `utils.py`: Fungsi-fungsi utilitas untuk aplikasi
- `data_utils.py`: Fungsi-fungsi untuk manajemen data
- `data/`: Direktori untuk menyimpan file database YAML
- `backup/`: Direktori untuk backup data
- `exports/`: Direktori untuk file ekspor

## Kredit

Dibuat oleh [Nama Anda] untuk [Nama Perusahaan]
"""
    
    readme_file = os.path.join(os.getcwd(), "README.md")
    with open(readme_file, 'w') as file:
        file.write(readme_content)
    
    return True, "File untuk sinkronisasi GitHub berhasil disiapkan"
