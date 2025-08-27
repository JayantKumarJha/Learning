import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# --- Your Google Sheet URL (common link) ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1r6BvQzRE_vYMegpxhOl-0AU0cix4wOLVDc_035eOUsA/edit?usp=sharing"

# --- Scopes required for Sheets + Drive ---
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# --- Authenticate with secrets JSON ---
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=SCOPES
)
gc = gspread.authorize(creds)

# --- Open the spreadsheet only once ---
sh = gc.open_by_url(SHEET_URL)

# Cache results for 5 minutes to avoid quota exhaustion
@st.cache_data(ttl=300)
def load_data():
    df_A = pd.DataFrame(sh.worksheet("Sheet1").get_all_records())
    df_B = pd.DataFrame(sh.worksheet("Sheet2").get_all_records())
    df_C = pd.DataFrame(sh.worksheet("Sheet3").get_all_records())
    return df_A, df_B, df_C

# --- Compute summary and update Sheet4 ---
def update_summary(df_A, df_B, df_C):
    summary_ws = sh.worksheet("Sheet4")

    # Example: compute daily averages across 3 plants
    avg_A = df_A.mean(numeric_only=True)
    avg_B = df_B.mean(numeric_only=True)
    avg_C = df_C.mean(numeric_only=True)

    summary_df = pd.DataFrame({
        "Plant": ["A", "B", "C"],
        "Average": [avg_A.mean(), avg_B.mean(), avg_C.mean()]
    })

    # Clear and update Sheet4
    summary_ws.clear()
    summary_ws.update([summary_df.columns.values.tolist()] + summary_df.values.tolist())
    return summary_df

# --- Streamlit UI ---
st.title("📊 Production Dashboard")

df_A, df_B, df_C = load_data()
summary_df = update_summary(df_A, df_B, df_C)

st.subheader("Summary (written to Sheet4)")
st.dataframe(summary_df)


