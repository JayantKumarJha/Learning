import streamlit as st
import pandas as pd
import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

# --- Google Sheets Authentication ---
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"])
gc = gspread.authorize(creds)

# --- Your Google Sheet link (embed it here) ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1r6BvQzRE_vYMegpxhOl-0AU0cix4wOLVDc_035eOUsA/edit?usp=sharing"

# --- Cached read function (refreshes every 5 minutes) ---
@st.cache_data(ttl=300)
def read_data():
    sh = gc.open_by_url(SHEET_URL)

    df_A = pd.DataFrame(sh.worksheet("Sheet1").get_all_records())
    df_B = pd.DataFrame(sh.worksheet("Sheet2").get_all_records())
    df_C = pd.DataFrame(sh.worksheet("Sheet3").get_all_records())

    return df_A, df_B, df_C, sh

# --- App main ---
st.title("📊 Plant Production Dashboard")

df_A, df_B, df_C, sh = read_data()

# Calculate summaries
summary_A = df_A.mean(numeric_only=True)
summary_B = df_B.mean(numeric_only=True)
summary_C = df_C.mean(numeric_only=True)

summary_df = pd.DataFrame({
    "Plant": ["Plant A", "Plant B", "Plant C"],
    "Daily Avg": [summary_A.mean(), summary_B.mean(), summary_C.mean()]
})

# Show results in app
st.subheader("Daily Average Production")
st.dataframe(summary_df)

# --- Write to Sheet4 ---
worksheet_summary = sh.worksheet("Sheet4")
worksheet_summary.clear()
worksheet_summary.update([summary_df.columns.values.tolist()] + summary_df.values.tolist())

st.success("✅ Summary written to Sheet4 successfully")

