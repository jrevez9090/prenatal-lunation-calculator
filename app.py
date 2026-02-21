import streamlit as st
from datetime import datetime
import pytz

st.set_page_config(page_title="Prenatal Lunation Calculator", layout="centered")

st.title("Prenatal Lunation Calculator (Valens Method)")

st.write("Enter birth data to calculate the exact prenatal lunation.")

st.markdown("---")

# ============================
# INPUT SECTION
# ============================

birth_date = st.date_input("Birth Date")
birth_time = st.time_input("Birth Time (local time)")
timezone_str = st.text_input("Timezone (example: Europe/Lisbon)", value="Europe/Lisbon")

st.markdown("---")

if st.button("Prepare Birth Data"):

    try:
        tz = pytz.timezone(timezone_str)

        local_dt = datetime.combine(birth_date, birth_time)
        local_dt = tz.localize(local_dt)

        utc_dt = local_dt.astimezone(pytz.utc)

        st.success("Birth data successfully converted to UTC.")

        st.write("Local time:", local_dt)
        st.write("UTC time:", utc_dt)

        st.session_state.utc_dt = utc_dt

    except Exception as e:
        st.error("Invalid timezone or input.")
