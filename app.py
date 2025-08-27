


import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# --------------------------
# Your Google Sheet URL (common link)
# --------------------------
SHEET_URL = "https://docs.google.com/spreadsheets/d/1r6BvQzRE_vYMegpxhOl-0AU0cix4wOLVDc_035eOUsA/edit?usp=sharing"

# --------------------------
# Correct scope for Sheets
# --------------------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# --------------------------
# Authenticate using the service account JSON stored in Streamlit secrets
# --------------------------
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)

gc = gspread.authorize(creds)

# --------------------------
# Open spreadsheet
# --------------------------
sh = gc.open_by_url(SHEET_URL)

# --------------------------
# Load sheets data (cached for 5 min to avoid quota issues)
# --------------------------
@st.cache_data(ttl=300)
def load_data():
    dfs = {}
    for sheet_name in ["Sheet1", "Sheet2", "Sheet3"]:
        df = pd.DataFrame(sh.worksheet(sheet_name).get_all_records())
        # Parse Date column
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y", errors="coerce")
        # Fill NaN with 0 to avoid JSON errors
        df = df.fillna(0)
        dfs[sheet_name] = df
    return dfs

# --------------------------
# Compute daily averages per sheet
# --------------------------
def compute_summary(dfs):
    summary_list = []
    for idx, sheet_name in enumerate(["Sheet1", "Sheet2", "Sheet3"], start=1):
        df = dfs[sheet_name]
        avg_values = df[["Line A", "Line B", "Line C"]].mean(numeric_only=True).fillna(0)
        summary_list.append([
            f"Plant {chr(64+idx)}",
            avg_values["Line A"],
            avg_values["Line B"],
            avg_values["Line C"]
        ])
    summary_df = pd.DataFrame(summary_list, columns=["Plant", "Avg Line A", "Avg Line B", "Avg Line C"])
    return summary_df

# --------------------------
# Write summary to Sheet4
# --------------------------
def write_summary(summary_df):
    ws = sh.worksheet("Sheet4")
    ws.clear()
    ws.update([summary_df.columns.tolist()] + summary_df.values.tolist())

# --------------------------
# Main Streamlit app
# --------------------------
def main():
    st.title("📊 Production Dashboard")

    # Load data (cached)
    dfs = load_data()

    # Show raw data
    st.subheader("Raw Data from Plants")
    for name, df in dfs.items():
        st.write(f"### {name}")
        st.dataframe(df)

    # Compute summary
    summary_df = compute_summary(dfs)
    st.subheader("Summary (Daily Averages)")
    st.dataframe(summary_df)

    # Write to Sheet4
    write_summary(summary_df)
    st.success("Summary written to Sheet4 ✅")

if __name__ == "__main__":
    main()

