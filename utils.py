import yaml
import os
import bcrypt
import uuid
from datetime import datetime
import streamlit as st

# Fungsi untuk membuat file YAML jika belum ada
def create_yaml_if_not_exists(file_path, default_content):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            yaml.dump(default_content, file)

# Fungsi untuk membaca data dari file YAML
def read_yaml(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    return None

# Fungsi untuk menulis data ke file YAML
def write_yaml(file_path, data):
    with open(file_path, 'w') as file:
        yaml.dump(data, file)

# Fungsi untuk hash password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Fungsi untuk verifikasi password
def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# Fungsi untuk membuat ID unik
def generate_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

# Fungsi untuk mendapatkan timestamp saat ini
def get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Fungsi untuk inisialisasi file database
def initialize_database():
    # Direktori data
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # File users.yaml
    users_file = os.path.join(data_dir, "users.yaml")
    default_users = {
        "users": [
            {
                "username": "admin",
                "password_hash": hash_password("admin123"),
                "name": "Admin Utama",
                "role": "superadmin",
                "email": "admin@example.com",
                "created_at": get_current_timestamp()
            }
        ]
    }
    create_yaml_if_not_exists(users_file, default_users)
    
    # File marketing_activities.yaml
    activities_file = os.path.join(data_dir, "marketing_activities.yaml")
    default_activities = {"activities": []}
    create_yaml_if_not_exists(activities_file, default_activities)
    
    # File followups.yaml
    followups_file = os.path.join(data_dir, "followups.yaml")
    default_followups = {"followups": []}
    create_yaml_if_not_exists(followups_file, default_followups)
    
    # File config.yaml
    config_file = os.path.join(data_dir, "config.yaml")
    default_config = {
        "app_settings": {
            "app_name": "AI Suara Marketing Tracker",
            "version": "1.0.0",
            "theme": "light",
            "date_format": "%Y-%m-%d %H:%M:%S"
        },
        "notification_settings": {
            "enable_email": False,
            "enable_reminder": True,
            "reminder_days_before": 1
        }
    }
    create_yaml_if_not_exists(config_file, default_config)

# Fungsi untuk autentikasi pengguna
def authenticate_user(username, password):
    users_file = os.path.join("data", "users.yaml")
    users_data = read_yaml(users_file)
    
    if not users_data or "users" not in users_data:
        return None
    
    for user in users_data["users"]:
        if user["username"] == username and verify_password(password, user["password_hash"]):
            return user
    
    return None

# Fungsi untuk mendapatkan semua pengguna
def get_all_users():
    users_file = os.path.join("data", "users.yaml")
    users_data = read_yaml(users_file)
    
    if not users_data or "users" not in users_data:
        return []
    
    return users_data["users"]

# Fungsi untuk menambahkan pengguna baru
def add_user(username, password, name, role, email):
    users_file = os.path.join("data", "users.yaml")
    users_data = read_yaml(users_file)
    
    if not users_data:
        users_data = {"users": []}
    
    # Cek apakah username sudah ada
    for user in users_data["users"]:
        if user["username"] == username:
            return False, "Username sudah digunakan"
    
    # Tambahkan pengguna baru
    new_user = {
        "username": username,
        "password_hash": hash_password(password),
        "name": name,
        "role": role,
        "email": email,
        "created_at": get_current_timestamp()
    }
    
    users_data["users"].append(new_user)
    write_yaml(users_file, users_data)
    
    return True, "Pengguna berhasil ditambahkan"

# Fungsi untuk mendapatkan semua aktivitas pemasaran
def get_all_marketing_activities():
    activities_file = os.path.join("data", "marketing_activities.yaml")
    activities_data = read_yaml(activities_file)
    
    if not activities_data or "activities" not in activities_data:
        return []
    
    return activities_data["activities"]

# Fungsi untuk mendapatkan aktivitas pemasaran berdasarkan username
def get_marketing_activities_by_username(username):
    activities = get_all_marketing_activities()
    return [activity for activity in activities if activity["marketer_username"] == username]

# Fungsi untuk menambahkan aktivitas pemasaran baru
def add_marketing_activity(marketer_username, prospect_name, prospect_location, 
                          contact_person, contact_position, contact_phone, 
                          contact_email, activity_date, activity_type, description):
    activities_file = os.path.join("data", "marketing_activities.yaml")
    activities_data = read_yaml(activities_file)
    
    if not activities_data:
        activities_data = {"activities": []}
    
    # Buat ID baru
    activity_id = generate_id("act")
    
    # Tambahkan aktivitas baru
    new_activity = {
        "id": activity_id,
        "marketer_username": marketer_username,
        "prospect_name": prospect_name,
        "prospect_location": prospect_location,
        "contact_person": contact_person,
        "contact_position": contact_position,
        "contact_phone": contact_phone,
        "contact_email": contact_email,
        "activity_date": activity_date,
        "activity_type": activity_type,
        "description": description,
        "status": "baru",
        "created_at": get_current_timestamp(),
        "updated_at": get_current_timestamp()
    }
    
    activities_data["activities"].append(new_activity)
    write_yaml(activities_file, activities_data)
    
    return True, "Aktivitas pemasaran berhasil ditambahkan", activity_id

# Fungsi untuk memperbarui status aktivitas pemasaran
def update_activity_status(activity_id, new_status):
    activities_file = os.path.join("data", "marketing_activities.yaml")
    activities_data = read_yaml(activities_file)
    
    if not activities_data or "activities" not in activities_data:
        return False, "Data aktivitas tidak ditemukan"
    
    for activity in activities_data["activities"]:
        if activity["id"] == activity_id:
            activity["status"] = new_status
            activity["updated_at"] = get_current_timestamp()
            write_yaml(activities_file, activities_data)
            return True, "Status aktivitas berhasil diperbarui"
    
    return False, "Aktivitas tidak ditemukan"

# Fungsi untuk mendapatkan aktivitas pemasaran berdasarkan ID
def get_activity_by_id(activity_id):
    activities = get_all_marketing_activities()
    for activity in activities:
        if activity["id"] == activity_id:
            return activity
    return None

# Fungsi untuk mendapatkan semua follow-up
def get_all_followups():
    followups_file = os.path.join("data", "followups.yaml")
    followups_data = read_yaml(followups_file)
    
    if not followups_data or "followups" not in followups_data:
        return []
    
    return followups_data["followups"]

# Fungsi untuk mendapatkan follow-up berdasarkan activity_id
def get_followups_by_activity_id(activity_id):
    followups = get_all_followups()
    return [followup for followup in followups if followup["activity_id"] == activity_id]

# Fungsi untuk mendapatkan follow-up berdasarkan username
def get_followups_by_username(username):
    followups = get_all_followups()
    return [followup for followup in followups if followup["marketer_username"] == username]

# Fungsi untuk menambahkan follow-up baru
def add_followup(activity_id, marketer_username, followup_date, notes, 
                next_action, next_followup_date, interest_level, status_update):
    followups_file = os.path.join("data", "followups.yaml")
    followups_data = read_yaml(followups_file)
    
    if not followups_data:
        followups_data = {"followups": []}
    
    # Buat ID baru
    followup_id = generate_id("fu")
    
    # Tambahkan follow-up baru
    new_followup = {
        "id": followup_id,
        "activity_id": activity_id,
        "marketer_username": marketer_username,
        "followup_date": followup_date,
        "notes": notes,
        "next_action": next_action,
        "next_followup_date": next_followup_date,
        "interest_level": interest_level,
        "status_update": status_update,
        "created_at": get_current_timestamp()
    }
    
    followups_data["followups"].append(new_followup)
    write_yaml(followups_file, followups_data)
    
    # Update status aktivitas
    update_activity_status(activity_id, status_update)
    
    return True, "Follow-up berhasil ditambahkan"

# Fungsi untuk mendapatkan konfigurasi aplikasi
def get_app_config():
    config_file = os.path.join("data", "config.yaml")
    config_data = read_yaml(config_file)
    
    if not config_data:
        return None
    
    return config_data

# Fungsi untuk memperbarui konfigurasi aplikasi
def update_app_config(config_data):
    config_file = os.path.join("data", "config.yaml")
    write_yaml(config_file, config_data)
    return True, "Konfigurasi berhasil diperbarui"

# Fungsi untuk cek login - FIXED: Hanya mengembalikan user, bukan tuple
def check_login():
    # Inisialisasi session state jika belum ada
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    # Mengembalikan user jika sudah login, None jika belum
    return st.session_state.user if st.session_state.logged_in else None

# Fungsi untuk login
def login(username, password):
    user = authenticate_user(username, password)
    if user:
        st.session_state.logged_in = True
        st.session_state.user = user
        return True
    return False

# Fungsi untuk logout
def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
