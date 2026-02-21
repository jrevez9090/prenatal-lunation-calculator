import streamlit as st
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo, available_timezones
import swisseph as swe
import math

st.set_page_config(page_title="Prenatal Lunation Calculator", layout="centered")

st.title("Prenatal Lunation Calculator (Valens Method)")
st.write("Calculate exact prenatal New or Full Moon.")

# ==============================
# DATE INPUT
# ==============================

birth_date = st.date_input(
    "Birth Date",
    value=date(1990, 1, 1),
    min_value=date(1, 1, 1),
    max_value=date(3000, 12, 31)
)

col1, col2, col3 = st.columns(3)
hour = col1.number_input("Hour", 0, 23, 12)
minute = col2.number_input("Minute", 0, 59, 0)
second = col3.number_input("Second", 0, 59, 0)

# ==============================
# TIMEZONE SELECT
# ==============================

timezones = sorted(list(available_timezones()))
default_index = timezones.index("Europe/Lisbon") if "Europe/Lisbon" in timezones else 0

timezone_str = st.selectbox("Select Timezone", timezones, index=default_index)

# ==============================
# HELPER FUNCTIONS
# ==============================

def to_zodiac(deg):
    signs = [
        "Aries","Taurus","Gemini","Cancer",
        "Leo","Virgo","Libra","Scorpio",
        "Sagittarius","Capricorn","Aquarius","Pisces"
    ]
    deg = deg % 360
    sign_index = int(deg // 30)
    sign_deg = deg % 30
    d = int(sign_deg)
    m_float = (sign_deg - d) * 60
    m = int(m_float)
    s = int((m_float - m) * 60)
    return f"{d:02d}º{m:02d}'{s:02d}'' {signs[sign_index]}"

def signed_angle_diff(sun, moon):
    diff = (moon - sun) % 360
    if diff > 180:
        diff -= 360
    return diff

def find_exact_lunation(jd_birth, phase="new"):
    step = 0.1
    jd = jd_birth

    while True:
        jd -= step
        sun = swe.calc_ut(jd, swe.SUN)[0][0]
        moon = swe.calc_ut(jd, swe.MOON)[0][0]
        diff = signed_angle_diff(sun, moon)

        if phase == "new":
            if abs(diff) < 1:
                break
        else:
            if abs(abs(diff) - 180) < 1:
                break

    # refine
    step = 0.001
    while True:
        jd -= step
        sun = swe.calc_ut(jd, swe.SUN)[0][0]
        moon = swe.calc_ut(jd, swe.MOON)[0][0]
        diff = signed_angle_diff(sun, moon)

        if phase == "new":
            if abs(diff) < 0.01:
                break
        else:
            if abs(abs(diff) - 180) < 0.01:
                break

    return jd

# ==============================
# CALCULATION
# ==============================

if st.button("Calculate"):

    try:
        local_dt = datetime(
            birth_date.year,
            birth_date.month,
            birth_date.day,
            hour,
            minute,
            second,
            tzinfo=ZoneInfo(timezone_str)
        )

        utc_dt = local_dt.astimezone(ZoneInfo("UTC"))
        st.success("Birth data successfully converted to UTC.")
        st.write("UTC time:", utc_dt)

        jd_birth = swe.julday(
            utc_dt.year,
            utc_dt.month,
            utc_dt.day,
            utc_dt.hour + utc_dt.minute/60 + utc_dt.second/3600
        )

        # Natal positions
        sun_nat = swe.calc_ut(jd_birth, swe.SUN)[0][0]
        moon_nat = swe.calc_ut(jd_birth, swe.MOON)[0][0]

        st.header("Natal Positions")
        st.write("Sun:", to_zodiac(sun_nat))
        st.write("Moon:", to_zodiac(moon_nat))

        # Phase classification
        diff = signed_angle_diff(sun_nat, moon_nat)

        if abs(diff) < 90:
            phase = "new"
            st.header("Lunar Phase Classification")
            st.write("After New Moon")
        else:
            phase = "full"
            st.header("Lunar Phase Classification")
            st.write("After Full Moon")

        # Find exact prenatal lunation
        jd_lun = find_exact_lunation(jd_birth, phase)

        y, m, d, h = swe.revjul(jd_lun)
        hour_lun = int(h)
        minute_lun = int((h - hour_lun) * 60)

        sun_lun = swe.calc_ut(jd_lun, swe.SUN)[0][0]
        moon_lun = swe.calc_ut(jd_lun, swe.MOON)[0][0]

        st.header("Exact Prenatal Lunation")
        st.write(f"Date (UTC): {y}-{m:02d}-{d:02d}")
        st.write(f"Time (UTC): {hour_lun:02d}:{minute_lun:02d}")

        st.write("Sun at Lunation:", to_zodiac(sun_lun))
        st.write("Moon at Lunation:", to_zodiac(moon_lun))

    except Exception as e:
        st.error("Calculation error.")
        st.write(str(e))
