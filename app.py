import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

st.set_page_config(page_title="Production Summary", layout="wide")

# --- 1. Load credentials from .streamlit/secrets.toml ---
creds_dict = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets"])

# --- 2. Connect to Google Sheets ---
gc = gspread.authorize(creds)

# Replace these with your actual sheet URLs
A_link = "https://docs.google.com/spreadsheets/d/1r6BvQzRE_vYMegpxhOl-0AU0cix4wOLVDc_035eOUsA/edit?gid=0#gid=0"
B_link = "https://docs.google.com/spreadsheets/d/1r6BvQzRE_vYMegpxhOl-0AU0cix4wOLVDc_035eOUsA/edit?gid=801337031#gid=801337031"
C_link = "https://docs.google.com/spreadsheets/d/1r6BvQzRE_vYMegpxhOl-0AU0cix4wOLVDc_035eOUsA/edit?gid=1333453642#gid=1333453642"
D_link = "https://docs.google.com/spreadsheets/d/1r6BvQzRE_vYMegpxhOl-0AU0cix4wOLVDc_035eOUsA/edit?gid=9246028#gid=9246028"

# --- 3. Read data from the first 3 sheets ---
def read_sheet(sheet_url):
    sh = gc.open_by_url(sheet_url)
    ws = sh.sheet1
    data = ws.get_all_records()
    return pd.DataFrame(data)

df_A = read_sheet(A_link)
df_B = read_sheet(B_link)
df_C = read_sheet(C_link)

# --- 4. Calculate daily averages ---
def calculate_daily_average(df):
    df["Date"] = pd.to_datetime(df["Date"])
    avg_df = df.groupby("Date").mean().reset_index()
    return avg_df

avg_A = calculate_daily_average(df_A)
avg_B = calculate_daily_average(df_B)
avg_C = calculate_daily_average(df_C)

# --- 5. Combine results ---
summary = (
    pd.concat([avg_A.assign(Plant="A"),
               avg_B.assign(Plant="B"),
               avg_C.assign(Plant="C")])
    .reset_index(drop=True)
)

# --- 6. Write summary to the 4th sheet ---
def write_to_summary(sheet_url, df):
    sh = gc.open_by_url(sheet_url)
    ws = sh.sheet1
    ws.clear()
    ws.update([df.columns.values.tolist()] + df.values.tolist())

write_to_summary(D_link, summary)

# --- 7. Show in Streamlit UI ---
st.title("📊 Production Summary")
st.dataframe(summary)
