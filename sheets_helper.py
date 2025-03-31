import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials

def get_sheet_data():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]

    creds_json = json.loads(os.environ.get("GOOGLE_CREDS"))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    client = gspread.authorize(creds)

    print("📂 Feuilles disponibles pour le bot :")
    for f in client.list_spreadsheet_files():
        print("-", f["name"])

    sheet = client.open("Patients").sheet1
    return sheet.get_all_records()

def find_patient(patient_input):
    data = get_sheet_data()
    patient_input = patient_input.strip().lower()

    for row in data:
        patient_id = str(row.get("patient_id", "")).strip().lower()
        prenom = row.get("prenom", "").strip().lower()

        if patient_input == patient_id or patient_input == prenom:
            return row
    return None

def find_patient_by_phone(phone_number):
    data = get_sheet_data()
    normalized = phone_number.replace("+33", "0").replace(" ", "")
    for row in data:
        tel = row.get("telephone", "").replace(" ", "").replace("+33", "0")
        if tel == normalized:
            return row
    return None
