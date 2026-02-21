import streamlit as st
from datetime import datetime, date
import pytz
import swisseph as swe

st.set_page_config(page_title="Prenatal Lunation Calculator", layout="centered")

st.title("Prenatal Lunation Calculator")
st.write("Enter birth data to calculate the exact prenatal lunation.")
st.markdown("---")

# ============================
# ZODIAC UTILITIES
# ============================

signs = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def decimal_to_zodiac(decimal_degree):
    decimal_degree = decimal_degree % 360
    sign_index = int(decimal_degree // 30)
    sign_name = signs[sign_index]

    degree_in_sign = decimal_degree % 30
    degrees = int(degree_in_sign)

    minutes_full = (degree_in_sign - degrees) * 60
    minutes = int(minutes_full)

    seconds = int(round((minutes_full - minutes) * 60))

    # Ajuste caso segundos arredondem para 60
    if seconds == 60:
        seconds = 0
        minutes += 1
    if minutes == 60:
        minutes = 0
        degrees += 1
    if degrees == 30:
        degrees = 0
        sign_index = (sign_index + 1) % 12
        sign_name = signs[sign_index]

    return f"{degrees:02d}º{minutes:02d}'{seconds:02d}'' {sign_name}"

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
    hour = st.number_input("Hour", 0, 23, 12)

with col2:
    minute = st.number_input("Minute", 0, 59, 0)

with col3:
    second = st.number_input("Second", 0, 59, 0)

timezone_str = st.text_input("Timezone (example: Europe/Lisbon)", value="Europe/Lisbon")

st.markdown("---")

# ============================
# CALCULATION
# ============================

if st.button("Calculate Sun & Moon Position"):

    try:
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

        # Calculate geocentric longitudes
        sun = swe.calc_ut(jd, swe.SUN)[0][0]
        moon = swe.calc_ut(jd, swe.MOON)[0][0]

        # Convert to zodiac format
        sun_zodiac = decimal_to_zodiac(sun)
        moon_zodiac = decimal_to_zodiac(moon)

        st.markdown("### Ecliptic Longitudes (Zodiac Format)")
        st.write(f"Sun: {sun_zodiac}")
        st.write(f"Moon: {moon_zodiac}")

        # Lunar phase classification
        diff = (moon - sun) % 360
        if diff < 180:
            phase_type = "After New Moon"
        else:
            phase_type = "After Full Moon"

        st.markdown("### Lunar Phase Classification")
        st.write(phase_type)

        # Store values for next steps
        st.session_state.jd = jd
        st.session_state.sun = sun
        st.session_state.moon = moon
        st.session_state.phase_type = phase_type

    except Exception as e:
        st.error("Invalid input or calculation error.")
