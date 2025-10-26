import streamlit as st
import gspread
import json
import pandas as pd
from datetime import date

# ------------------ Streamlit Page ------------------
st.set_page_config(page_title="Daily Salary Entry", page_icon="💰", layout="wide")
st.title("💰 Daily Salary Entry App (Google Sheet)")

# ------------------ Google Sheet Auth ------------------
try:
    # Load service account from Streamlit secrets
    sa_json_str = st.secrets["gcp_service_account"]["json"]
    sa_info = json.loads(sa_json_str)
    gc = gspread.service_account_from_dict(sa_info)

    # Get sheet by ID
    SHEET_ID = st.secrets["gcp_service_account"]["sheet_id"]
    sh = gc.open_by_key(SHEET_ID)
    ws = sh.sheet1

except Exception as e:
    st.error(f"❌ Could not connect to Google Sheet: {e}")
    st.stop()

# ------------------ Create Headers if Empty ------------------
if ws.get_all_values() == []:
    headers = ["Date", "Name", "Salary", "Notes"]
    ws.append_row(headers)

# ------------------ Data Entry Form ------------------
st.subheader("📝 Add a new entry")

with st.form("entry_form", clear_on_submit=True):
    name = st.text_input("Worker Name")
    salary = st.number_input("Salary (₹)", min_value=0.0, format="%.2f")
    notes = st.text_area("Notes (optional)")
    submitted = st.form_submit_button("✅ Submit")

if submitted:
    if name.strip() == "":
        st.warning("⚠️ Please enter a worker name.")
    else:
        today = date.today().isoformat()
        row = [today, name, salary, notes]
        try:
            ws.append_row(row, value_input_option="USER_ENTERED")
            st.success(f"✅ Entry for {name} saved successfully!")
        except Exception as e:
            st.error(f"❌ Could not save data: {e}")

# ------------------ Display Current Records ------------------
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
