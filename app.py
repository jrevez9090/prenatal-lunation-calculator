import streamlit as st
from datetime import datetime, date
from zoneinfo import ZoneInfo, available_timezones
import swisseph as swe

st.set_page_config(page_title="Prenatal Lunation Calculator", layout="centered")

st.title("Prenatal Lunation Calculator (Valens Method)")
st.write("Calculate the exact prenatal New or Full Moon immediately preceding birth.")

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

def find_last_lunation(jd_birth, phase):
    step = 0.25  # 6 horas
    jd = jd_birth
    prev_diff = None

    while True:
        jd -= step
        sun = swe.calc_ut(jd, swe.SUN)[0][0]
        moon = swe.calc_ut(jd, swe.MOON)[0][0]
        diff = (moon - sun) % 360

        if prev_diff is not None:

            if phase == "new":
                # detect crossing near 0°
                if prev_diff > 300 and diff < 60:
                    break

            else:
                # detect crossing near 180°
                if (prev_diff < 180 and diff >= 180) or (prev_diff > 180 and diff <= 180):
                    break

        prev_diff = diff

    # refine search
    step = 0.01
    for _ in range(1000):
        jd -= step
        sun = swe.calc_ut(jd, swe.SUN)[0][0]
        moon = swe.calc_ut(jd, swe.MOON)[0][0]
        diff = (moon - sun) % 360

        if phase == "new":
            if abs(diff) < 0.001 or abs(diff - 360) < 0.001:
                break
        else:
            if abs(diff - 180) < 0.001:
                break

    return jd

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

    jd_lun = find_last_lunation(jd_birth, phase)

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
