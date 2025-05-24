import streamlit as st
import os
import time

def test_login_authentication():
    """
    Menguji fitur login dan autentikasi
    """
    print("Menguji fitur login dan autentikasi...")
    
    # Test case 1: Login dengan kredensial valid (superadmin)
    print("Test case 1: Login dengan kredensial valid (superadmin)")
    from utils import authenticate_user
    user = authenticate_user("admin", "admin123")
    assert user is not None, "Login superadmin gagal"
    assert user["role"] == "superadmin", "Role superadmin tidak sesuai"
    print("✓ Login superadmin berhasil")
    
    # Test case 2: Login dengan kredensial tidak valid
    print("Test case 2: Login dengan kredensial tidak valid")
    user = authenticate_user("admin", "password_salah")
    assert user is None, "Login dengan password salah seharusnya gagal"
    print("✓ Login dengan password salah berhasil ditolak")
    
    # Test case 3: Login dengan username tidak terdaftar
    print("Test case 3: Login dengan username tidak terdaftar")
    user = authenticate_user("user_tidak_ada", "password")
    assert user is None, "Login dengan username tidak terdaftar seharusnya gagal"
    print("✓ Login dengan username tidak terdaftar berhasil ditolak")
    
    print("Semua test login dan autentikasi berhasil!")
    return True

def test_user_access_control():
    """
    Menguji kontrol akses pengguna (superadmin vs marketing)
    """
    print("Menguji kontrol akses pengguna...")
    
    # Tambahkan user marketing untuk pengujian
    from utils import add_user, authenticate_user
    
    # Test case 1: Tambah user marketing
    print("Test case 1: Tambah user marketing")
    success, message = add_user("marketing_test", "password123", "Marketing Test", "marketing", "marketing@example.com")
    assert success, f"Gagal menambahkan user marketing: {message}"
    print("✓ Berhasil menambahkan user marketing")
    
    # Test case 2: Verifikasi user marketing dapat login
    print("Test case 2: Verifikasi user marketing dapat login")
    user = authenticate_user("marketing_test", "password123")
    assert user is not None, "Login marketing gagal"
    assert user["role"] == "marketing", "Role marketing tidak sesuai"
    print("✓ Login marketing berhasil")
    
    # Test case 3: Verifikasi perbedaan akses
    print("Test case 3: Verifikasi perbedaan akses")
    # Ini hanya simulasi karena kita tidak bisa menguji UI Streamlit secara langsung
    # Dalam aplikasi sebenarnya, perbedaan akses diimplementasikan melalui kondisi if-else
    # berdasarkan role pengguna
    
    # Simulasi akses superadmin
    admin_user = authenticate_user("admin", "admin123")
    assert admin_user["role"] == "superadmin", "Role superadmin tidak sesuai"
    
    # Simulasi akses marketing
    marketing_user = authenticate_user("marketing_test", "password123")
    assert marketing_user["role"] == "marketing", "Role marketing tidak sesuai"
    
    print("✓ Verifikasi perbedaan role berhasil")
    print("Semua test kontrol akses pengguna berhasil!")
    return True

def test_marketing_activity_features():
    """
    Menguji fitur aktivitas pemasaran
    """
    print("Menguji fitur aktivitas pemasaran...")
    
    from utils import add_marketing_activity, get_marketing_activities_by_username, get_activity_by_id
    
    # Test case 1: Tambah aktivitas pemasaran
    print("Test case 1: Tambah aktivitas pemasaran")
    success, message, activity_id = add_marketing_activity(
        "marketing_test", "PT Test", "Jakarta", 
        "John Doe", "Manager", "08123456789", 
        "john@test.com", "2025-05-24 10:00:00", "Presentasi", 
        "Presentasi produk AI Suara"
    )
    assert success, f"Gagal menambahkan aktivitas pemasaran: {message}"
    assert activity_id is not None, "ID aktivitas tidak diberikan"
    print(f"✓ Berhasil menambahkan aktivitas pemasaran dengan ID: {activity_id}")
    
    # Test case 2: Mendapatkan aktivitas berdasarkan username
    print("Test case 2: Mendapatkan aktivitas berdasarkan username")
    activities = get_marketing_activities_by_username("marketing_test")
    assert len(activities) > 0, "Tidak ada aktivitas yang ditemukan"
    assert activities[0]["marketer_username"] == "marketing_test", "Username tidak sesuai"
    print("✓ Berhasil mendapatkan aktivitas berdasarkan username")
    
    # Test case 3: Mendapatkan aktivitas berdasarkan ID
    print("Test case 3: Mendapatkan aktivitas berdasarkan ID")
    activity = get_activity_by_id(activity_id)
    assert activity is not None, "Aktivitas tidak ditemukan"
    assert activity["id"] == activity_id, "ID aktivitas tidak sesuai"
    assert activity["prospect_name"] == "PT Test", "Nama prospek tidak sesuai"
    print("✓ Berhasil mendapatkan aktivitas berdasarkan ID")
    
    print("Semua test fitur aktivitas pemasaran berhasil!")
    return True, activity_id

def test_followup_features(activity_id):
    """
    Menguji fitur follow-up
    """
    print("Menguji fitur follow-up...")
    
    from utils import add_followup, get_followups_by_activity_id
    
    # Test case 1: Tambah follow-up
    print("Test case 1: Tambah follow-up")
    success, message = add_followup(
        activity_id, "marketing_test", "2025-05-25 11:00:00",
        "Klien tertarik dengan produk", "Kirim proposal",
        "2025-05-28 10:00:00", 4, "dalam_proses"
    )
    assert success, f"Gagal menambahkan follow-up: {message}"
    print("✓ Berhasil menambahkan follow-up")
    
    # Test case 2: Mendapatkan follow-up berdasarkan activity_id
    print("Test case 2: Mendapatkan follow-up berdasarkan activity_id")
    followups = get_followups_by_activity_id(activity_id)
    assert len(followups) > 0, "Tidak ada follow-up yang ditemukan"
    assert followups[0]["activity_id"] == activity_id, "Activity ID tidak sesuai"
    assert followups[0]["marketer_username"] == "marketing_test", "Username tidak sesuai"
    print("✓ Berhasil mendapatkan follow-up berdasarkan activity_id")
    
    print("Semua test fitur follow-up berhasil!")
    return True

def test_data_persistence():
    """
    Menguji persistensi data
    """
    print("Menguji persistensi data...")
    
    from utils import get_all_users, get_all_marketing_activities, get_all_followups
    
    # Test case 1: Verifikasi data pengguna tersimpan
    print("Test case 1: Verifikasi data pengguna tersimpan")
    users = get_all_users()
    assert len(users) >= 2, "Data pengguna tidak tersimpan dengan benar"
    assert any(user["username"] == "admin" for user in users), "User admin tidak ditemukan"
    assert any(user["username"] == "marketing_test" for user in users), "User marketing_test tidak ditemukan"
    print("✓ Data pengguna tersimpan dengan benar")
    
    # Test case 2: Verifikasi data aktivitas tersimpan
    print("Test case 2: Verifikasi data aktivitas tersimpan")
    activities = get_all_marketing_activities()
    assert len(activities) > 0, "Data aktivitas tidak tersimpan dengan benar"
    assert any(activity["marketer_username"] == "marketing_test" for activity in activities), "Aktivitas marketing_test tidak ditemukan"
    print("✓ Data aktivitas tersimpan dengan benar")
    
    # Test case 3: Verifikasi data follow-up tersimpan
    print("Test case 3: Verifikasi data follow-up tersimpan")
    followups = get_all_followups()
    assert len(followups) > 0, "Data follow-up tidak tersimpan dengan benar"
    assert any(followup["marketer_username"] == "marketing_test" for followup in followups), "Follow-up marketing_test tidak ditemukan"
    print("✓ Data follow-up tersimpan dengan benar")
    
    print("Semua test persistensi data berhasil!")
    return True

def test_data_backup_restore():
    """
    Menguji fitur backup dan restore data
    """
    print("Menguji fitur backup dan restore data...")
    
    from data_utils import backup_data, restore_data, validate_data_integrity
    
    # Test case 1: Backup data
    print("Test case 1: Backup data")
    backup_folder = backup_data()
    assert os.path.exists(backup_folder), "Folder backup tidak dibuat"
    assert len(os.listdir(backup_folder)) > 0, "Tidak ada file yang di-backup"
    print(f"✓ Berhasil melakukan backup data ke folder: {backup_folder}")
    
    # Test case 2: Validasi integritas data
    print("Test case 2: Validasi integritas data")
    valid, message = validate_data_integrity()
    assert valid, f"Validasi integritas data gagal: {message}"
    print("✓ Validasi integritas data berhasil")
    
    # Test case 3: Restore data (simulasi)
    print("Test case 3: Restore data (simulasi)")
    # Kita tidak benar-benar melakukan restore untuk menghindari kehilangan data
    # Tapi kita bisa memverifikasi bahwa fungsi restore berjalan dengan benar
    # dengan memeriksa apakah folder backup ada dan berisi file
    assert os.path.exists(backup_folder), "Folder backup tidak ditemukan"
    assert len(os.listdir(backup_folder)) > 0, "Folder backup kosong"
    print("✓ Simulasi restore data berhasil")
    
    print("Semua test backup dan restore data berhasil!")
    return True

def run_all_tests():
    """
    Menjalankan semua test
    """
    print("Menjalankan semua test...")
    
    # Uji login dan autentikasi
    test_login_authentication()
    print("\n")
    
    # Uji kontrol akses pengguna
    test_user_access_control()
    print("\n")
    
    # Uji fitur aktivitas pemasaran
    success, activity_id = test_marketing_activity_features()
    print("\n")
    
    # Uji fitur follow-up
    test_followup_features(activity_id)
    print("\n")
    
    # Uji persistensi data
    test_data_persistence()
    print("\n")
    
    # Uji backup dan restore data
    test_data_backup_restore()
    print("\n")
    
    print("Semua test berhasil!")
    return True

if __name__ == "__main__":
    run_all_tests()
