import gspread
from utils_with_edit_delete import get_all_marketing_activities

def backup_data():
    """Backup data ke Google Sheets"""
    try:
        # 1. Autentikasi
        gc = gspread.service_account("service_account_key.json")
        
        # 2. Buka spreadsheet (ganti dengan ID Anda)
        sheet = gc.open_by_key("1SdEX5TzMzKfKcE1oCuaez2ctxgIxwwipkk9NT0jOYtI").sheet1
        
        # 3. Ambil data terbaru
        activities = get_all_marketing_activities()
        
        # 4. Format data
        data = [[
            a.get("id", ""),
            a.get("prospect_name", ""),
            a.get("prospect_location", ""),
            a.get("activity_date", ""),
            a.get("status", ""),
            a.get("marketer_username", "")
        ] for a in activities]
        
        # 5. Update sheet
        sheet.clear()
        sheet.update("A1", [["ID", "Nama Prospek", "Lokasi", "Tanggal", "Status", "Marketing"]])
        sheet.update("A2", data)
        
        return True
    except Exception as e:
        print("⚠️ Backup gagal:", e)
        return False