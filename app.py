import streamlit as st
from datetime import datetime
import pytz
import swisseph as swe

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

if st.button("Calculate Sun & Moon Position"):

    try:
        tz = pytz.timezone(timezone_str)

        local_dt = datetime.combine(birth_date, birth_time)
        local_dt = tz.localize(local_dt)
        utc_dt = local_dt.astimezone(pytz.utc)

        st.success("Birth data successfully converted to UTC.")
        st.write("UTC time:", utc_dt)

        # Convert to Julian Day
        jd = swe.julday(
            utc_dt.year,
            utc_dt.month,
            utc_dt.day,
            utc_dt.hour + utc_dt.minute / 60.0
        )

        # Calculate Sun & Moon positions
        sun = swe.calc_ut(jd, swe.SUN)[0][0]
        moon = swe.calc_ut(jd, swe.MOON)[0][0]

        st.markdown("### Ecliptic Longitudes")
        st.write(f"Sun: {sun:.6f}°")
        st.write(f"Moon: {moon:.6f}°")

        st.session_state.jd = jd
        st.session_state.sun = sun
        st.session_state.moon = moon

    except Exception as e:
        st.error("Invalid input or calculation error.")
