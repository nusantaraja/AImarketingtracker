# Fungsi untuk menampilkan dashboard marketing
def show_marketing_dashboard():
    st.title("DASHBOARD MARKETING")
    user = st.session_state.user
    username = user["username"]

    # Ambil data aktivitas marketing
    activities = get_marketing_activities_by_username(username)
    followups = get_followups_by_username(username)

    # Jika tidak ada data, tampilkan pesan
    if not activities:
        st.info("Anda belum memiliki aktivitas pemasaran. Tambahkan aktivitas pemasaran terlebih dahulu.")
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

    # Aktivitas per jenis
    if not activities_df.empty and "activity_type" in activities_df.columns:
        st.subheader("Distribusi Jenis Aktivitas Anda")
        type_counts = activities_df["activity_type"].value_counts().reset_index()
        type_counts.columns = ["Jenis Aktivitas", "Jumlah"]
        fig = px.pie(type_counts, values="Jumlah", names="Jenis Aktivitas", title="Distribusi Jenis Aktivitas Anda", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Belum ada data jenis aktivitas untuk ditampilkan.")

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

