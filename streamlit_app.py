import streamlit as st
import gspread
import json
import pandas as pd
from datetime import date

st.set_page_config(page_title="Daily Salary Entry", page_icon="💰", layout="wide")

st.title("💰 Daily Salary Entry App (Google Sheet)")

# ---------- GOOGLE SHEET AUTH ----------
USE_LOCAL_FILE = False  # change to True if using service_account.json locally

if USE_LOCAL_FILE:
    gc = gspread.service_account(filename="service_account.json")
    SHEET_ID = "PASTE_YOUR_SHEET_ID_HERE"
else:
    sa_json_str = st.secrets["gcp_service_account"]["json"]
    sa_info = json.loads(sa_json_str)
    gc = gspread.service_account_from_dict(sa_info)
    SHEET_ID = st.secrets["gcp_service_account"]["sheet_id"]

# ---------- OPEN SHEET ----------
try:
    sh = gc.open_by_key(SHEET_ID)
    ws = sh.sheet1
except Exception as e:
    st.error(f"❌ Could not open Google Sheet: {e}")
    st.stop()

# ---------- FORM ----------
st.subheader("📝 Add a new entry")

with st.form("entry_form", clear_on_submit=True):
    entry_date = st.date_input("Date", value=date.today())
    name = st.text_input("Worker Name")
    salary = st.number_input("Salary (₹)", min_value=0.0, format="%.2f")
    notes = st.text_area("Notes (optional)")
    submitted = st.form_submit_button("✅ Submit")

if submitted:
    if name.strip() == "":
        st.warning("⚠️ Please enter a worker name.")
    else:
        row = [entry_date.isoformat(), name, salary, notes]
        try:
            ws.append_row(row, value_input_option="USER_ENTERED")
            st.success(f"✅ Entry for {name} saved successfully!")
        except Exception as e:
            st.error(f"❌ Could not save data: {e}")

# ---------- SHOW DATA ----------
st.subheader("📋 Current Records")

try:
    data = ws.get_all_records()
    if data:
        df = pd.DataFrame(data)
        df["Salary"] = pd.to_numeric(df["Salary"], errors="coerce")
        st.dataframe(df)
        total_salary = df["Salary"].sum()
        st.write(f"💵 **Total Salary Recorded:** ₹{total_salary:,.2f}")
        st.write(f"🧍‍♂️ **Total Entries:** {len(df)}")
    else:
        st.info("No data yet — add your first record above!")
except Exception as e:
    st.error(f"❌ Could not load data: {e}")
