import gspread

def backup_data():
    try:
        gc = gspread.service_account("service_account_key.json")
        sheet = gc.open_by_key("1SdEX5TzMzKfKcE1oCuaez2ctxgIxwwipkk9NT0jOYtI").sheet1
        
        # Ambil data dari database
        activities = get_all_marketing_activities()  # Fungsi yang sudah ada
        
        # Format data sederhana
        data = [[
            a["id"], a["prospect_name"], a["prospect_location"], 
            a["activity_date"], a["status"], a["marketer_username"]
        ] for a in activities]
        
        # Update sheet (clear + isi ulang)
        sheet.clear()
        sheet.update("A1", [["ID", "Nama Prospek", "Lokasi", "Tanggal", "Status", "Marketing"]])
        sheet.update("A2", data)
        
        print("✅ Backup berhasil!")
    except Exception as e:
        print(f"❌ Error: {e}")