import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime, timedelta
import os
from utils import (
    initialize_database, check_login, login, logout,
    get_all_users, add_user, get_all_marketing_activities,
    get_marketing_activities_by_username, add_marketing_activity,
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
    st.markdown(
        """
        <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            background-color: #f8f9fa;
        }
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .login-footer {
            text-align: center;
            margin-top: 2rem;
            font-size: 0.8rem;
            color: #6c757d;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-header">', unsafe_allow_html=True)
        st.title("AI Suara Marketing Tracker")
        st.markdown("</div>", unsafe_allow_html=True)
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", use_container_width=True):
            if login(username, password):
                st.success("Login berhasil!")
                st.rerun()
            else:
                st.error("Username atau password salah!")
        st.markdown('<div class="login-footer">', unsafe_allow_html=True)
        st.markdown("© 2025 AI Suara Marketing Tracker")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

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
    
    # Tab untuk daftar aktivitas dan tambah aktivitas
    tab1, tab2 = st.tabs(["Daftar Aktivitas", "Tambah Aktivitas"])
    
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
                    
                    # Tampilkan follow-up
                    st.subheader("Riwayat Follow-up")
                    followups = get_followups_by_activity_id(selected_id)
                    
                    if followups:
                        followups_df = pd.DataFrame(followups)
                        followups_df = followups_df.sort_values('created_at', ascending=False)
                        
                        for idx, followup in followups_df.iterrows():
                            with st.expander(f"Follow-up {followup['followup_date']}"):
                                st.write(f"**Catatan**: {followup['notes']}")
                                st.write(f"**Tindakan Selanjutnya**: {followup['next_action']}")
                                st.write(f"**Jadwal Follow-up Berikutnya**: {followup['next_followup_date']}")
                                st.write(f"**Tingkat Ketertarikan**: {followup['interest_level']}/5")
                                st.write(f"**Status**: {status_mapping.get(followup['status_update'], followup['status_update'])}")
                    else:
                        st.info("Belum ada follow-up untuk aktivitas ini.")
                    
                    # Tambah follow-up baru
                    if st.button("Tambah Follow-up Baru"):
                        st.session_state.add_followup_activity_id = selected_id
                        st.session_state.add_followup_mode = True
                        st.experimental_rerun()
    
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
                        # Tambahkan opsi untuk langsung menambahkan follow-up
                        if st.button("Tambahkan Follow-up Sekarang"):
                            st.session_state.add_followup_activity_id = activity_id
                            st.session_state.add_followup_mode = True
                            st.experimental_rerun()
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
                            st.success(message)
                            # Reset mode tambah follow-up
                            st.session_state.add_followup_mode = False
                            st.session_state.pop('add_followup_activity_id', None)
                            st.experimental_rerun()
                        else:
                            st.error(message)
            
            # Tombol batal
            if st.button("Batal"):
                st.session_state.add_followup_mode = False
                st.session_state.pop('add_followup_activity_id', None)
                st.experimental_rerun()
        else:
            st.error("Aktivitas tidak ditemukan.")
            st.session_state.add_followup_mode = False
            st.session_state.pop('add_followup_activity_id', None)
            st.experimental_rerun()
    else:
        # Tab untuk daftar follow-up dan tambah follow-up
        tab1, tab2 = st.tabs(["Daftar Follow-up", "Tambah Follow-up"])
        
        with tab1:
            # Filter berdasarkan role
            if user['role'] == 'superadmin':
                followups = get_all_followups()
                activities = get_all_marketing_activities()
            else:
                followups = get_followups_by_username(user['username'])
                activities = get_marketing_activities_by_username(user['username'])
            
            if not followups:
                st.info("Belum ada data follow-up.")
            else:
                # Konversi ke DataFrame
                followups_df = pd.DataFrame(followups)
                activities_df = pd.DataFrame(activities)
                
                # Gabungkan dengan data aktivitas untuk mendapatkan nama prospek
                merged_df = followups_df.merge(
                    activities_df[['id', 'prospect_name', 'prospect_location']],
                    left_on='activity_id',
                    right_on='id',
                    how='left',
                    suffixes=('', '_activity')
                )
                
                # Filter dan pencarian
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'status_update' in merged_df.columns:
                        status_options = ['Semua'] + sorted(merged_df['status_update'].unique().tolist())
                        status_filter = st.selectbox("Filter Status", status_options)
                
                with col2:
                    search_term = st.text_input("Cari Prospek", "")
                
                # Terapkan filter
                filtered_df = merged_df.copy()
                
                if status_filter != 'Semua' and 'status_update' in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df['status_update'] == status_filter]
                
                if search_term:
                    filtered_df = filtered_df[
                        filtered_df['prospect_name'].str.contains(search_term, case=False) |
                        filtered_df['prospect_location'].str.contains(search_term, case=False)
                    ]
                
                # Pilih kolom yang ingin ditampilkan
                if user['role'] == 'superadmin':
                    display_columns = ['id', 'marketer_username', 'prospect_name', 'followup_date', 
                                      'next_followup_date', 'interest_level', 'status_update']
                    column_mapping = {
                        'id': 'ID',
                        'marketer_username': 'Marketing',
                        'prospect_name': 'Nama Prospek',
                        'followup_date': 'Tanggal Follow-up',
                        'next_followup_date': 'Jadwal Follow-up Berikutnya',
                        'interest_level': 'Ketertarikan',
                        'status_update': 'Status'
                    }
                else:
                    display_columns = ['id', 'prospect_name', 'followup_date', 
                                      'next_followup_date', 'interest_level', 'status_update']
                    column_mapping = {
                        'id': 'ID',
                        'prospect_name': 'Nama Prospek',
                        'followup_date': 'Tanggal Follow-up',
                        'next_followup_date': 'Jadwal Follow-up Berikutnya',
                        'interest_level': 'Ketertarikan',
                        'status_update': 'Status'
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
                
                # Detail follow-up
                st.subheader("Detail Follow-up")
                selected_id = st.selectbox("Pilih ID Follow-up untuk melihat detail", 
                                          options=filtered_df['id'].tolist())
                
                if selected_id:
                    selected_followup = None
                    for followup in followups:
                        if followup['id'] == selected_id:
                            selected_followup = followup
                            break
                    
                    if selected_followup:
                        # Dapatkan data aktivitas terkait
                        activity = get_activity_by_id(selected_followup['activity_id'])
                        
                        if activity:
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write("**Informasi Prospek**")
                                st.write(f"Nama: {activity['prospect_name']}")
                                st.write(f"Lokasi: {activity['prospect_location']}")
                                st.write(f"Marketing: {selected_followup['marketer_username']}")
                            
                            with col2:
                                st.write("**Informasi Follow-up**")
                                st.write(f"Tanggal Follow-up: {selected_followup['followup_date']}")
                                st.write(f"Jadwal Follow-up Berikutnya: {selected_followup['next_followup_date']}")
                                st.write(f"Tingkat Ketertarikan: {selected_followup['interest_level']}/5")
                                st.write(f"Status: {status_mapping.get(selected_followup['status_update'], selected_followup['status_update'])}")
                            
                            st.write("**Catatan Hasil Follow-up**")
                            st.write(selected_followup['notes'])
                            
                            st.write("**Rencana Tindak Lanjut**")
                            st.write(selected_followup['next_action'])
        
        with tab2:
            st.subheader("Tambah Follow-up Baru")
            
            # Dapatkan daftar aktivitas
            if user['role'] == 'superadmin':
                activities = get_all_marketing_activities()
            else:
                activities = get_marketing_activities_by_username(user['username'])
            
            if not activities:
                st.info("Belum ada aktivitas pemasaran. Tambahkan aktivitas pemasaran terlebih dahulu.")
            else:
                # Buat opsi untuk dropdown
                activity_options = []
                for activity in activities:
                    option_text = f"{activity['prospect_name']} - {activity['prospect_location']} ({activity['id']})"
                    activity_options.append((activity['id'], option_text))
                
                # Form tambah follow-up
                with st.form("add_followup_form_tab"):
                    # Pilih aktivitas
                    selected_activity_id = st.selectbox(
                        "Pilih Aktivitas *",
                        options=[id for id, _ in activity_options],
                        format_func=lambda x: next((text for id, text in activity_options if id == x), x)
                    )
                    
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
                                selected_activity_id, user['username'], followup_date_str,
                                notes, next_action, next_followup_date_str,
                                interest_level, status_update
                            )
                            
                            if success:
                                st.success(message)
                            else:
                                st.error(message)

# Fungsi untuk menampilkan halaman manajemen pengguna (superadmin only)
def show_user_management_page():
    st.title("Manajemen Pengguna")
    
    # Tab untuk daftar pengguna dan tambah pengguna
    tab1, tab2 = st.tabs(["Daftar Pengguna", "Tambah Pengguna"])
    
    with tab1:
        users = get_all_users()
        
        if not users:
            st.info("Belum ada data pengguna.")
        else:
            # Konversi ke DataFrame
            users_df = pd.DataFrame(users)
            
            # Hapus kolom password_hash
            if 'password_hash' in users_df.columns:
                users_df = users_df.drop(columns=['password_hash'])
            
            # Rename kolom untuk tampilan yang lebih baik
            column_mapping = {
                'username': 'Username',
                'name': 'Nama',
                'role': 'Role',
                'email': 'Email',
                'created_at': 'Tanggal Dibuat'
            }
            
            display_df = users_df.rename(columns=column_mapping)
            
            # Mapping role untuk tampilan yang lebih baik
            display_df['Role'] = display_df['Role'].map(lambda x: x.capitalize())
            
            # Tampilkan data
            st.dataframe(display_df, use_container_width=True)
    
    with tab2:
        st.subheader("Tambah Pengguna Baru")
        
        with st.form("add_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("Username *")
                password = st.text_input("Password *", type="password")
                confirm_password = st.text_input("Konfirmasi Password *", type="password")
            
            with col2:
                name = st.text_input("Nama Lengkap *")
                email = st.text_input("Email *")
                role = st.selectbox("Role *", ["marketing", "superadmin"])
            
            submitted = st.form_submit_button("Simpan", use_container_width=True)
            
            if submitted:
                if not username or not password or not confirm_password or not name or not email:
                    st.error("Mohon lengkapi semua field yang wajib diisi (bertanda *).")
                elif password != confirm_password:
                    st.error("Password dan konfirmasi password tidak sama.")
                else:
                    # Tambahkan pengguna baru
                    success, message = add_user(username, password, name, role, email)
                    
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

# Fungsi untuk menampilkan halaman pengaturan (superadmin only)
def show_settings_page():
    st.title("Pengaturan Aplikasi")
    
    # Ambil konfigurasi aplikasi
    config = get_app_config()
    
    if not config:
        st.error("Gagal memuat konfigurasi aplikasi.")
        return
    
    # Tab untuk pengaturan umum dan notifikasi
    tab1, tab2 = st.tabs(["Pengaturan Umum", "Pengaturan Notifikasi"])
    
    with tab1:
        st.subheader("Pengaturan Umum")
        
        with st.form("general_settings_form"):
            app_name = st.text_input("Nama Aplikasi", config['app_settings']['app_name'])
            theme = st.selectbox("Tema", ["light", "dark"], 
                               index=0 if config['app_settings']['theme'] == 'light' else 1)
            date_format = st.text_input("Format Tanggal", config['app_settings']['date_format'])
            
            submitted = st.form_submit_button("Simpan", use_container_width=True)
            
            if submitted:
                # Update konfigurasi
                config['app_settings']['app_name'] = app_name
                config['app_settings']['theme'] = theme
                config['app_settings']['date_format'] = date_format
                
                success, message = update_app_config(config)
                
                if success:
                    st.success(message)
                else:
                    st.error(message)
    
    with tab2:
        st.subheader("Pengaturan Notifikasi")
        
        with st.form("notification_settings_form"):
            enable_email = st.checkbox("Aktifkan Notifikasi Email", 
                                     config['notification_settings']['enable_email'])
            enable_reminder = st.checkbox("Aktifkan Pengingat Follow-up", 
                                        config['notification_settings']['enable_reminder'])
            reminder_days_before = st.number_input("Hari Sebelum Follow-up untuk Pengingat", 
                                                 min_value=1, max_value=7, 
                                                 value=config['notification_settings']['reminder_days_before'])
            
            submitted = st.form_submit_button("Simpan", use_container_width=True)
            
            if submitted:
                # Update konfigurasi
                config['notification_settings']['enable_email'] = enable_email
                config['notification_settings']['enable_reminder'] = enable_reminder
                config['notification_settings']['reminder_days_before'] = reminder_days_before
                
                success, message = update_app_config(config)
                
                if success:
                    st.success(message)
                else:
                    st.error(message)

# Fungsi untuk menampilkan halaman profil (marketing only)
def show_profile_page():
    st.title("Profil Pengguna")
    
    user = st.session_state.user
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Informasi Pengguna**")
        st.write(f"Username: {user['username']}")
        st.write(f"Nama: {user['name']}")
        st.write(f"Email: {user['email']}")
        st.write(f"Role: {user['role'].capitalize()}")
        st.write(f"Tanggal Dibuat: {user['created_at']}")
    
    with col2:
        st.write("**Statistik Aktivitas**")
        
        # Ambil data aktivitas marketing
        activities = get_marketing_activities_by_username(user['username'])
        followups = get_followups_by_username(user['username'])
        
        st.write(f"Total Aktivitas: {len(activities)}")
        st.write(f"Total Follow-up: {len(followups)}")
        
        if activities:
            # Hitung jumlah prospek
            prospect_count = len(set([activity['prospect_name'] for activity in activities]))
            st.write(f"Total Prospek: {prospect_count}")
            
            # Hitung distribusi status
            status_counts = {}
            for activity in activities:
                status = activity['status']
                if status in status_counts:
                    status_counts[status] += 1
                else:
                    status_counts[status] = 1
            
            # Mapping status untuk tampilan yang lebih baik
            status_mapping = {
                'baru': 'Baru',
                'dalam_proses': 'Dalam Proses',
                'berhasil': 'Berhasil',
                'gagal': 'Gagal'
            }
            
            for status, count in status_counts.items():
                st.write(f"{status_mapping.get(status, status)}: {count}")
    
    # Ganti password
    st.subheader("Ganti Password")
    
    with st.form("change_password_form"):
        current_password = st.text_input("Password Saat Ini", type="password")
        new_password = st.text_input("Password Baru", type="password")
        confirm_password = st.text_input("Konfirmasi Password Baru", type="password")
        
        submitted = st.form_submit_button("Simpan", use_container_width=True)
        
        if submitted:
            if not current_password or not new_password or not confirm_password:
                st.error("Mohon lengkapi semua field.")
            elif new_password != confirm_password:
                st.error("Password baru dan konfirmasi password tidak sama.")
            else:
                # Verifikasi password saat ini
                if authenticate_user(user['username'], current_password):
                    # Update password
                    users_file = os.path.join("data", "users.yaml")
                    users_data = read_yaml(users_file)
                    
                    for u in users_data['users']:
                        if u['username'] == user['username']:
                            u['password_hash'] = hash_password(new_password)
                            break
                    
                    write_yaml(users_file, users_data)
                    st.success("Password berhasil diubah.")
                else:
                    st.error("Password saat ini salah.")

# Fungsi utama
def main():
    # Cek login
    logged_in, user = check_login()
    
    # Tambahkan CSS kustom
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #f8f9fa;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #f1f3f5;
            border-radius: 4px 4px 0 0;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #4e73df;
            color: white;
        }
        .stButton>button {
            background-color: #4e73df;
            color: white;
            border-radius: 4px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 500;
        }
        .stButton>button:hover {
            background-color: #3a5ccc;
        }
        .css-1d391kg, .css-12oz5g7 {
            padding-top: 2rem;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )
    
    if not logged_in:
        show_login_page()
    else:
        menu = show_sidebar()
        
        if menu == "Dashboard":
            if user['role'] == 'superadmin':
                show_superadmin_dashboard()
            else:
                show_marketing_dashboard()
        
        elif menu == "Aktivitas Pemasaran":
            show_marketing_activities_page()
        
        elif menu == "Follow-up":
            show_followup_page()
        
        elif menu == "Manajemen Pengguna" and user['role'] == 'superadmin':
            show_user_management_page()
        
        elif menu == "Pengaturan" and user['role'] == 'superadmin':
            show_settings_page()
        
        elif menu == "Profil" and user['role'] == 'marketing':
            show_profile_page()

if __name__ == "__main__":
    main()
