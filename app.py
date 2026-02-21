import streamlit as st
from datetime import datetime, date
import pytz
import swisseph as swe

st.set_page_config(page_title="Prenatal Lunation Calculator", layout="centered")

st.title("Prenatal Lunation Calculator (Valens Method)")

st.write("Enter birth data to calculate the exact prenatal lunation.")
st.markdown("---")

# ============================
# INPUT SECTION
# ============================

birth_date = st.date_input(
    "Birth Date",
    value=date(1990, 1, 1),
    min_value=date(1800, 1, 1),
    max_value=date(2100, 12, 31)
)

col1, col2, col3 = st.columns(3)

with col1:
    hour = st.number_input("Hour", min_value=0, max_value=23, value=12)

with col2:
    minute = st.number_input("Minute", min_value=0, max_value=59, value=0)

with col3:
    second = st.number_input("Second", min_value=0, max_value=59, value=0)

timezone_str = st.text_input("Timezone (example: Europe/Lisbon)", value="Europe/Lisbon")

st.markdown("---")

# ============================
# CALCULATION
# ============================

if st.button("Calculate Sun & Moon Position"):

    try:
        # Timezone handling
        tz = pytz.timezone(timezone_str)

        local_dt = datetime(
            birth_date.year,
            birth_date.month,
            birth_date.day,
            int(hour),
            int(minute),
            int(second)
        )

        local_dt = tz.localize(local_dt)
        utc_dt = local_dt.astimezone(pytz.utc)

        st.success("Birth data successfully converted to UTC.")
        st.write("UTC time:", utc_dt)

        # Convert to Julian Day
        jd = swe.julday(
            utc_dt.year,
            utc_dt.month,
            utc_dt.day,
            utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
        )

        # Calculate Sun & Moon
        sun = swe.calc_ut(jd, swe.SUN)[0][0]
        moon = swe.calc_ut(jd, swe.MOON)[0][0]

        st.markdown("### Ecliptic Longitudes (Geocentric)")
        st.write(f"Sun: {sun:.6f}°")
        st.write(f"Moon: {moon:.6f}°")

        # Determine lunar phase (basic)
        diff = (moon - sun) % 360
        phase_type = "After New Moon" if diff < 180 else "After Full Moon"

        st.markdown("### Lunar Phase Classification")
        st.write(phase_type)

        # Store for next steps
        st.session_state.jd = jd
        st.session_state.sun = sun
        st.session_state.moon = moon
        st.session_state.phase_type = phase_type

    except Exception as e:
        st.error("Invalid input or calculation error.")
