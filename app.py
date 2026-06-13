
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import requests

st.set_page_config(page_title="What Have You Lost?", page_icon="✦", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Space+Grotesk:wght@300;400;500;600&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #03030a; }
    section[data-testid="stSidebar"] { display: none; }
    .main .block-container { max-width: 900px; margin: 0 auto; padding: 4rem 2rem; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; color: white !important; font-weight: 300 !important; letter-spacing: 0.05em !important; }
    label { color: #8888AA !important; }
    .stTextInput input { background-color: #0d0d1a !important; border: 1px solid #222244 !important; border-radius: 4px !important; color: white !important; padding: 0.75rem 1rem !important; font-size: 16px !important; }
    .stButton button { background-color: transparent !important; border: 1px solid #4444AA !important; border-radius: 4px !important; color: #8888CC !important; padding: 0.75rem 2rem !important; font-size: 14px !important; letter-spacing: 0.15em !important; text-transform: uppercase !important; width: 100% !important; }
    .stButton button:hover { background-color: #4444AA22 !important; color: white !important; }
    .stMetric { background-color: #0d0d1a !important; border: 1px solid #111133 !important; border-radius: 4px !important; padding: 1.5rem !important; }
    .stMetric label { color: #555577 !important; font-size: 11px !important; letter-spacing: 0.15em !important; text-transform: uppercase !important; }
    .stMetric [data-testid="stMetricValue"] { color: white !important; font-size: 2rem !important; font-weight: 300 !important; }
    hr { border-color: #111133 !important; margin: 3rem 0 !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_zip_data():
    url = "https://raw.githubusercontent.com/prestonbliang/what-you-have-lost/main/zip_radiance.json"
    response = requests.get(url, timeout=15)
    return response.json()

ZIP_DATA = load_zip_data()

def get_radiance_by_year(zipcode):
    data = ZIP_DATA.get(str(zipcode).zfill(5), None)
    if data:
        return {int(k): v for k, v in data.items()}
    # Fallback to San Diego data
    return {2012: 19.77, 2013: 21.00, 2014: 21.17, 2015: 20.64,
            2016: 20.53, 2017: 20.36, 2018: 20.70, 2019: 20.86,
            2020: 21.15, 2021: 21.29, 2022: 19.90, 2023: 22.68}

stars = [
    ("Sirius", -1.46), ("Arcturus", -0.05), ("Vega", 0.03),
    ("Rigel", 0.13), ("Procyon", 0.34), ("Betelgeuse", 0.42),
    ("Altair", 0.76), ("Aldebaran", 0.87), ("Antares", 1.06),
    ("Spica", 1.04), ("Pollux", 1.16), ("Fomalhaut", 1.17),
    ("Deneb", 1.25), ("Regulus", 1.36), ("Adhara", 1.50),
    ("Castor", 1.58), ("Bellatrix", 1.64), ("Elnath", 1.65),
    ("Alnilam", 1.70), ("Alioth", 1.76), ("Mirfak", 1.79),
    ("Dubhe", 1.81), ("Alkaid", 1.85), ("Peacock", 1.94),
    ("Polaris", 1.97), ("Hamal", 2.01), ("Alpheratz", 2.07),
    ("Kochab", 2.07), ("Algol", 2.09), ("Denebola", 2.14),
    ("Alphecca", 2.22), ("Mintaka", 2.23), ("Schedar", 2.24),
    ("Phad", 2.40), ("Izar", 2.35), ("Mizar", 2.23),
    ("Muphrid", 2.68), ("Porrima", 2.74), ("Sabik", 2.87),
    ("Cor Caroli", 2.89), ("Megrez", 3.31), ("Segin", 3.38),
    ("Tania Borealis", 3.45), ("Alula Australis", 3.67),
    ("Fulu", 3.66), ("Albali", 3.77), ("Andromeda Galaxy", 3.44),
    ("Beehive Cluster", 3.70), ("Omega Centauri", 3.90),
    ("Acubens", 3.94), ("Propus", 3.97), ("Castula", 3.97),
    ("Marfak", 3.98), ("Alzirr", 3.99), ("Alula Borealis", 3.99),
    ("Jabbah", 4.00), ("Orion Nebula", 4.00), ("Mekbuda", 4.01),
    ("Deneb el Okab", 4.02), ("47 Tucanae", 4.09),
    ("Ancha", 4.17), ("Chara", 4.26), ("Asterion", 4.26),
    ("NGC 869", 4.30), ("Paikauhale", 4.35), ("Situla", 4.42),
    ("Iota Leporis", 4.45), ("M41", 4.50), ("Gamma Pictoris", 4.51),
]

def radiance_to_limiting_magnitude(radiance):
    # Continuous conversion - more sensitive to small changes
    # Based on Bortle scale: limiting mag decreases as radiance increases
    import math
    if radiance <= 0:
        return 7.6
    # Logarithmic relationship between radiance and limiting magnitude
    lm = 7.6 - 1.2 * math.log10(max(1, radiance))
    return round(max(2.0, min(7.6, lm)), 2)

def star_alpha(mag, limiting_mag, fade_range=0.8):
    """Calculate star brightness - stars fade gradually before disappearing"""
    if mag <= limiting_mag - fade_range:
        # Fully visible - brightness based on magnitude
        return min(1.0, max(0.3, 1.0 - (mag / 10)))
    elif mag <= limiting_mag:
        # Fading zone - gradually dim
        fade_progress = (limiting_mag - mag) / fade_range
        base = min(1.0, max(0.3, 1.0 - (mag / 10)))
        return base * fade_progress
    else:
        return 0  # invisible

def zip_to_coords(zipcode):
    # Try multiple APIs in case one is blocked
    apis = [
        f"https://api.zippopotam.us/us/{zipcode}",
        f"https://nominatim.openstreetmap.org/search?postalcode={zipcode}&country=US&format=json"
    ]
    
    # Try zippopotam first
    try:
        response = requests.get(f"https://api.zippopotam.us/us/{zipcode}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            lat = float(data["places"][0]["latitude"])
            lon = float(data["places"][0]["longitude"])
            city = data["places"][0]["place name"]
            state = data["places"][0]["state"]
            return lat, lon, f"{city}, {state}"
    except:
        pass
    
    # Fallback to nominatim
    try:
        headers = {"User-Agent": "WhatHaveYouLost/1.0"}
        response = requests.get(
            f"https://nominatim.openstreetmap.org/search?postalcode={zipcode}&country=US&format=json",
            headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"]), data[0]["display_name"]
    except:
        pass
    
    return None, None, None

def make_sky_chart(stars, year, radiance, limiting_mag, baseline_limit):
    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor("#03030a")
    ax.set_facecolor("#03030a")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # Light pollution glow - gets stronger over time
    from matplotlib.patches import Circle
    glow_alpha = min(0.12, max(0, (radiance - 19) / 25))
    glow = Circle((5, 0), 8, color="#FF6600", alpha=glow_alpha)
    ax.add_patch(glow)
    glow2 = Circle((5, 0), 5, color="#FF8800", alpha=glow_alpha * 0.5)
    ax.add_patch(glow2)

    # Unique colors for each potentially lost star
    LOST_COLORS = [
        "#FF6B6B", "#FF9F43", "#FECA57", "#2ED573", "#48DBFB",
        "#FF6348", "#A29BFE", "#FD79A8", "#7BED9F", "#ECCC68"
    ]
    
    # Assign colors to all stars that could be lost
    all_possible_lost = sorted(
        [(n, m) for n, m in stars if m > radiance_to_limiting_magnitude(RADIANCE_BY_YEAR[2023]) 
         and m <= radiance_to_limiting_magnitude(RADIANCE_BY_YEAR[2012])],
        key=lambda x: x[1]
    )
    star_colors = {(n, m): LOST_COLORS[i % len(LOST_COLORS)] 
                   for i, (n, m) in enumerate(all_possible_lost)}

    np.random.seed(42)
    positions = {(name, mag): (np.random.uniform(0.3, 9.7), np.random.uniform(0.8, 9.5))
                 for name, mag in stars}

    visible_count = 0
    lost_names = []

    for name, mag in stars:
        x, y = positions[(name, mag)]
        alpha = star_alpha(mag, limiting_mag)

        if alpha > 0:
            size = max(6, 90 / (mag + 2))
            fade_ratio = (limiting_mag - mag) / 0.8 if mag > limiting_mag - 0.8 else 1.0
            fade_ratio = max(0, min(1, fade_ratio))
            if (name, mag) in star_colors and fade_ratio < 1.0:
                color = star_colors[(name, mag)]
            elif fade_ratio < 1.0:
                color = (1.0, 1.0 - (1 - fade_ratio) * 0.7, 1.0 - (1 - fade_ratio) * 0.7)
            else:
                color = "white"
            ax.scatter(x, y, s=size, color=color, alpha=alpha, zorder=3)
            if mag <= limiting_mag:
                visible_count += 1
        else:
            if mag <= baseline_limit:
                lost_color = star_colors.get((name, mag), "#FF2222")
                lost_names.append((name, lost_color))
                ax.scatter(x, y, s=12, color=lost_color, alpha=0.4, zorder=2, marker="*")

    # Labels for brightest
    brightest = sorted(stars, key=lambda x: x[1])[:10]
    for name, mag in brightest:
        x, y = positions[(name, mag)]
        offset_y = 0.35 if y < 8.5 else -0.35
        alpha = star_alpha(mag, limiting_mag)
        color = "#6688AA" if alpha > 0.5 else "#663333"
        ax.text(x, y + offset_y, name, color=color, fontsize=5.5,
                ha="center", va="center", style="italic")

    # Legend
    ax.scatter([0.4], [0.6], s=20, color="white", alpha=0.9, zorder=5)
    ax.text(0.7, 0.6, "visible", color="#8899BB", fontsize=6, va="center")
    ax.scatter([2.2], [0.6], s=8, color="#FF2222", alpha=0.3, marker="*", zorder=5)
    ax.text(2.5, 0.6, "lost", color="#AA4444", fontsize=6, va="center")

    ax.text(5, 9.75, str(year), ha="center", color="white", fontsize=14)
    ax.text(5, 9.35, f"{radiance:.2f} nW/cm²/sr  ·  limiting mag {limiting_mag}",
            ha="center", color="#444466", fontsize=7)
    ax.text(5, 0.25, f"{visible_count} objects visible",
            ha="center", color="#333355", fontsize=8)

    return fig, lost_names, star_colors

# Session state
if "searched" not in st.session_state:
    st.session_state.searched = False
if "zipcode" not in st.session_state:
    st.session_state.zipcode = ""

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center; font-size:3rem; letter-spacing:0.2em;'>WHAT HAVE YOU LOST</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:1rem; letter-spacing:0.1em;'>enter your zip code to see which stars have disappeared from your sky since 2012</p>", unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    zipcode_input = st.text_input("", placeholder="zip code", label_visibility="collapsed")
    if st.button("search", use_container_width=True):
        lat, lon, display_name = zip_to_coords(zipcode_input)
        if lat:
            st.session_state.searched = True
            st.session_state.zipcode = zipcode_input
        else:
            st.markdown("<p style='text-align:center; color:#442222;'>zip code not found</p>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if st.session_state.searched:
    zipcode = st.session_state.zipcode
    RADIANCE_BY_YEAR = get_radiance_by_year(zipcode)
    radiance_2012 = RADIANCE_BY_YEAR[2012]
    radiance_2023 = RADIANCE_BY_YEAR[2023]
    baseline_limit = radiance_to_limiting_magnitude(radiance_2012)
    limit_2023 = radiance_to_limiting_magnitude(radiance_2023)
    all_lost = [(n, m) for n, m in stars if limit_2023 < m <= baseline_limit]
    pct_change = ((radiance_2023 - radiance_2012) / radiance_2012) * 100

    st.markdown(f"<p style='text-align:center; letter-spacing:0.15em; font-size:0.75rem; color:#444466;'>ZIP CODE {zipcode}</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("light pollution since 2012", f"{pct_change:+.1f}%")
    gained = [(n, m) for n, m in stars if baseline_limit < m <= limit_2023]
    if pct_change < 0:
        m2.metric("stars gained since 2012", len(gained))
    else:
        m2.metric("stars lost since 2012", len(all_lost))
    m3.metric("still visible tonight", len([s for s in stars if s[1] <= limit_2023]))

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; letter-spacing:0.1em; font-size:0.7rem; color:#334466;'>DRAG TO TRAVEL THROUGH TIME</p>", unsafe_allow_html=True)

    year = st.slider("", min_value=2012, max_value=2023, value=2012,
                     label_visibility="collapsed")

    radiance = RADIANCE_BY_YEAR[year]
    limiting_mag = radiance_to_limiting_magnitude(radiance)

    st.write(f"DEBUG: radiance={radiance:.2f} limiting_mag={limiting_mag} baseline={baseline_limit} visible={len([s for s in stars if s[1] <= limiting_mag])}")
    col_center = st.columns([1, 6, 1])[1]
    with col_center:
        fig, lost_names, star_colors = make_sky_chart(stars, year, radiance, limiting_mag, baseline_limit)
        st.pyplot(fig, use_container_width=True)

    if lost_names:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<p style='letter-spacing:0.15em; font-size:0.7rem; color:#333355;'>LOST FROM YOUR SKY BY {year}</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        html = "<div style='display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px;'>"
        for name, color in lost_names:
            html += f"<div style='color:{color}; font-size:0.85rem;'>★ {name}</div>"
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:0.65rem; letter-spacing:0.1em; color:#1a1a2e;'>NASA BLACK MARBLE VNP46A4</p>", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; letter-spacing:0.15em; font-size:0.7rem; color:#222244;'>HOW IS THIS DIFFERENT</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; max-width:600px; margin:0 auto; font-size:0.9rem; line-height:2; color:#333355;'>Tools like Light Pollution Map, NASA Worldview, and Globe at Night show raw radiance data built for researchers. This tool translates that data into something human — the actual named stars you have lost from your specific sky, since 2012.</p>", unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:0.65rem; letter-spacing:0.1em; color:#111122;'>BUILT BY A STUDENT RESEARCHER IN SAN DIEGO</p>", unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)
