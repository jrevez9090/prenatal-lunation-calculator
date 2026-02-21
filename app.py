import streamlit as st
from datetime import datetime, date
import pytz
import swisseph as swe

st.set_page_config(page_title="Prenatal Lunation Calculator", layout="centered")

st.title("Prenatal Lunation Calculator (Valens Method)")
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
# ASTRONOMICAL FUNCTIONS
# ============================

def sun_moon_diff_signed(jd):
    sun = swe.calc_ut(jd, swe.SUN)[0][0]
    moon = swe.calc_ut(jd, swe.MOON)[0][0]
    diff = (moon - sun + 180) % 360 - 180
    return diff


def find_previous_lunation(jd_birth, phase_type):

    jd_high = jd_birth
    step = 1 / 24  # 1 hour

    # Step backwards until we bracket the event
    while True:
        jd_low = jd_high - step
        diff_high = sun_moon_diff_signed(jd_high)
        diff_low = sun_moon_diff_signed(jd_low)

        if phase_type == "After New Moon":
            if diff_high > 0 and diff_low <= 0:
                break
        else:
            if diff_high < 0 and diff_low >= 0:
                break

        jd_high = jd_low

    # Bisection refinement
    for _ in range(50):
        jd_mid = (jd_low + jd_high) / 2
        diff_mid = sun_moon_diff_signed(jd_mid)

        if phase_type == "After New Moon":
            if diff_mid > 0:
                jd_high = jd_mid
            else:
                jd_low = jd_mid
        else:
            if diff_mid < 0:
                jd_high = jd_mid
            else:
                jd_low = jd_mid

    return (jd_low + jd_high) / 2


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
# MAIN CALCULATION
# ============================

if st.button("Calculate Prenatal Lunation"):

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

        jd = swe.julday(
            utc_dt.year,
            utc_dt.month,
            utc_dt.day,
            utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
        )

        # Natal positions
        sun = swe.calc_ut(jd, swe.SUN)[0][0]
        moon = swe.calc_ut(jd, swe.MOON)[0][0]

        st.markdown("### Natal Positions")
        st.write(f"Sun: {decimal_to_zodiac(sun)}")
        st.write(f"Moon: {decimal_to_zodiac(moon)}")

        diff = (moon - sun) % 360
        phase_type = "After New Moon" if diff < 180 else "After Full Moon"

        st.markdown("### Lunar Phase Classification")
        st.write(phase_type)

        # Find exact lunation
        lunation_jd = find_previous_lunation(jd, phase_type)

        sun_lun = swe.calc_ut(lunation_jd, swe.SUN)[0][0]
        moon_lun = swe.calc_ut(lunation_jd, swe.MOON)[0][0]

        y, m, d, ut = swe.revjul(lunation_jd)
        h = int(ut)
        min_lun = int((ut - h) * 60)

        st.markdown("### Exact Prenatal Lunation")
        st.write(f"Date (UTC): {int(y)}-{int(m):02d}-{int(d):02d}")
        st.write(f"Time (UTC): {h:02d}:{min_lun:02d}")
        st.write(f"Sun at Lunation: {decimal_to_zodiac(sun_lun)}")
        st.write(f"Moon at Lunation: {decimal_to_zodiac(moon_lun)}")

    except Exception as e:
        st.error("Invalid input or calculation error.")
