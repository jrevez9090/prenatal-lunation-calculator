import streamlit as st
from datetime import datetime, date
from zoneinfo import ZoneInfo, available_timezones
import swisseph as swe
import math

st.set_page_config(page_title="Prenatal Lunation Calculator", layout="centered")

st.title("Prenatal Lunation Calculator (Valens Method)")
st.write("Find the exact prenatal New or Full Moon immediately before birth.")

# ==============================
# INPUT
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

timezones = sorted(list(available_timezones()))
default_index = timezones.index("Europe/Lisbon") if "Europe/Lisbon" in timezones else 0
timezone_str = st.selectbox("Select Timezone", timezones, index=default_index)

# ==============================
# HELPERS
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

def separation(jd):
    sun = swe.calc_ut(jd, swe.SUN)[0][0]
    moon = swe.calc_ut(jd, swe.MOON)[0][0]
    return (moon - sun) % 360

def find_previous_lunation(jd_birth, phase):
    """
    Procura a lunação imediatamente anterior ao nascimento
    usando minimização real da separação.
    """
    search_days = 40
    step = 0.1  # 2.4 horas

    best_jd = None
    best_value = 999

    jd = jd_birth
    end = jd_birth - search_days

    while jd > end:
        jd -= step
        sep = separation(jd)

        if phase == "new":
            value = min(sep, 360 - sep)  # distância ao 0°
        else:
            value = abs(sep - 180)

        if value < best_value:
            best_value = value
            best_jd = jd

    # refinamento fino
    step = 0.001
    for _ in range(2000):
        left = best_jd - step
        right = best_jd + step

        if phase == "new":
            val_left = min(separation(left), 360 - separation(left))
            val_right = min(separation(right), 360 - separation(right))
        else:
            val_left = abs(separation(left) - 180)
            val_right = abs(separation(right) - 180)

        if val_left < best_value:
            best_value = val_left
            best_jd = left
        elif val_right < best_value:
            best_value = val_right
            best_jd = right
        else:
            break

    return best_jd

# ==============================
# CALCULATION
# ==============================

if st.button("Calculate"):

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

    sun_nat = swe.calc_ut(jd_birth, swe.SUN)[0][0]
    moon_nat = swe.calc_ut(jd_birth, swe.MOON)[0][0]

    st.header("Natal Positions")
    st.write("Sun:", to_zodiac(sun_nat))
    st.write("Moon:", to_zodiac(moon_nat))

    diff = (moon_nat - sun_nat) % 360

    if 0 < diff < 180:
        phase = "new"
        st.header("Lunar Phase Classification")
        st.write("After New Moon")
    else:
        phase = "full"
        st.header("Lunar Phase Classification")
        st.write("After Full Moon")

    jd_lun = find_previous_lunation(jd_birth, phase)

    y, m, d, h = swe.revjul(jd_lun)
    hour_lun = int(h)
    minute_lun = int((h - hour_lun) * 60)
    second_lun = int((((h - hour_lun) * 60) - minute_lun) * 60)

    sun_lun = swe.calc_ut(jd_lun, swe.SUN)[0][0]
    moon_lun = swe.calc_ut(jd_lun, swe.MOON)[0][0]

    st.header("Exact Prenatal Lunation")
    st.write(f"Date (UTC): {y}-{m:02d}-{d:02d}")
    st.write(f"Time (UTC): {hour_lun:02d}:{minute_lun:02d}:{second_lun:02d}")
    st.write("Sun at Lunation:", to_zodiac(sun_lun))
    st.write("Moon at Lunation:", to_zodiac(moon_lun))
