import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime, timedelta
import os
from utils_with_edit_delete import (
    initialize_database, check_login, login, logout,
    get_all_users, add_user, delete_user, get_all_marketing_activities,
    get_marketing_activities_by_username, add_marketing_activity,
    edit_marketing_activity, delete_marketing_activity,
    get_activity_by_id, get_all_followups, get_followups_by_activity_id,
    get_followups_by_username, add_followup, update_activity_status,
    get_app_config, update_app_config
)
from data_utils import backup_data, restore_data, validate_data_integrity, export_to_csv

print("DEBUG: Initializing database...")
# Inisialisasi database
initialize_database()
print("DEBUG: Database initialized.")

# Konfigurasi halaman
st.set_page_config(
    page_title="AI Suara Marketing Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fungsi untuk menampilkan halaman login
def show_login_page():
    print("DEBUG: Starting show_login_page")
    # Hapus semua padding dan margin default
    st.markdown("""
        <style>
            .block-container {
                padding-top: 0 !important;
                padding-bottom: 0 !important;
                margin-top: 0 !important;
            }
            .css-1544g2n {
                padding-top: 0 !important;
            }
            .css-18e3th9 {
                padding-top: 0 !important;
                padding-bottom: 0 !important;
            }
            .css-1d391kg {
                padding-top: 0 !important;
                padding-bottom: 0 !important;
            }
            div[data-testid="stVerticalBlock"] {
                gap: 0 !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Gunakan HTML murni untuk memastikan logo benar-benar di tengah
    st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; margin-top: 20px; margin-bottom: 20px;">
            <img src="static/img/logo.jpg" style="max-width: 180px; margin: 0 auto;">
        </div>
        <h1 style="text-align: center; margin-bottom: 30px;">AI Suara Marketing Tracker</h1>
    """, unsafe_allow_html=True)

    # Buat container untuk form login
    login_container = st.container()

    # Buat kolom untuk memastikan form login berada di tengah
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)

            if submit:
                print("DEBUG: Login form submitted")
                if login(username, password):
                    st.success("Login berhasil!")
                    st.rerun()
                else:
                    st.error("Username atau password salah!")

        # Footer
        st.markdown("""
            <div style="text-align: center; margin-top: 20px; font-size: 0.8rem; color: #6c757d;">
                © 2025 AI Suara Marketing Tracker
            </div>
        """, unsafe_allow_html=True)
    print("DEBUG: Finished show_login_page")

# Fungsi untuk menampilkan sidebar
def show_sidebar():
    print("DEBUG: Starting show_sidebar")
    with st.sidebar:
        st.title("AI Suara Marketing")

        user = st.session_state.user
        st.write(f"Selamat datang, **{user['name']}**!")
        st.write(f"Role: **{user['role'].capitalize()}**")

        st.divider()

        # Menu berbeda untuk superadmin dan marketing
        if user['role'] == 'superadmin':
            menu = st.radio(
                "Menu",
                ["Dashboard", "Aktivitas Pemasaran", "Follow-up", "Manajemen Pengguna", "Pengaturan"],
                key="sidebar_menu"
            )
        else:
            menu = st.radio(
                "Menu",
                ["Dashboard", "Aktivitas Pemasaran", "Follow-up", "Profil"],
                key="sidebar_menu"
            )

        st.divider()

        if st.button("Logout", use_container_width=True):
            print("DEBUG: Logout button clicked")
            logout()
            st.rerun()

    print(f"DEBUG: Finished show_sidebar, selected menu: {menu}")
    return menu

# Fungsi untuk menampilkan dashboard superadmin
def show_superadmin_dashboard():
    print("DEBUG: Starting show_superadmin_dashboard")
    st.title("Dashboard Superadmin")

    # Ambil semua data
    print("DEBUG: Getting all marketing activities...")
    activities = get_all_marketing_activities()
    print("DEBUG: Getting all followups...")
    followups = get_all_followups()
    print("DEBUG: Getting all users...")
    users = get_all_users()
    marketing_users = [user for user in users if user['role'] == 'marketing']
    print("DEBUG: Data fetched for superadmin dashboard")

    # Jika tidak ada data, tampilkan pesan
    if not activities:
        st.info("Belum ada data aktivitas pemasaran. Tambahkan aktivitas pemasaran terlebih dahulu.")
        print("DEBUG: Finished show_superadmin_dashboard (no activities)")
        return

    # Konversi ke DataFrame untuk analisis
    activities_df = pd.DataFrame(activities)

    # Metrik utama
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Aktivitas", len(activities))
    with col2:
        st.metric("Total Prospek", activities_df['prospect_name'].nunique())
    with col3:
        st.metric("Total Marketing", len(marketing_users))
    with col4:
        if followups:
            followups_df = pd.DataFrame(followups)
            st.metric("Total Follow-up", len(followups))
        else:
            st.metric("Total Follow-up", 0)
    print("DEBUG: Metrics displayed")

    # Baris pertama grafik
    st.subheader("Analisis Aktivitas Pemasaran")
    col1, col2 = st.columns(2)

    with col1:
        # Distribusi status prospek
        if not activities_df.empty and 'status' in activities_df.columns:
            status_counts = activities_df['status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Jumlah']
            status_mapping = {'baru': 'Baru', 'dalam_proses': 'Dalam Proses', 'berhasil': 'Berhasil', 'gagal': 'Gagal'}
            status_counts['Status'] = status_counts['Status'].map(lambda x: status_mapping.get(x, x))
            fig = px.pie(status_counts, values='Jumlah', names='Status', title='Distribusi Status Prospek', color='Status',
                         color_discrete_map={'Baru': '#3498db', 'Dalam Proses': '#f39c12', 'Berhasil': '#2ecc71', 'Gagal': '#e74c3c'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Data status tidak tersedia.")

    with col2:
        # Aktivitas per marketing
        if not activities_df.empty and 'marketer_username' in activities_df.columns:
            marketer_counts = activities_df['marketer_username'].value_counts().reset_index()
            marketer_counts.columns = ['Marketing', 'Jumlah Aktivitas']
            fig = px.bar(marketer_counts, x='Marketing', y='Jumlah Aktivitas', title='Jumlah Aktivitas per Marketing',
                         color='Jumlah Aktivitas', color_continuous_scale=px.colors.sequential.Viridis)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Data marketing tidak tersedia.")
    print("DEBUG: First row of charts displayed")

    # Baris kedua grafik
    col1, col2 = st.columns(2)

    with col1:
        # Aktivitas per lokasi
        if not activities_df.empty and 'prospect_location' in activities_df.columns:
            location_counts = activities_df['prospect_location'].value_counts().reset_index()
            location_counts.columns = ['Lokasi', 'Jumlah']
            fig = px.bar(location_counts.head(10), x='Lokasi', y='Jumlah', title='10 Lokasi Prospek Teratas',
                         color='Jumlah', color_continuous_scale=px.colors.sequential.Plasma)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Data lokasi tidak tersedia.")

    with col2:
        # Aktivitas per jenis
        if not activities_df.empty and 'activity_type' in activities_df.columns:
            type_counts = activities_df['activity_type'].value_counts().reset_index()
            type_counts.columns = ['Jenis Aktivitas', 'Jumlah']
            fig = px.pie(type_counts, values='Jumlah', names='Jenis Aktivitas', title='Distribusi Jenis Aktivitas', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Data jenis aktivitas tidak tersedia.")
    print("DEBUG: Second row of charts displayed")

    # Daftar aktivitas terbaru
    st.subheader("Aktivitas Pemasaran Terbaru")
    if not activities_df.empty:
        activities_df['created_at'] = pd.to_datetime(activities_df['created_at'])
        activities_df = activities_df.sort_values('created_at', ascending=False)
        display_columns = ['marketer_username', 'prospect_name', 'prospect_location', 'activity_type', 'status', 'created_at']
        column_mapping = {'marketer_username': 'Marketing', 'prospect_name': 'Nama Prospek', 'prospect_location': 'Lokasi', 'activity_type': 'Jenis Aktivitas', 'status': 'Status', 'created_at': 'Tanggal Dibuat'}
        display_df = activities_df[display_columns].rename(columns=column_mapping)
        status_mapping = {'baru': 'Baru', 'dalam_proses': 'Dalam Proses', 'berhasil': 'Berhasil', 'gagal': 'Gagal'}
        if 'Status' in display_df.columns:
            display_df['Status'] = display_df['Status'].map(lambda x: status_mapping.get(x, x))
        st.dataframe(display_df.head(10), use_container_width=True)
    else:
        st.info("Tidak ada aktivitas terbaru.")
    print("DEBUG: Recent activities displayed")

    # Daftar follow-up yang akan datang
    if followups:
        st.subheader("Follow-up yang Akan Datang")
        followups_df = pd.DataFrame(followups)
        followups_df['next_followup_date'] = pd.to_datetime(followups_df['next_followup_date'])
        today = datetime.now()
        next_week = today + timedelta(days=7)
        upcoming_followups = followups_df[
            (followups_df['next_followup_date'] >= today) &
            (followups_df['next_followup_date'] <= next_week)
        ]

        if not upcoming_followups.empty:
            if not activities_df.empty:
                upcoming_followups = upcoming_followups.merge(
                    activities_df[['id', 'prospect_name']],
                    left_on='activity_id',
                    right_on='id',
                    how='left'
                )
                upcoming_followups['prospect_name'] = upcoming_followups['prospect_name'].fillna('N/A')
                display_columns = ['marketer_username', 'prospect_name', 'next_followup_date', 'next_action']
                column_mapping = {'marketer_username': 'Marketing', 'prospect_name': 'Nama Prospek', 'next_followup_date': 'Tanggal Follow-up', 'next_action': 'Tindakan Selanjutnya'}
                display_df = upcoming_followups[display_columns].rename(columns=column_mapping)
                display_df = display_df.sort_values('Tanggal Follow-up')
                st.dataframe(display_df, use_container_width=True)
            else:
                st.info("Data aktivitas tidak ditemukan untuk follow-up.")
        else:
            st.info("Tidak ada follow-up yang dijadwalkan dalam 7 hari ke depan.")
    else:
        st.info("Tidak ada data follow-up.")
    print("DEBUG: Upcoming followups displayed")
    print("DEBUG: Finished show_superadmin_dashboard")

# Fungsi untuk menampilkan dashboard marketing
def show_marketing_dashboard():
    print("DEBUG: Starting show_marketing_dashboard")
    st.title("DASHBOARD MARKETING")
    user = st.session_state.user
    username = user["username"]

    # Ambil data aktivitas marketing
    print(f"DEBUG: Getting activities for user: {username}")
    activities = get_marketing_activities_by_username(username)
    print(f"DEBUG: Getting followups for user: {username}")
    followups = get_followups_by_username(username)
    print("DEBUG: Data fetched for marketing dashboard")

    # Jika tidak ada data, tampilkan pesan
    if not activities:
        st.info("Anda belum memiliki aktivitas pemasaran. Tambahkan aktivitas pemasaran terlebih dahulu.")
        print("DEBUG: Finished show_marketing_dashboard (no activities)")
        return

    # Konversi ke DataFrame
    activities_df = pd.DataFrame(activities)
    if followups:
         followups_df = pd.DataFrame(followups)
    else:
         followups_df = pd.DataFrame(columns=["activity_id", "marketer_username", "followup_date", "notes", "next_followup_date", "next_action", "created_at"]) # Create empty df with expected columns if no followups

    # Metrik utama (Marketing)
    st.subheader("Ringkasan Kinerja Anda")
    col1, col2, col3 = st.columns(3) # Only 3 metrics needed for marketing user
    with col1:
        st.metric("Total Aktivitas Anda", len(activities_df))
    with col2:
        if not activities_df.empty:
             st.metric("Total Prospek Anda", activities_df["prospect_name"].nunique())
        else:
             st.metric("Total Prospek Anda", 0)
    with col3:
        st.metric("Total Follow-up Anda", len(followups_df))
    print("DEBUG: Marketing metrics displayed")

    st.divider()

    # Baris pertama grafik (Marketing)
    st.subheader("Analisis Aktivitas Pemasaran Anda")
    col1, col2 = st.columns(2)

    with col1:
        # Distribusi status prospek
        if not activities_df.empty and "status" in activities_df.columns:
            status_counts = activities_df["status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Jumlah"]
            status_mapping = {"baru": "Baru", "dalam_proses": "Dalam Proses", "berhasil": "Berhasil", "gagal": "Gagal"}
            status_counts["Status"] = status_counts["Status"].map(lambda x: status_mapping.get(x, x))
            fig = px.pie(status_counts, values="Jumlah", names="Status", title="Distribusi Status Prospek Anda", color="Status",
                         color_discrete_map={"Baru": "#3498db", "Dalam Proses": "#f39c12", "Berhasil": "#2ecc71", "Gagal": "#e74c3c"})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Belum ada data status untuk ditampilkan.")


    with col2:
        # Aktivitas per lokasi
        if not activities_df.empty and "prospect_location" in activities_df.columns:
            location_counts = activities_df["prospect_location"].value_counts().reset_index()
            location_counts.columns = ["Lokasi", "Jumlah"]
            fig = px.bar(location_counts.head(10), x="Lokasi", y="Jumlah", title="10 Lokasi Prospek Teratas Anda",
                         color="Jumlah", color_continuous_scale=px.colors.sequential.Plasma)
            st.plotly_chart(fig, use_container_width=True)
        else:
             st.info("Belum ada data lokasi untuk ditampilkan.")
    print("DEBUG: Marketing first row charts displayed")

    # Aktivitas per jenis
    if not activities_df.empty and "activity_type" in activities_df.columns:
        st.subheader("Distribusi Jenis Aktivitas Anda")
        type_counts = activities_df["activity_type"].value_counts().reset_index()
        type_counts.columns = ["Jenis Aktivitas", "Jumlah"]
        fig = px.pie(type_counts, values="Jumlah", names="Jenis Aktivitas", title="Distribusi Jenis Aktivitas Anda", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Belum ada data jenis aktivitas untuk ditampilkan.")
    print("DEBUG: Marketing activity type chart displayed")

    st.divider()

    # Daftar aktivitas terbaru
    st.subheader("Aktivitas Pemasaran Terbaru Anda")
    if not activities_df.empty:
        activities_df["created_at"] = pd.to_datetime(activities_df["created_at"])
        activities_df = activities_df.sort_values("created_at", ascending=False)
        display_columns = ["prospect_name", "prospect_location", "activity_type", "status", "created_at"] # Removed marketer_username
        column_mapping = {"prospect_name": "Nama Prospek", "prospect_location": "Lokasi", "activity_type": "Jenis Aktivitas", "status": "Status", "created_at": "Tanggal Dibuat"}
        display_df = activities_df[display_columns].rename(columns=column_mapping)
        status_mapping = {"baru": "Baru", "dalam_proses": "Dalam Proses", "berhasil": "Berhasil", "gagal": "Gagal"}
        if "Status" in display_df.columns:
             display_df["Status"] = display_df["Status"].map(lambda x: status_mapping.get(x, x))
        st.dataframe(display_df.head(10), use_container_width=True)
    else:
        st.info("Tidak ada aktivitas terbaru untuk ditampilkan.")
    print("DEBUG: Marketing recent activities displayed")

    st.divider()

    # Daftar follow-up yang akan datang
    st.subheader("Follow-up Anda yang Akan Datang")
    if not followups_df.empty:
        followups_df["next_followup_date"] = pd.to_datetime(followups_df["next_followup_date"])
        today = datetime.now()
        next_week = today + timedelta(days=7)
        upcoming_followups = followups_df[
            (followups_df["next_followup_date"] >= today) &
            (followups_df["next_followup_date"] <= next_week)
        ]

        if not upcoming_followups.empty:
            # Gabungkan dengan data aktivitas untuk mendapatkan nama prospek
            if not activities_df.empty:
                 upcoming_followups = upcoming_followups.merge(
                     activities_df[["id", "prospect_name"]],
                     left_on="activity_id",
                     right_on="id",
                     how="left"
                 )
                 # Handle cases where prospect_name might be missing after merge if activity was deleted
                 upcoming_followups["prospect_name"] = upcoming_followups["prospect_name"].fillna("N/A")

                 display_columns = ["prospect_name", "next_followup_date", "next_action"] # Removed marketer_username
                 column_mapping = {"prospect_name": "Nama Prospek", "next_followup_date": "Tanggal Follow-up", "next_action": "Tindakan Selanjutnya"}
                 display_df = upcoming_followups[display_columns].rename(columns=column_mapping)
                 display_df = display_df.sort_values("Tanggal Follow-up")
                 st.dataframe(display_df, use_container_width=True)
            else:
                 st.info("Data aktivitas tidak ditemukan untuk menampilkan nama prospek pada follow-up.")

        else:
            st.info("Tidak ada follow-up yang dijadwalkan dalam 7 hari ke depan.")
    else:
        st.info("Anda belum memiliki data follow-up.")
    print("DEBUG: Marketing upcoming followups displayed")
    print("DEBUG: Finished show_marketing_dashboard")

# Fungsi lainnya (show_marketing_activities_page, show_followup_page, etc.) tetap sama
# ... (kode fungsi lain tidak ditampilkan untuk keringkasan, tapi diasumsikan ada di sini)

# Fungsi untuk menampilkan halaman aktivitas pemasaran
def show_marketing_activities_page():
    print("DEBUG: Starting show_marketing_activities_page")
    st.title("Aktivitas Pemasaran")
    # ... (rest of the function code)
    print("DEBUG: Finished show_marketing_activities_page")

# Fungsi untuk menampilkan halaman follow-up
def show_followup_page():
    print("DEBUG: Starting show_followup_page")
    st.title("Follow-up")
    # ... (rest of the function code)
    print("DEBUG: Finished show_followup_page")

# Fungsi untuk menampilkan halaman manajemen pengguna
def show_user_management_page():
    print("DEBUG: Starting show_user_management_page")
    st.title("Manajemen Pengguna")
    # ... (rest of the function code)
    print("DEBUG: Finished show_user_management_page")

# Fungsi untuk menampilkan halaman pengaturan
def show_settings_page():
    print("DEBUG: Starting show_settings_page")
    st.title("Pengaturan")
    # ... (rest of the function code)
    print("DEBUG: Finished show_settings_page")

# Fungsi untuk menampilkan halaman profil
def show_profile_page():
    print("DEBUG: Starting show_profile_page")
    st.title("Profil Pengguna")
    # ... (rest of the function code)
    print("DEBUG: Finished show_profile_page")


# Fungsi utama aplikasi
def main():
    print("DEBUG: Starting main function")
    # Cek status login
    user = check_login()

    if not user:
        print("DEBUG: User not logged in, showing login page")
        show_login_page()
    else:
        print(f"DEBUG: User {user['username']} logged in, showing sidebar")
        menu = show_sidebar()
        print(f"DEBUG: Sidebar returned menu: {menu}")

        # Tampilkan halaman sesuai menu yang dipilih
        print(f"DEBUG: Routing to page: {menu}")
        if menu == "Dashboard":
            if st.session_state.user['role'] == 'superadmin':
                show_superadmin_dashboard()
            else:
                show_marketing_dashboard()
        elif menu == "Aktivitas Pemasaran":
            show_marketing_activities_page()
        elif menu == "Follow-up":
            show_followup_page()
        elif menu == "Manajemen Pengguna":
            show_user_management_page()
        elif menu == "Pengaturan":
            show_settings_page()
        elif menu == "Profil":
            show_profile_page()
        print(f"DEBUG: Finished rendering page: {menu}")

    print("DEBUG: Finished main function")

if __name__ == "__main__":
    print("DEBUG: Script execution started")
    main()
    print("DEBUG: Script execution finished")


