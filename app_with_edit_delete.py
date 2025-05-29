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

# Inisialisasi database
initialize_database()

# Konfigurasi halaman
st.set_page_config(
    page_title="AI Suara Marketing Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fungsi untuk menampilkan halaman login
def show_login_page():
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

# Fungsi untuk menampilkan sidebar
def show_sidebar():
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
                ["Dashboard", "Aktivitas Pemasaran", "Follow-up", "Manajemen Pengguna", "Pengaturan"]
            )
        else:
            menu = st.radio(
                "Menu",
                ["Dashboard", "Aktivitas Pemasaran", "Follow-up", "Profil"]
            )
        
        st.divider()
        
        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()
    
    return menu

# Fungsi untuk menampilkan dashboard superadmin
def show_superadmin_dashboard():
    st.title("Dashboard Superadmin")
    
    # Ambil semua data
    activities = get_all_marketing_activities()
    followups = get_all_followups()
    users = get_all_users()
    marketing_users = [user for user in users if user['role'] == 'marketing']
    
    # Jika tidak ada data, tampilkan pesan
    if not activities:
        st.info("Belum ada data aktivitas pemasaran. Tambahkan aktivitas pemasaran terlebih dahulu.")
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
    
    # Baris pertama grafik
    st.subheader("Analisis Aktivitas Pemasaran")
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribusi status prospek
        status_counts = activities_df['status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Jumlah']
        
        # Mapping status untuk tampilan yang lebih baik
        status_mapping = {
            'baru': 'Baru',
            'dalam_proses': 'Dalam Proses',
            'berhasil': 'Berhasil',
            'gagal': 'Gagal'
        }
        status_counts['Status'] = status_counts['Status'].map(lambda x: status_mapping.get(x, x))
        
        fig = px.pie(
            status_counts, 
            values='Jumlah', 
            names='Status',
            title='Distribusi Status Prospek',
            color='Status',
            color_discrete_map={
                'Baru': '#3498db',
                'Dalam Proses': '#f39c12',
                'Berhasil': '#2ecc71',
                'Gagal': '#e74c3c'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Aktivitas per marketing
        marketer_counts = activities_df['marketer_username'].value_counts().reset_index()
        marketer_counts.columns = ['Marketing', 'Jumlah Aktivitas']
        
        fig = px.bar(
            marketer_counts,
            x='Marketing',
            y='Jumlah Aktivitas',
            title='Jumlah Aktivitas per Marketing',
            color='Jumlah Aktivitas',
            color_continuous_scale=px.colors.sequential.Viridis
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Baris kedua grafik
    col1, col2 = st.columns(2)
    
    with col1:
        # Aktivitas per lokasi
        location_counts = activities_df['prospect_location'].value_counts().reset_index()
        location_counts.columns = ['Lokasi', 'Jumlah']
        
        fig = px.bar(
            location_counts.head(10),
            x='Lokasi',
            y='Jumlah',
            title='10 Lokasi Prospek Teratas',
            color='Jumlah',
            color_continuous_scale=px.colors.sequential.Plasma
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Aktivitas per jenis
        if 'activity_type' in activities_df.columns:
            type_counts = activities_df['activity_type'].value_counts().reset_index()
            type_counts.columns = ['Jenis Aktivitas', 'Jumlah']
            
            fig = px.pie(
                type_counts,
                values='Jumlah',
                names='Jenis Aktivitas',
                title='Distribusi Jenis Aktivitas',
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Daftar aktivitas terbaru
    st.subheader("Aktivitas Pemasaran Terbaru")
    
    # Konversi created_at ke datetime dan urutkan
    activities_df['created_at'] = pd.to_datetime(activities_df['created_at'])
    activities_df = activities_df.sort_values('created_at', ascending=False)
    
    # Pilih kolom yang ingin ditampilkan
    display_columns = ['marketer_username', 'prospect_name', 'prospect_location', 
                      'activity_type', 'status', 'created_at']
    
    # Rename kolom untuk tampilan yang lebih baik
    column_mapping = {
        'marketer_username': 'Marketing',
        'prospect_name': 'Nama Prospek',
        'prospect_location': 'Lokasi',
        'activity_type': 'Jenis Aktivitas',
        'status': 'Status',
        'created_at': 'Tanggal Dibuat'
    }
    
    display_df = activities_df[display_columns].rename(columns=column_mapping)
    
    # Mapping status untuk tampilan yang lebih baik
    display_df['Status'] = display_df['Status'].map(lambda x: status_mapping.get(x, x))
    
    # Tampilkan 10 aktivitas terbaru
    st.dataframe(display_df.head(10), use_container_width=True)
    
    # Daftar follow-up yang akan datang
    if followups:
        st.subheader("Follow-up yang Akan Datang")
        
        followups_df = pd.DataFrame(followups)
        followups_df['next_followup_date'] = pd.to_datetime(followups_df['next_followup_date'])
        
        # Filter follow-up yang akan datang (dalam 7 hari ke depan)
        today = datetime.now()
        next_week = today + timedelta(days=7)
        upcoming_followups = followups_df[
            (followups_df['next_followup_date'] >= today) & 
            (followups_df['next_followup_date'] <= next_week)
        ]
        
        if not upcoming_followups.empty:
            # Gabungkan dengan data aktivitas untuk mendapatkan nama prospek
            upcoming_followups = upcoming_followups.merge(
                activities_df[['id', 'prospect_name']],
                left_on='activity_id',
                right_on='id',
                how='left'
            )
            
            # Pilih kolom yang ingin ditampilkan
            display_columns = ['marketer_username', 'prospect_name', 'next_followup_date', 'next_action']
            
            # Rename kolom untuk tampilan yang lebih baik
            column_mapping = {
                'marketer_username': 'Marketing',
                'prospect_name': 'Nama Prospek',
                'next_followup_date': 'Tanggal Follow-up',
                'next_action': 'Tindakan Selanjutnya'
            }
            
            display_df = upcoming_followups[display_columns].rename(columns=column_mapping)
            display_df = display_df.sort_values('Tanggal Follow-up')
            
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("Tidak ada follow-up yang dijadwalkan dalam 7 hari ke depan.")

# Fungsi untuk menampilkan dashboard marketing
def show_marketing_dashboard():
    st.title("DASHBOARD MARKETING")
    
    user = st.session_state.user
    username = user['username']
    
    # Ambil data aktivitas marketing
    activities = get_marketing_activities_by_username(username)
    followups = get_followups_by_username(username)
    
    # Jika tidak ada data, tampilkan pesan
    if not activities:
        st.info("Anda belum memiliki aktivitas pemasaran. Tambahkan aktivitas pemasaran terlebih dahulu.")
        return

# Fungsi untuk menampilkan halaman aktivitas pemasaran
def show_marketing_activities_page():
    st.title("Aktivitas Pemasaran")
    
    user = st.session_state.user
    
    # Tab untuk daftar aktivitas, tambah aktivitas, edit aktivitas, dan hapus aktivitas
    tab1, tab2, tab3, tab4 = st.tabs(["Daftar Aktivitas", "Tambah Aktivitas", "Edit Aktivitas", "Hapus Aktivitas"])
    
    with tab1:
        # Filter berdasarkan role
        if user['role'] == 'superadmin':
            activities = get_all_marketing_activities()
        else:
            activities = get_marketing_activities_by_username(user['username'])
        
        if not activities:
            st.info("Belum ada data aktivitas pemasaran.")
        else:
            # Konversi ke DataFrame
            activities_df = pd.DataFrame(activities)
            
            # Filter dan pencarian
            col1, col2 = st.columns(2)
            
            with col1:
                if 'status' in activities_df.columns:
                    status_options = ['Semua'] + sorted(activities_df['status'].unique().tolist())
                    status_filter = st.selectbox("Filter Status", status_options)
            
            with col2:
                search_term = st.text_input("Cari Prospek", "")
            
            # Terapkan filter
            filtered_df = activities_df.copy()
            
            if status_filter != 'Semua' and 'status' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['status'] == status_filter]
            
            if search_term:
                filtered_df = filtered_df[
                    filtered_df['prospect_name'].str.contains(search_term, case=False) |
                    filtered_df['prospect_location'].str.contains(search_term, case=False)
                ]
            
            # Pilih kolom yang ingin ditampilkan
            if user['role'] == 'superadmin':
                display_columns = ['id', 'marketer_username', 'prospect_name', 'prospect_location', 
                                  'activity_type', 'status', 'created_at']
                column_mapping = {
                    'id': 'ID',
                    'marketer_username': 'Marketing',
                    'prospect_name': 'Nama Prospek',
                    'prospect_location': 'Lokasi',
                    'activity_type': 'Jenis Aktivitas',
                    'status': 'Status',
                    'created_at': 'Tanggal Dibuat'
                }
            else:
                display_columns = ['id', 'prospect_name', 'prospect_location', 
                                  'activity_type', 'status', 'created_at']
                column_mapping = {
                    'id': 'ID',
                    'prospect_name': 'Nama Prospek',
                    'prospect_location': 'Lokasi',
                    'activity_type': 'Jenis Aktivitas',
                    'status': 'Status',
                    'created_at': 'Tanggal Dibuat'
                }
            
            # Mapping status untuk tampilan yang lebih baik
            status_mapping = {
                'baru': 'Baru',
                'dalam_proses': 'Dalam Proses',
                'berhasil': 'Berhasil',
                'gagal': 'Gagal'
            }
            
            display_df = filtered_df[display_columns].rename(columns=column_mapping)
            
            if 'Status' in display_df.columns:
                display_df['Status'] = display_df['Status'].map(lambda x: status_mapping.get(x, x))
            
            # Tampilkan data
            st.dataframe(display_df, use_container_width=True)
            
            # Detail aktivitas
            st.subheader("Detail Aktivitas")
            selected_id = st.selectbox("Pilih ID Aktivitas untuk melihat detail", 
                                      options=filtered_df['id'].tolist())
            
            if selected_id:
                activity = get_activity_by_id(selected_id)
                
                if activity:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Informasi Prospek**")
                        st.write(f"Nama: {activity['prospect_name']}")
                        st.write(f"Lokasi: {activity['prospect_location']}")
                        st.write(f"Kontak: {activity['contact_person']}")
                        st.write(f"Jabatan: {activity['contact_position']}")
                        st.write(f"Telepon: {activity['contact_phone']}")
                        st.write(f"Email: {activity['contact_email']}")
                    
                    with col2:
                        st.write("**Informasi Aktivitas**")
                        st.write(f"Jenis: {activity['activity_type']}")
                        st.write(f"Tanggal: {activity['activity_date']}")
                        st.write(f"Status: {status_mapping.get(activity['status'], activity['status'])}")
                        st.write(f"Marketing: {activity['marketer_username']}")
                        st.write(f"Dibuat: {activity['created_at']}")
                        st.write(f"Diperbarui: {activity['updated_at']}")
                    
                    st.write("**Deskripsi**")
                    st.write(activity['description'])
                    
                    # Tampilkan riwayat follow-up untuk aktivitas ini
                    followups = get_followups_by_activity_id(selected_id)
                    
                    if followups:
                        st.subheader("Riwayat Follow-up")
                        
                        followups_df = pd.DataFrame(followups)
                        followups_df = followups_df.sort_values('created_at', ascending=False)
                        
                        for i, followup in enumerate(followups_df.to_dict('records')):
                            with st.expander(f"Follow-up #{i+1} - {followup['followup_date']}"):
                                st.write(f"**Catatan:** {followup['notes']}")
                                st.write(f"**Tindakan Selanjutnya:** {followup['next_action']}")
                                st.write(f"**Jadwal Follow-up Berikutnya:** {followup['next_followup_date']}")
                                st.write(f"**Tingkat Ketertarikan:** {followup['interest_level']}/5")
                                st.write(f"**Status Update:** {status_mapping.get(followup['status_update'], followup['status_update'])}")
                                st.write(f"**Dibuat pada:** {followup['created_at']}")
                    else:
                        st.info("Belum ada follow-up untuk aktivitas ini.")
                    
                    # Tombol untuk menambahkan follow-up
                    if st.button("Tambahkan Follow-up", key="add_followup_button"):
                        st.session_state.add_followup_activity_id = selected_id
                        st.session_state.add_followup_mode = True
                        st.rerun()
    
    with tab2:
        st.subheader("Tambah Aktivitas Pemasaran Baru")
        
        # Form tambah aktivitas
        with st.form("add_activity_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                prospect_name = st.text_input("Nama Prospek *")
                prospect_location = st.text_input("Lokasi Prospek *")
                contact_person = st.text_input("Nama Kontak Person *")
                contact_position = st.text_input("Jabatan Kontak Person")
            
            with col2:
                contact_phone = st.text_input("Nomor Telepon Kontak")
                contact_email = st.text_input("Email Kontak")
                activity_date = st.date_input("Tanggal Aktivitas *", datetime.now())
                activity_type = st.selectbox(
                    "Jenis Aktivitas *",
                    ["Presentasi", "Demo Produk", "Follow-up Call", "Email", "Meeting", "Lainnya"]
                )
            
            description = st.text_area("Deskripsi Aktivitas *", height=150)
            
            # Tambahkan opsi untuk langsung menambahkan follow-up setelah simpan
            add_followup_after = st.checkbox("Tambahkan Follow-up setelah simpan")
            
            submitted = st.form_submit_button("Simpan", use_container_width=True)
            
            if submitted:
                if not prospect_name or not prospect_location or not contact_person or not description:
                    st.error("Mohon lengkapi semua field yang wajib diisi (bertanda *).")
                else:
                    # Format tanggal
                    activity_date_str = activity_date.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Tambahkan aktivitas
                    success, message, activity_id = add_marketing_activity(
                        user['username'], prospect_name, prospect_location,
                        contact_person, contact_position, contact_phone,
                        contact_email, activity_date_str, activity_type, description
                    )
                    
                    if success:
                        st.success(message)
                        # Jika opsi tambah follow-up dicentang, arahkan ke halaman follow-up
                        if add_followup_after:
                            st.session_state.add_followup_activity_id = activity_id
                            st.session_state.add_followup_mode = True
                            st.rerun()
                    else:
                        st.error(message)
    
    with tab3:
        st.subheader("Edit Aktivitas Pemasaran")
        
        # Filter aktivitas berdasarkan role
        if user['role'] == 'superadmin':
            activities = get_all_marketing_activities()
        else:
            activities = get_marketing_activities_by_username(user['username'])
        
        if not activities:
            st.info("Belum ada data aktivitas pemasaran untuk diedit.")
        else:
            # Konversi ke DataFrame untuk tampilan
            activities_df = pd.DataFrame(activities)
            
            # Pilih aktivitas yang akan diedit
            selected_id = st.selectbox(
                "Pilih ID Aktivitas untuk diedit",
                options=activities_df['id'].tolist(),
                format_func=lambda x: f"{x} - {activities_df[activities_df['id'] == x]['prospect_name'].values[0]}"
            )
            
            if selected_id:
                activity = get_activity_by_id(selected_id)
                
                if activity:
                    # Form edit aktivitas
                    with st.form("edit_activity_form"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            prospect_name = st.text_input("Nama Prospek *", value=activity['prospect_name'])
                            prospect_location = st.text_input("Lokasi Prospek *", value=activity['prospect_location'])
                            contact_person = st.text_input("Nama Kontak Person *", value=activity['contact_person'])
                            contact_position = st.text_input("Jabatan Kontak Person", value=activity['contact_position'])
                        
                        with col2:
                            contact_phone = st.text_input("Nomor Telepon Kontak", value=activity['contact_phone'])
                            contact_email = st.text_input("Email Kontak", value=activity['contact_email'])
                            
                            # Konversi string tanggal ke datetime untuk date_input
                            try:
                                activity_date_dt = datetime.strptime(activity['activity_date'], "%Y-%m-%d %H:%M:%S")
                            except:
                                activity_date_dt = datetime.now()
                                
                            activity_date = st.date_input("Tanggal Aktivitas *", activity_date_dt)
                            
                            activity_type = st.selectbox(
                                "Jenis Aktivitas *",
                                ["Presentasi", "Demo Produk", "Follow-up Call", "Email", "Meeting", "Lainnya"],
                                index=["Presentasi", "Demo Produk", "Follow-up Call", "Email", "Meeting", "Lainnya"].index(activity['activity_type']) if activity['activity_type'] in ["Presentasi", "Demo Produk", "Follow-up Call", "Email", "Meeting", "Lainnya"] else 0
                            )
                            
                            status = st.selectbox(
                                "Status *",
                                ["baru", "dalam_proses", "berhasil", "gagal"],
                                index=["baru", "dalam_proses", "berhasil", "gagal"].index(activity['status']) if activity['status'] in ["baru", "dalam_proses", "berhasil", "gagal"] else 0,
                                format_func=lambda x: {
                                    'baru': 'Baru',
                                    'dalam_proses': 'Dalam Proses',
                                    'berhasil': 'Berhasil',
                                    'gagal': 'Gagal'
                                }.get(x, x)
                            )
                        
                        description = st.text_area("Deskripsi Aktivitas *", value=activity['description'], height=150)
                        
                        submitted = st.form_submit_button("Simpan Perubahan", use_container_width=True)
                        
                        if submitted:
                            if not prospect_name or not prospect_location or not contact_person or not description:
                                st.error("Mohon lengkapi semua field yang wajib diisi (bertanda *).")
                            else:
                                # Format tanggal
                                activity_date_str = activity_date.strftime("%Y-%m-%d %H:%M:%S")
                                
                                # Edit aktivitas
                                success, message = edit_marketing_activity(
                                    selected_id, prospect_name, prospect_location,
                                    contact_person, contact_position, contact_phone,
                                    contact_email, activity_date_str, activity_type, description, status
                                )
                                
                                if success:
                                    st.success(message)
                                else:
                                    st.error(message)
    
    with tab4:
        st.subheader("Hapus Aktivitas Pemasaran")
        
        # Filter aktivitas berdasarkan role
        if user['role'] == 'superadmin':
            activities = get_all_marketing_activities()
        else:
            activities = get_marketing_activities_by_username(user['username'])
        
        if not activities:
            st.info("Belum ada data aktivitas pemasaran untuk dihapus.")
        else:
            # Konversi ke DataFrame untuk tampilan
            activities_df = pd.DataFrame(activities)
            
            # Pilih aktivitas yang akan dihapus
            selected_id = st.selectbox(
                "Pilih ID Aktivitas untuk dihapus",
                options=activities_df['id'].tolist(),
                format_func=lambda x: f"{x} - {activities_df[activities_df['id'] == x]['prospect_name'].values[0]}",
                key="delete_activity_select"
            )
            
            if selected_id:
                activity = get_activity_by_id(selected_id)
                
                if activity:
                    st.warning("Perhatian: Menghapus aktivitas pemasaran akan menghapus juga semua follow-up terkait. Tindakan ini tidak dapat dibatalkan.")
                    
                    # Tampilkan detail aktivitas yang akan dihapus
                    st.write("**Detail Aktivitas yang akan dihapus:**")
                    st.write(f"ID: {activity['id']}")
                    st.write(f"Nama Prospek: {activity['prospect_name']}")
                    st.write(f"Lokasi: {activity['prospect_location']}")
                    st.write(f"Jenis Aktivitas: {activity['activity_type']}")
                    st.write(f"Status: {status_mapping.get(activity['status'], activity['status'])}")
                    
                    # Hitung jumlah follow-up terkait
                    followups = get_followups_by_activity_id(selected_id)
                    if followups:
                        st.write(f"**Jumlah follow-up terkait yang akan dihapus: {len(followups)}**")
                    
                    # Konfirmasi penghapusan
                    confirm = st.checkbox("Saya yakin ingin menghapus aktivitas pemasaran ini beserta semua follow-up terkait")
                    
                    if st.button("Hapus Aktivitas", disabled=not confirm):
                        success, message = delete_marketing_activity(selected_id)
                        
                        if success:
                            st.success(message)
                            # Refresh halaman setelah penghapusan berhasil
                            st.rerun()
                        else:
                            st.error(message)

# Fungsi untuk menampilkan halaman follow-up
def show_followup_page():
    st.title("Follow-up")
    
    user = st.session_state.user
    
    # Cek apakah dalam mode tambah follow-up
    if hasattr(st.session_state, 'add_followup_mode') and st.session_state.add_followup_mode:
        activity_id = st.session_state.add_followup_activity_id
        activity = get_activity_by_id(activity_id)
        
        if activity:
            st.subheader(f"Tambah Follow-up untuk {activity['prospect_name']}")
            st.info("Follow-up adalah kelanjutan dari aktivitas pemasaran untuk masing-masing klien atau calon klien. Setiap follow-up akan terkait dengan aktivitas pemasaran tertentu.")
            
            with st.form("add_followup_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    followup_date = st.date_input("Tanggal Follow-up *", datetime.now())
                    notes = st.text_area("Catatan Hasil Follow-up *", height=150)
                
                with col2:
                    next_action = st.text_input("Rencana Tindak Lanjut Berikutnya *")
                    next_followup_date = st.date_input("Jadwal Follow-up Berikutnya *", 
                                                     datetime.now() + timedelta(days=7))
                    interest_level = st.slider("Tingkat Ketertarikan Prospek", 1, 5, 3)
                    status_update = st.selectbox(
                        "Status Prospek *",
                        ["baru", "dalam_proses", "berhasil", "gagal"],
                        format_func=lambda x: {
                            'baru': 'Baru',
                            'dalam_proses': 'Dalam Proses',
                            'berhasil': 'Berhasil',
                            'gagal': 'Gagal'
                        }.get(x, x)
                    )
                
                submitted = st.form_submit_button("Simpan", use_container_width=True)
                
                if submitted:
                    if not notes or not next_action:
                        st.error("Mohon lengkapi semua field yang wajib diisi (bertanda *).")
                    else:
                        # Format tanggal
                        followup_date_str = followup_date.strftime("%Y-%m-%d %H:%M:%S")
                        next_followup_date_str = next_followup_date.strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Tambahkan follow-up
                        success, message = add_followup(
                            activity_id, user['username'], followup_date_str,
                            notes, next_action, next_followup_date_str,
                            interest_level, status_update
                        )
                        
                        if success:
                            # Update status aktivitas
                            update_activity_status(activity_id, status_update)
                            
                            st.success(message)
                            # Reset mode tambah follow-up
                            st.session_state.add_followup_mode = False
                            del st.session_state.add_followup_activity_id
                            st.rerun()
                        else:
                            st.error(message)
            
            # Tombol untuk membatalkan
            if st.button("Batal"):
                st.session_state.add_followup_mode = False
                if hasattr(st.session_state, 'add_followup_activity_id'):
                    del st.session_state.add_followup_activity_id
                st.rerun()
    else:
        # Tab untuk daftar follow-up dan tambah follow-up
        tab1, tab2 = st.tabs(["Daftar Follow-up", "Tambah Follow-up"])
        
        with tab1:
            st.subheader("Daftar Follow-up")
            st.info("Follow-up adalah kelanjutan dari aktivitas pemasaran untuk masing-masing klien atau calon klien. Setiap follow-up terkait dengan aktivitas pemasaran tertentu.")
            
            # Filter follow-up berdasarkan role
            if user['role'] == 'superadmin':
                followups = get_all_followups()
            else:
                followups = get_followups_by_username(user['username'])
            
            if not followups:
                st.info("Belum ada data follow-up.")
            else:
                # Konversi ke DataFrame
                followups_df = pd.DataFrame(followups)
                
                # Gabungkan dengan data aktivitas untuk mendapatkan nama prospek
                activities = get_all_marketing_activities()
                activities_df = pd.DataFrame(activities)
                
                # Buat dictionary untuk mapping activity_id ke prospect_name
                activity_to_prospect = {activity['id']: activity['prospect_name'] for activity in activities}
                
                # Tambahkan kolom prospect_name ke followups_df
                followups_df['prospect_name'] = followups_df['activity_id'].map(activity_to_prospect)
                
                # Urutkan berdasarkan tanggal follow-up berikutnya
                followups_df['next_followup_date'] = pd.to_datetime(followups_df['next_followup_date'])
                followups_df = followups_df.sort_values('next_followup_date')
                
                # Pilih kolom yang ingin ditampilkan
                display_columns = ['id', 'activity_id', 'prospect_name', 'marketer_username', 
                                  'followup_date', 'next_followup_date', 'status_update']
                
                # Rename kolom untuk tampilan yang lebih baik
                column_mapping = {
                    'id': 'ID',
                    'activity_id': 'ID Aktivitas',
                    'prospect_name': 'Nama Prospek',
                    'marketer_username': 'Marketing',
                    'followup_date': 'Tanggal Follow-up',
                    'next_followup_date': 'Tanggal Follow-up Berikutnya',
                    'status_update': 'Status'
                }
                
                # Mapping status untuk tampilan yang lebih baik
                status_mapping = {
                    'baru': 'Baru',
                    'dalam_proses': 'Dalam Proses',
                    'berhasil': 'Berhasil',
                    'gagal': 'Gagal'
                }
                
                display_df = followups_df[display_columns].rename(columns=column_mapping)
                
                if 'Status' in display_df.columns:
                    display_df['Status'] = display_df['Status'].map(lambda x: status_mapping.get(x, x))
                
                # Tampilkan data
                st.dataframe(display_df, use_container_width=True)
                
                # Detail follow-up
                st.subheader("Detail Follow-up")
                selected_id = st.selectbox("Pilih ID Follow-up untuk melihat detail", 
                                          options=followups_df['id'].tolist())
                
                if selected_id:
                    followup = next((f for f in followups if f['id'] == selected_id), None)
                    
                    if followup:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write("**Informasi Follow-up**")
                            st.write(f"Tanggal Follow-up: {followup['followup_date']}")
                            st.write(f"Jadwal Follow-up Berikutnya: {followup['next_followup_date']}")
                            st.write(f"Tingkat Ketertarikan: {followup['interest_level']}/5")
                            st.write(f"Status: {status_mapping.get(followup['status_update'], followup['status_update'])}")
                        
                        with col2:
                            # Dapatkan informasi aktivitas terkait
                            activity = get_activity_by_id(followup['activity_id'])
                            if activity:
                                st.write("**Informasi Aktivitas Terkait**")
                                st.write(f"Nama Prospek: {activity['prospect_name']}")
                                st.write(f"Lokasi: {activity['prospect_location']}")
                                st.write(f"Jenis Aktivitas: {activity['activity_type']}")
                                st.write(f"Marketing: {activity['marketer_username']}")
                        
                        st.write("**Catatan Hasil Follow-up**")
                        st.write(followup['notes'])
                        
                        st.write("**Rencana Tindak Lanjut Berikutnya**")
                        st.write(followup['next_action'])
        
        with tab2:
            st.subheader("Tambah Follow-up Baru")
            st.info("Follow-up adalah kelanjutan dari aktivitas pemasaran untuk masing-masing klien atau calon klien. Pilih aktivitas pemasaran yang ingin di-follow-up.")
            
            # Filter aktivitas berdasarkan role
            if user['role'] == 'superadmin':
                activities = get_all_marketing_activities()
            else:
                activities = get_marketing_activities_by_username(user['username'])
            
            if not activities:
                st.info("Belum ada aktivitas pemasaran. Tambahkan aktivitas pemasaran terlebih dahulu.")
            else:
                # Konversi ke DataFrame untuk tampilan
                activities_df = pd.DataFrame(activities)
                
                # Pilih aktivitas untuk follow-up
                selected_id = st.selectbox(
                    "Pilih Aktivitas Pemasaran untuk Follow-up",
                    options=activities_df['id'].tolist(),
                    format_func=lambda x: f"{x} - {activities_df[activities_df['id'] == x]['prospect_name'].values[0]}"
                )
                
                if selected_id:
                    if st.button("Lanjutkan ke Form Follow-up"):
                        st.session_state.add_followup_activity_id = selected_id
                        st.session_state.add_followup_mode = True
                        st.rerun()

# Fungsi untuk menampilkan halaman manajemen pengguna
def show_user_management_page():
    st.title("Manajemen Pengguna")
    
    # Hanya superadmin yang bisa mengakses halaman ini
    if st.session_state.user['role'] != 'superadmin':
        st.error("Anda tidak memiliki akses ke halaman ini.")
        return
    
    # Tab untuk daftar pengguna dan tambah pengguna
    tab1, tab2, tab3 = st.tabs(["Daftar Pengguna", "Tambah Pengguna", "Hapus Pengguna"])
    
    with tab1:
        users = get_all_users()
        
        if not users:
            st.info("Belum ada data pengguna.")
        else:
            # Konversi ke DataFrame
            users_df = pd.DataFrame(users)
            
            # Pilih kolom yang ingin ditampilkan
            display_columns = ['username', 'name', 'email', 'role', 'created_at']
            
            # Rename kolom untuk tampilan yang lebih baik
            column_mapping = {
                'username': 'Username',
                'name': 'Nama',
                'email': 'Email',
                'role': 'Role',
                'created_at': 'Tanggal Dibuat'
            }
            
            display_df = users_df[display_columns].rename(columns=column_mapping)
            
            # Mapping role untuk tampilan yang lebih baik
            display_df['Role'] = display_df['Role'].map(lambda x: x.capitalize())
            
            # Tampilkan data
            st.dataframe(display_df, use_container_width=True)
    
    with tab2:
        st.subheader("Tambah Pengguna Baru")
        
        # Form tambah pengguna
        with st.form("add_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("Username *")
                name = st.text_input("Nama Lengkap *")
                email = st.text_input("Email *")
            
            with col2:
                password = st.text_input("Password *", type="password")
                confirm_password = st.text_input("Konfirmasi Password *", type="password")
                role = st.selectbox("Role *", ["marketing", "superadmin"], format_func=lambda x: x.capitalize())
            
            submitted = st.form_submit_button("Simpan", use_container_width=True)
            
            if submitted:
                if not username or not name or not email or not password:
                    st.error("Mohon lengkapi semua field yang wajib diisi (bertanda *).")
                elif password != confirm_password:
                    st.error("Password dan konfirmasi password tidak cocok.")
                else:
                    # Tambahkan pengguna
                    success, message = add_user(username, password, name, role, email)
                    
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
    
    with tab3:
        st.subheader("Hapus Pengguna")
        
        users = get_all_users()
        current_username = st.session_state.user['username']
        
        # Filter pengguna yang bisa dihapus (tidak termasuk diri sendiri)
        deletable_users = [user for user in users if user['username'] != current_username]
        
        if not deletable_users:
            st.info("Tidak ada pengguna lain yang dapat dihapus.")
        else:
            # Buat daftar username untuk dropdown
            usernames = [user['username'] for user in deletable_users]
            
            # Tampilkan dropdown dan tombol hapus
            selected_username = st.selectbox("Pilih pengguna yang akan dihapus", usernames)
            
            # Tampilkan detail pengguna yang dipilih
            selected_user = next((user for user in deletable_users if user['username'] == selected_username), None)
            
            if selected_user:
                st.write("**Detail Pengguna:**")
                st.write(f"Username: {selected_user['username']}")
                st.write(f"Nama: {selected_user['name']}")
                st.write(f"Email: {selected_user['email']}")
                st.write(f"Role: {selected_user['role'].capitalize()}")
                
                # Konfirmasi penghapusan
                st.warning("Penghapusan pengguna tidak dapat dibatalkan. Semua data aktivitas dan follow-up yang terkait dengan pengguna ini akan tetap ada.")
                
                if st.button("Hapus Pengguna", key="delete_user_button"):
                    # Konfirmasi tambahan
                    confirm = st.checkbox(f"Saya yakin ingin menghapus pengguna {selected_username}")
                    
                    if confirm:
                        success, message = delete_user(selected_username, current_username)
                        
                        if success:
                            st.success(message)
                            # Refresh halaman setelah penghapusan berhasil
                            st.rerun()
                        else:
                            st.error(message)

# Fungsi untuk menampilkan halaman pengaturan
def show_settings_page():
    st.title("Pengaturan")
    
    # Hanya superadmin yang bisa mengakses halaman ini
    if st.session_state.user['role'] != 'superadmin':
        st.error("Anda tidak memiliki akses ke halaman ini.")
        return
    
    # Tab untuk pengaturan umum dan backup/restore
    tab1, tab2 = st.tabs(["Pengaturan Umum", "Backup & Restore"])
    
    with tab1:
        st.subheader("Pengaturan Aplikasi")
        
        # Ambil konfigurasi saat ini
        config = get_app_config()
        
        # Form pengaturan
        with st.form("settings_form"):
            app_name = st.text_input("Nama Aplikasi", config.get('app_name', 'AI Suara Marketing Tracker'))
            company_name = st.text_input("Nama Perusahaan", config.get('company_name', 'AI Suara'))
            
            submitted = st.form_submit_button("Simpan Pengaturan", use_container_width=True)
            
            if submitted:
                # Update konfigurasi
                new_config = {
                    'app_name': app_name,
                    'company_name': company_name
                }
                
                success, message = update_app_config(new_config)
                
                if success:
                    st.success(message)
                else:
                    st.error(message)
    
    with tab2:
        st.subheader("Backup & Restore Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Backup Data**")
            st.write("Backup data aplikasi ke file.")
            
            if st.button("Backup Data Sekarang", use_container_width=True):
                success, message, backup_file = backup_data()
                
                if success:
                    st.success(message)
                    
                    # Download link
                    with open(backup_file, "rb") as file:
                        st.download_button(
                            label="Download Backup File",
                            data=file,
                            file_name=os.path.basename(backup_file),
                            mime="application/octet-stream",
                            use_container_width=True
                        )
                else:
                    st.error(message)
        
        with col2:
            st.write("**Restore Data**")
            st.write("Restore data aplikasi dari file backup.")
            
            uploaded_file = st.file_uploader("Pilih file backup", type=["zip"])
            
            if uploaded_file is not None:
                if st.button("Restore Data", use_container_width=True):
                    # Simpan file yang diupload
                    with open("temp_backup.zip", "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Restore data
                    success, message = restore_data("temp_backup.zip")
                    
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
        
        st.divider()
        
        st.subheader("Validasi & Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Validasi Integritas Data**")
            st.write("Periksa integritas data aplikasi.")
            
            if st.button("Validasi Data", use_container_width=True):
                success, message, issues = validate_data_integrity()
                
                if success and not issues:
                    st.success(message)
                elif success and issues:
                    st.warning(message)
                    st.write("Masalah yang ditemukan:")
                    for issue in issues:
                        st.write(f"- {issue}")
                else:
                    st.error(message)
        
        with col2:
            st.write("**Export Data ke CSV**")
            st.write("Export data aplikasi ke file CSV.")
            
            export_type = st.selectbox(
                "Pilih data yang akan diexport",
                ["Aktivitas Pemasaran", "Follow-up", "Pengguna"]
            )
            
            if st.button("Export Data", use_container_width=True):
                if export_type == "Aktivitas Pemasaran":
                    success, message, export_file = export_to_csv("activities")
                elif export_type == "Follow-up":
                    success, message, export_file = export_to_csv("followups")
                else:
                    success, message, export_file = export_to_csv("users")
                
                if success:
                    st.success(message)
                    
                    # Download link
                    with open(export_file, "rb") as file:
                        st.download_button(
                            label="Download CSV File",
                            data=file,
                            file_name=os.path.basename(export_file),
                            mime="text/csv",
                            use_container_width=True
                        )
                else:
                    st.error(message)

# Fungsi untuk menampilkan halaman profil
def show_profile_page():
    st.title("Profil Saya")
    
    user = st.session_state.user
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Informasi Pengguna**")
        st.write(f"Username: {user['username']}")
        st.write(f"Nama: {user['name']}")
        st.write(f"Email: {user['email']}")
        st.write(f"Role: {user['role'].capitalize()}")
        st.write(f"Bergabung sejak: {user['created_at']}")
    
    with col2:
        st.write("**Statistik Aktivitas**")
        
        # Ambil data aktivitas
        activities = get_marketing_activities_by_username(user['username'])
        followups = get_followups_by_username(user['username'])
        
        st.write(f"Total Aktivitas: {len(activities)}")
        st.write(f"Total Follow-up: {len(followups)}")
        
        if activities:
            # Hitung statistik
            activities_df = pd.DataFrame(activities)
            
            # Status
            if 'status' in activities_df.columns:
                status_counts = activities_df['status'].value_counts()
                
                st.write("**Distribusi Status Prospek**")
                
                # Mapping status untuk tampilan yang lebih baik
                status_mapping = {
                    'baru': 'Baru',
                    'dalam_proses': 'Dalam Proses',
                    'berhasil': 'Berhasil',
                    'gagal': 'Gagal'
                }
                
                for status, count in status_counts.items():
                    st.write(f"{status_mapping.get(status, status)}: {count}")

# Fungsi utama
def main():
    # Inisialisasi session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    # Cek login
    if not st.session_state.logged_in:
        user = check_login()
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
        else:
            show_login_page()
            return
    
    # Tampilkan sidebar dan dapatkan menu yang dipilih
    menu = show_sidebar()
    
    # Tampilkan halaman sesuai menu yang dipilih
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

if __name__ == "__main__":
    main()
