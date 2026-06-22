import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import requests
import math

st.set_page_config(page_title="What Have You Lost?", page_icon="✦", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Space+Grotesk:wght@300;400;500;600&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #03030a; }
    section[data-testid="stSidebar"] { display: none; }
    .main .block-container { max-width: 900px; margin: 0 auto; padding: 4rem 2rem; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; color: white !important; font-weight: 300 !important; letter-spacing: 0.05em !important; }
    .stTextInput input { background-color: #0d0d1a !important; border: 1px solid #222244 !important; border-radius: 4px !important; color: white !important; padding: 0.75rem 1rem !important; font-size: 16px !important; }
    .stButton button { background-color: transparent !important; border: 1px solid #4444AA !important; border-radius: 4px !important; color: #8888CC !important; padding: 0.75rem 2rem !important; font-size: 14px !important; letter-spacing: 0.15em !important; text-transform: uppercase !important; width: 100% !important; }
    .stButton button:hover { background-color: #4444AA22 !important; color: white !important; }
    .stMetric { background-color: #0d0d1a !important; border: 1px solid #111133 !important; border-radius: 4px !important; padding: 1.5rem !important; }
    .stMetric label { color: #555577 !important; font-size: 11px !important; letter-spacing: 0.15em !important; text-transform: uppercase !important; }
    .stMetric [data-testid="stMetricValue"] { color: white !important; font-size: 2rem !important; font-weight: 300 !important; }
    hr { border-color: #111133 !important; margin: 3rem 0 !important; }
</style>
""", unsafe_allow_html=True)

STARS = [
    ("Sirius",          -1.46,  6.752, -16.716),
    ("Arcturus",        -0.05, 14.261,  19.182),
    ("Vega",             0.03, 18.615,  38.784),
    ("Rigel",            0.13,  5.242,  -8.202),
    ("Procyon",          0.34,  7.655,   5.225),
    ("Betelgeuse",       0.42,  5.919,   7.407),
    ("Altair",           0.76, 19.846,   8.868),
    ("Aldebaran",        0.87,  4.599,  16.509),
    ("Antares",          1.06, 16.490, -26.432),
    ("Spica",            1.04, 13.420, -11.161),
    ("Pollux",           1.16,  7.755,  28.026),
    ("Fomalhaut",        1.17, 22.961, -29.622),
    ("Deneb",            1.25, 20.691,  45.280),
    ("Regulus",          1.36, 10.139,  11.967),
    ("Adhara",           1.50,  6.977, -28.972),
    ("Castor",           1.58,  7.577,  31.888),
    ("Bellatrix",        1.64,  5.419,   6.350),
    ("Elnath",           1.65,  5.438,  28.608),
    ("Alnilam",          1.70,  5.603,  -1.202),
    ("Alioth",           1.76, 12.900,  55.960),
    ("Mirfak",           1.79,  3.406,  49.861),
    ("Dubhe",            1.81, 11.062,  61.751),
    ("Alkaid",           1.85, 13.792,  49.313),
    ("Peacock",          1.94, 20.427, -56.735),
    ("Polaris",          1.97,  2.530,  89.264),
    ("Hamal",            2.01,  2.120,  23.463),
    ("Alpheratz",        2.07,  0.140,  29.091),
    ("Kochab",           2.07, 14.845,  74.156),
    ("Algol",            2.09,  3.136,  40.957),
    ("Denebola",         2.14, 11.818,  14.572),
    ("Alphecca",         2.22, 15.578,  26.715),
    ("Mintaka",          2.23,  5.534,  -0.299),
    ("Schedar",          2.24,  0.675,  56.537),
    ("Phad",             2.40, 11.897,  53.695),
    ("Izar",             2.35, 14.749,  27.074),
    ("Mizar",            2.23, 13.399,  54.926),
    ("Muphrid",          2.68, 13.911,  18.398),
    ("Porrima",          2.74, 12.694,  -1.449),
    ("Sabik",            2.87, 17.173, -15.724),
    ("Cor Caroli",       2.89, 12.934,  38.318),
    ("Megrez",           3.31, 12.257,  57.033),
    ("Segin",            3.38,  0.945,  63.670),
    ("Tania Borealis",   3.45, 10.285,  42.914),
    ("Alula Australis",  3.67, 11.307,  31.529),
    ("Fulu",             3.66,  0.317,  77.274),
    ("Albali",           3.77, 20.794,  -9.496),
    ("Andromeda Galaxy", 3.44,  0.712,  41.269),
    ("Beehive Cluster",  3.70,  8.667,  19.621),
    ("Omega Centauri",   3.90, 13.447, -47.479),
    ("Acubens",          3.94,  8.975,  11.858),
    ("Propus",           3.97,  6.269,  22.506),
    ("Castula",          3.97,  0.945,  63.670),
    ("Marfak",           3.98,  2.859,  55.896),
    ("Alzirr",           3.99,  6.754,  12.896),
    ("Alula Borealis",   3.99, 11.294,  33.094),
    ("Jabbah",           4.00, 16.200, -19.460),
    ("Orion Nebula",     4.00,  5.588,  -5.390),
    ("Mekbuda",          4.01,  7.069,  20.570),
    ("Deneb el Okab",    4.02, 19.090,  13.863),
    ("47 Tucanae",       4.09,  0.402, -72.081),
    ("Ancha",            4.17, 22.277,  -7.783),
    ("Chara",            4.26, 12.270,  41.358),
    ("Asterion",         4.26, 13.121,  35.945),
    ("NGC 869",          4.30,  2.322,  57.133),
    ("Paikauhale",       4.35, 17.622, -43.239),
    ("Situla",           4.42, 22.491,  -8.982),
    ("Iota Leporis",     4.45,  5.207, -11.869),
    ("M41",              4.50,  6.767, -20.759),
    ("Gamma Pictoris",   4.51,  5.830, -56.167),
]

LOST_COLORS = [
    "#FF6B6B", "#FF9F43", "#FECA57", "#2ED573", "#48DBFB",
    "#FF6348", "#A29BFE", "#FD79A8", "#7BED9F", "#ECCC68"
]

CONSTELLATION_LINES = [
    ("Betelgeuse", "Bellatrix"),
    ("Bellatrix", "Mintaka"),
    ("Mintaka", "Alnilam"),
    ("Betelgeuse", "Alnilam"),
    ("Rigel", "Mintaka"),
    ("Rigel", "Alnilam"),
    ("Betelgeuse", "Orion Nebula"),
    ("Mintaka", "Orion Nebula"),
    ("Sirius", "Adhara"),
    ("Sirius", "M41"),
    ("Procyon", "Sirius"),
    ("Castor", "Pollux"),
    ("Pollux", "Alzirr"),
    ("Castor", "Mekbuda"),
    ("Mekbuda", "Alzirr"),
    ("Propus", "Castor"),
    ("Aldebaran", "Elnath"),
    ("Dubhe", "Phad"),
    ("Phad", "Megrez"),
    ("Megrez", "Alioth"),
    ("Alioth", "Mizar"),
    ("Mizar", "Alkaid"),
    ("Megrez", "Dubhe"),
    ("Polaris", "Kochab"),
    ("Arcturus", "Izar"),
    ("Izar", "Muphrid"),
    ("Arcturus", "Muphrid"),
    ("Schedar", "Segin"),
    ("Regulus", "Denebola"),
    ("Spica", "Porrima"),
    ("Antares", "Jabbah"),
    ("Jabbah", "Paikauhale"),
    ("Altair", "Deneb el Okab"),
    ("Vega", "Deneb"),
    ("Deneb", "Altair"),
    ("Altair", "Vega"),
]

SD_RADIANCE = {
    2012: 19.77, 2013: 21.00, 2014: 21.17, 2015: 20.64,
    2016: 20.53, 2017: 20.36, 2018: 20.70, 2019: 20.86,
    2020: 21.15, 2021: 21.29, 2022: 21.50, 2023: 22.68
}


def load_zip_data():
    url = "https://raw.githubusercontent.com/prestonbliang/what-you-have-lost/main/zip_radiance.json"
    try:
        response = requests.get(url, timeout=15)
        return response.json()
    except Exception:
        return {}


def get_radiance_by_year(zipcode, zip_data):
    data = zip_data.get(str(zipcode).zfill(5), None)
    if data:
        return {int(k): float(v) for k, v in data.items()}
    return SD_RADIANCE


def radiance_to_limiting_magnitude(radiance):
    if radiance < 18:
        return 4.9
    elif radiance < 20:
        return 4.6
    elif radiance < 22:
        return 4.3
    elif radiance < 24:
        return 4.1
    elif radiance < 26:
        return 3.9
    else:
        return 3.0


def zip_to_coords(zipcode):
    try:
        response = requests.get(f"https://api.zippopotam.us/us/{zipcode}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            lat = float(data["places"][0]["latitude"])
            lon = float(data["places"][0]["longitude"])
            city = data["places"][0]["place name"]
            state = data["places"][0]["state"]
            return lat, lon, f"{city}, {state}"
    except Exception:
        pass
    try:
        headers = {"User-Agent": "WhatHaveYouLost/1.0"}
        response = requests.get(
            f"https://nominatim.openstreetmap.org/search?postalcode={zipcode}&country=US&format=json",
            headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"]), data[0]["display_name"]
    except Exception:
        pass
    return None, None, None


def compute_lst(lon_deg, year):
    return 9.0


def ra_dec_to_xy(ra_hours, dec_deg, lat_deg, lst_hours):
    ra = math.radians(ra_hours * 15)
    dec = math.radians(dec_deg)
    lat_r = math.radians(lat_deg)
    ha = math.radians(lst_hours * 15) - ra
    sin_alt = (math.sin(dec) * math.sin(lat_r) +
               math.cos(dec) * math.cos(lat_r) * math.cos(ha))
    sin_alt = max(-1.0, min(1.0, sin_alt))
    alt = math.asin(sin_alt)
    denom = (math.cos(alt) * math.cos(lat_r))
    if abs(denom) < 1e-10:
        denom = 1e-10
    cos_az = ((math.sin(dec) - math.sin(alt) * math.sin(lat_r)) / denom)
    cos_az = max(-1.0, min(1.0, cos_az))
    az = math.acos(cos_az)
    if math.sin(ha) > 0:
        az = 2 * math.pi - az
    r = (math.pi / 2 - alt) / (math.pi / 2)
    x = r * math.sin(az)
    y = r * math.cos(az)
    return x, y, math.degrees(alt)


def make_sky_chart(stars, year, radiance_by_year, color_map, lat, lon, constellation_lines):
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor("#03030a")
    ax.set_facecolor("#03030a")
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.35, 1.35)
    ax.axis("off")
    ax.set_aspect("equal")

    rad_2012 = radiance_by_year[2012]
    rad_now = radiance_by_year[year]
    lm_2012 = radiance_to_limiting_magnitude(rad_2012)
    lm_now = radiance_to_limiting_magnitude(rad_now)

    glow_alpha = min(0.05, max(0, (rad_now - rad_2012) / (rad_2012 * 3)))
    glow = mpatches.Circle((0, -0.3), 1.3, color="#FF6600", alpha=glow_alpha)
    ax.add_patch(glow)

    horizon = plt.Circle((0, 0), 1.0, color="#1a2a4a", fill=False, linewidth=1.0)
    ax.add_patch(horizon)

    for alt_deg in [20, 40, 60, 80]:
        r = 1.0 - alt_deg / 90
        ring = plt.Circle((0, 0), r, color="#2a4a7a", fill=False,
                           linewidth=0.4, linestyle=(0, (1, 3)))
        ax.add_patch(ring)

    for deg in range(0, 360, 30):
        angle = math.radians(deg)
        x_end = math.sin(angle)
        y_end = math.cos(angle)
        ax.plot([0, x_end], [0, y_end], color="#2a4a7a",
                linewidth=0.4, linestyle=(0, (1, 3)), zorder=1)

    for label, angle in [("N", 0), ("E", -math.pi / 2), ("S", math.pi), ("W", math.pi / 2)]:
        x = 1.12 * math.sin(angle)
        y = 1.12 * math.cos(angle)
        ax.text(x, y, label, color="#7799CC", fontsize=9,
                ha="center", va="center", fontweight="bold")

    lst = compute_lst(lon, year)

    positions = {}
    altitudes = {}
    for name, mag, ra, dec in stars:
        x, y, alt = ra_dec_to_xy(ra, dec, lat, lst)
        positions[name] = (x, y)
        altitudes[name] = alt

    for star_a, star_b in constellation_lines:
        if star_a in positions and star_b in positions:
            if altitudes[star_a] >= 0 and altitudes[star_b] >= 0:
                xa, ya = positions[star_a]
                xb, yb = positions[star_b]
                ax.plot([xa, xb], [ya, yb], color="#3a5a8a",
                        linewidth=0.6, alpha=0.55, zorder=1.5)

    visible_count = 0
    lost_on_chart = []

    for name, mag, ra, dec in stars:
        x, y = positions[name]
        alt = altitudes[name]
        if alt < 0:
            continue

        was_visible = mag <= lm_2012
        is_visible = mag <= lm_now

        if is_visible:
            size = max(6, 90 / (mag + 2.5))
            brightness = min(1.0, max(0.3, 1.0 - mag / 9))
            ax.scatter(x, y, s=size, color="white", alpha=brightness, zorder=3)
            visible_count += 1
            if mag < 1.0:
                ax.text(x, y + 0.06, name, color="#7799CC", fontsize=6,
                        ha="center", va="center", style="italic")
        elif was_visible:
            color = color_map.get((name, mag), "#FF4444")
            size = max(8, 80 / (mag + 2.5))
            ax.scatter(x, y, s=size, color=color, alpha=0.7,
                       zorder=2, marker="*")
            lost_on_chart.append((name, color))
            label_offset = -0.07 if name == "M41" else 0.06
            ax.text(x, y + label_offset, name, color=color, fontsize=5.5,
                    ha="center", va="center", style="italic", alpha=0.85)

    ax.scatter([-1.05], [-1.1], s=15, color="white", alpha=0.9, zorder=5)
    ax.text(-0.92, -1.1, "visible", color="#8899BB", fontsize=6, va="center")
    ax.scatter([-0.5], [-1.1], s=14, color="#FF6B6B", alpha=0.7,
               marker="*", zorder=5)
    ax.text(-0.38, -1.1, "lost since 2012", color="#CC6666",
            fontsize=6, va="center")

    ax.text(0, 1.25, str(year), ha="center", color="white", fontsize=13)
    ax.text(0, -1.27, f"{rad_now:.1f} nW/cm²/sr  ·  {visible_count} visible",
            ha="center", color="#445566", fontsize=7)

    return fig, lost_on_chart


if "searched" not in st.session_state:
    st.session_state.searched = False
if "zipcode" not in st.session_state:
    st.session_state.zipcode = ""
if "radiance_by_year" not in st.session_state:
    st.session_state.radiance_by_year = {}
if "lat" not in st.session_state:
    st.session_state.lat = 32.8
if "lon" not in st.session_state:
    st.session_state.lon = -117.2
if "place_name" not in st.session_state:
    st.session_state.place_name = ""

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center; font-size:3rem; letter-spacing:0.2em; color:#FF4444;'>WHAT HAVE YOU LOST</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:1rem; letter-spacing:0.1em; color:#555577;'>enter your zip code to see which stars have disappeared from your sky since 2012</p>", unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    zipcode_input = st.text_input("", placeholder="zip code", label_visibility="collapsed")
    if st.button("search", use_container_width=True):
        lat, lon, display_name = zip_to_coords(zipcode_input)
        if lat:
            zip_data = load_zip_data()
            st.session_state.searched = True
            st.session_state.zipcode = zipcode_input
            st.session_state.radiance_by_year = get_radiance_by_year(zipcode_input, zip_data)
            st.session_state.lat = lat
            st.session_state.lon = lon
            st.session_state.place_name = display_name
        else:
            st.markdown("<p style='text-align:center; color:#442222;'>zip code not found</p>",
                        unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if st.session_state.searched:
    zipcode = st.session_state.zipcode
    radiance_by_year = st.session_state.radiance_by_year
    lat = st.session_state.lat
    lon = st.session_state.lon

    rad_2012 = radiance_by_year[2012]
    rad_2023 = radiance_by_year[2023]
    lm_2012 = radiance_to_limiting_magnitude(rad_2012)
    lm_2023 = radiance_to_limiting_magnitude(rad_2023)
    pct_change = ((rad_2023 - rad_2012) / rad_2012) * 100

    star_mags = [(s[0], s[1]) for s in STARS]
    potentially_lost = sorted(
        [(n, m) for n, m in star_mags if lm_2023 < m <= lm_2012],
        key=lambda x: x[1]
    )
    color_map = {(n, m): LOST_COLORS[i % len(LOST_COLORS)]
                 for i, (n, m) in enumerate(potentially_lost)}

    all_lost = potentially_lost
    still_visible = [(n, m) for n, m in star_mags if m <= lm_2023]

    st.markdown(f"<p style='text-align:center; letter-spacing:0.15em; font-size:0.75rem; color:#444466;'>ZIP CODE {zipcode}</p>",
                unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; font-size:0.85rem; color:#7788AA; margin-top:-8px;'>{st.session_state.place_name}</p>",
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("light pollution since 2012", f"{pct_change:+.1f}%")
    if pct_change >= 0:
        m2.metric("stars lost since 2012", len(all_lost))
    else:
        gained = [(n, m) for n, m in star_mags if lm_2012 < m <= lm_2023]
        m2.metric("stars gained since 2012", len(gained))
    m3.metric("still visible tonight", len(still_visible))

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; letter-spacing:0.1em; font-size:0.7rem; color:#334466;'>DRAG TO TRAVEL THROUGH TIME</p>",
                unsafe_allow_html=True)

    year = st.slider("", min_value=2012, max_value=2023, value=2012,
                      label_visibility="collapsed")

    col_center = st.columns([1, 6, 1])[1]
    with col_center:
        fig, lost_on_chart = make_sky_chart(STARS, year, radiance_by_year,
                                             color_map, lat, lon, CONSTELLATION_LINES)
        st.pyplot(fig, use_container_width=True)

    st.markdown("<p style='text-align:center; font-size:0.7rem; color:#334455; margin-top:-10px;'>face south · center is straight up · stars near the edge sit low on the horizon</p>",
                unsafe_allow_html=True)

    if lost_on_chart:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<p style='letter-spacing:0.15em; font-size:0.7rem; color:#333355;'>LOST FROM YOUR SKY BY {year}</p>",
                    unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        html = "<div style='display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px;'>"
        for name, color in lost_on_chart:
            html += f"<div style='color:{color}; font-size:0.85rem;'>★ {name}</div>"
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:0.65rem; letter-spacing:0.1em; color:#445566;'>NASA BLACK MARBLE VNP46A4</p>",
                unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; letter-spacing:0.15em; font-size:0.7rem; color:#6666AA;'>HOW IS THIS DIFFERENT</p>",
            unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; max-width:600px; margin:0 auto; font-size:0.9rem; line-height:2; color:#7788AA;'>Tools like Light Pollution Map, NASA Worldview, and Globe at Night show raw radiance data built for researchers. This tool translates that data into something human — the actual named stars you have lost from your specific sky, since 2012.</p>",
            unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:0.65rem; letter-spacing:0.1em; color:#445566;'>BUILT BY A STUDENT RESEARCHER IN SAN DIEGO</p>",
            unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)
