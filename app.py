import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ------------------------
# Hardcoded Google Sheet URLs
SHEET_A_URL = "https://docs.google.com/spreadsheets/d/1r6BvQzRE_vYMegpxhOl-0AU0cix4wOLVDc_035eOUsA/edit?gid=0#gid=0"
SHEET_B_URL = "https://docs.google.com/spreadsheets/d/1r6BvQzRE_vYMegpxhOl-0AU0cix4wOLVDc_035eOUsA/edit?gid=801337031#gid=801337031"
SHEET_C_URL = "https://docs.google.com/spreadsheets/d/1r6BvQzRE_vYMegpxhOl-0AU0cix4wOLVDc_035eOUsA/edit?gid=1333453642#gid=1333453642"
SUMMARY_URL = "https://docs.google.com/spreadsheets/d/1r6BvQzRE_vYMegpxhOl-0cix4wOLVDc_035eOUsA/edit?gid=9246028#gid=9246028"

# ------------------------
# Hardcoded service account credentials
# ------------------------
SERVICE_ACCOUNT_INFO = {
  "type": "service_account",
  "project_id": "my-project-learning-468310",
  "private_key_id": "YOUR_PRIVATE_KEY_ID",
  "private_key": "-----BEGIN PRIVATE KEY-----\nYOURPRIVATEKEY\n-----END PRIVATE KEY-----\n",
  "client_email": "demo-383@my-project-learning-468310.iam.gserviceaccount.com",
  "client_id": "115965891258217840622",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/demo-383%40my-project-learning-468310.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# ------------------------
# Authenticate and create gspread client
# ------------------------
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
client = gspread.authorize(credentials)

# ------------------------
# Functions
# ------------------------
def read_sheet(sheet_url):
    sheet = client.open_by_url(sheet_url)
    worksheet = sheet.get_worksheet(0)
    df = pd.DataFrame(worksheet.get_all_records())
    df['Date'] = pd.to_datetime(df['Date'])
    return df

def write_summary(df, summary_url):
    summary_sheet = client.open_by_url(summary_url)
    worksheet = summary_sheet.get_worksheet(0)
    worksheet.clear()
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

def calculate_daily_averages(df, plant_name):
    df['Average'] = df[['Line A', 'Line B', 'Line C']].mean(axis=1)
    df['Plant'] = plant_name
    return df[['Date', 'Plant', 'Average']]

# ------------------------
# Main App
# ------------------------
st.title("📊 Daily Average Production Dashboard")

try:
    # Use the correct variables
    df1 = read_sheet(SHEET_A_URL)
    df2 = read_sheet(SHEET_B_URL)
    df3 = read_sheet(SHEET_C_URL)

    avg1 = calculate_daily_averages(df1, 'Plant A')
    avg2 = calculate_daily_averages(df2, 'Plant B')
    avg3 = calculate_daily_averages(df3, 'Plant C')

    full_summary = pd.concat([avg1, avg2, avg3], ignore_index=True)
    full_summary.sort_values('Date', inplace=True)

    # Write summary back
    write_summary(full_summary, SUMMARY_URL)

    st.success("✅ Daily averages calculated and written to summary sheet.")
    st.dataframe(full_summary)

except Exception as e:
    st.error(f"❌ Error: {e}")
