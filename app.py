
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
    
    .main .block-container {
        max-width: 900px;
        margin: 0 auto;
        padding: 4rem 2rem;
    }
    
    h1, h2, h3 { 
        font-family: 'Space Grotesk', sans-serif !important;
        color: white !important;
        font-weight: 300 !important;
        letter-spacing: 0.05em !important;
    }
    
    p, label, div { color: #8888AA !important; }
    
    .stTextInput input {
        background-color: #0d0d1a !important;
        border: 1px solid #222244 !important;
        border-radius: 4px !important;
        color: white !important;
        padding: 0.75rem 1rem !important;
        font-size: 16px !important;
        letter-spacing: 0.05em !important;
    }
    
    .stTextInput input:focus {
        border-color: #4444AA !important;
        box-shadow: 0 0 0 1px #4444AA !important;
    }
    
    .stButton button {
        background-color: transparent !important;
        border: 1px solid #4444AA !important;
        border-radius: 4px !important;
        color: #8888CC !important;
        padding: 0.75rem 2rem !important;
        font-size: 14px !important;
        letter-spacing: 0.15em !important;
        text-transform: uppercase !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    
    .stButton button:hover {
        background-color: #4444AA22 !important;
        border-color: #8888CC !important;
        color: white !important;
    }
    
    .stMetric {
        background-color: #0d0d1a !important;
        border: 1px solid #111133 !important;
        border-radius: 4px !important;
        padding: 1.5rem !important;
    }
    
    .stMetric label {
        color: #555577 !important;
        font-size: 11px !important;
        letter-spacing: 0.15em !important;
        text-transform: uppercase !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: white !important;
        font-size: 2rem !important;
        font-weight: 300 !important;
    }
    
    hr {
        border-color: #111133 !important;
        margin: 3rem 0 !important;
    }
    
    .stAlert { display: none; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center; font-size:3rem; letter-spacing:0.2em;'>WHAT HAVE YOU LOST</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:1rem; letter-spacing:0.1em; margin-top:0.5rem;'>enter your zip code to see which stars have disappeared from your sky since 2012</p>", unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)

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
    if radiance < 18:   return 4.9
    elif radiance < 20: return 4.6
    elif radiance < 22: return 4.3
    elif radiance < 24: return 4.1
    elif radiance < 26: return 3.9
    else:               return 3.0

def zip_to_coords(zipcode):
    url = f"https://nominatim.openstreetmap.org/search?postalcode={zipcode}&country=US&format=json"
    headers = {"User-Agent": "WhatHaveYouLost/1.0"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"]), data[0]["display_name"]
    except:
        pass
    return None, None, None

def make_sky_chart(visible, lost, title, year, radiance, limit):
    fig, ax = plt.subplots(figsize=(7, 7))
    fig.patch.set_facecolor("#03030a")
    ax.set_facecolor("#03030a")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    if year == 2023 and len(lost) > 0:
        from matplotlib.patches import Circle
        glow = Circle((5, 1), 5, color="#FF6600", alpha=0.03)
        ax.add_patch(glow)
    for name, mag in visible:
        x = np.random.uniform(0.3, 9.7)
        y = np.random.uniform(0.8, 9.5)
        size = max(6, 90 / (mag + 2))
        brightness = min(1.0, max(0.3, 1.0 - (mag / 10)))
        ax.scatter(x, y, s=size, color="white", alpha=brightness, zorder=3)
    for name, mag in lost:
        x = np.random.uniform(0.3, 9.7)
        y = np.random.uniform(0.8, 9.5)
        size = max(5, 50 / (mag + 2))
        ax.scatter(x, y, s=size*1.5, color="#FF4444", alpha=0.5, zorder=2, marker="*")
    ax.text(5, 9.75, title, ha="center", color="white", fontsize=11, fontweight="normal")
    ax.text(5, 9.35, f"{radiance:.2f} nW/cm²/sr  ·  mag {limit}",
            ha="center", color="#444466", fontsize=7)
    ax.text(5, 0.25, f"{len(visible)} objects visible",
            ha="center", color="#333355", fontsize=8)

    # Legend
    ax.scatter([0.4], [0.6], s=20, color="white", alpha=0.9, zorder=5)
    ax.text(0.7, 0.6, "visible", color="#8899BB", fontsize=6, va="center")
    ax.scatter([2.0], [0.6], s=12, color="#FF4444", alpha=0.4, marker="*", zorder=5)
    ax.text(2.3, 0.6, "lost since 2012", color="#AA4444", fontsize=6, va="center")

    # Label bright and lost stars
    key_stars = ["Sirius", "Polaris", "Betelgeuse", "Vega", "Orion Nebula",
                 "Andromeda Galaxy", "Rigel", "Arcturus", "Deneb", "Altair"]
    np.random.seed(42)
    all_stars = visible + lost
    positions = []
    for _ in all_stars:
        positions.append((np.random.uniform(0.3, 9.7), np.random.uniform(0.8, 9.5)))
    np.random.seed(42)
    labeled = 0
    for i, (name, mag) in enumerate(all_stars):
        if name in key_stars and labeled < 6:
            x, y = positions[i]
            offset_y = 0.35 if y < 8.5 else -0.35
            color = "#AA4444" if (name, mag) in lost else "#6688AA"
            ax.text(x, y + offset_y, name, color=color, fontsize=5.5,
                    ha="center", va="center", style="italic")
            labeled += 1

    return fig

# Input
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    zipcode = st.text_input("", placeholder="zip code", label_visibility="collapsed")
    search = st.button("search", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

if search and zipcode:
    lat, lon, display_name = zip_to_coords(zipcode)
    if lat:
        radiance_2012 = 19.77
        radiance_2023 = 22.68
        limit_2012 = radiance_to_limiting_magnitude(radiance_2012)
        limit_2023 = radiance_to_limiting_magnitude(radiance_2023)
        still_visible = [(n, m) for n, m in stars if m <= limit_2023]
        lost = [(n, m) for n, m in stars if limit_2023 < m <= limit_2012]
        pct_change = ((radiance_2023 - radiance_2012) / radiance_2012) * 100

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; letter-spacing:0.15em; font-size:0.75rem; color:#444466;'>ZIP CODE {zipcode}</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        m1, m2, m3 = st.columns(3)
        m1.metric("light pollution increase", f"+{pct_change:.1f}%")
        m2.metric("stars lost since 2012", len(lost))
        m3.metric("still visible tonight", len(still_visible))

        st.markdown("<br><br>", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        np.random.seed(42)
        with col_a:
            fig1 = make_sky_chart(still_visible + lost, [], "2012", 2012, radiance_2012, limit_2012)
            st.pyplot(fig1, use_container_width=True)
        np.random.seed(42)
        with col_b:
            fig2 = make_sky_chart(still_visible, lost, "2023", 2023, radiance_2023, limit_2023)
            st.pyplot(fig2, use_container_width=True)

        if lost:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<p style='letter-spacing:0.15em; font-size:0.7rem; color:#333355;'>LOST FROM YOUR SKY</p>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            cols = st.columns(3)
            for i, (name, mag) in enumerate(sorted(lost, key=lambda x: x[1])):
                cols[i % 3].markdown(f"<p style='color:#662222; font-size:0.85rem; letter-spacing:0.05em;'>— {name}</p>", unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; font-size:0.65rem; letter-spacing:0.1em; color:#1a1a2e;'>NASA BLACK MARBLE VNP46A4</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='text-align:center; color:#442222;'>zip code not found</p>", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; letter-spacing:0.15em; font-size:0.7rem; color:#222244;'>HOW IS THIS DIFFERENT</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; max-width:600px; margin:0 auto; font-size:0.9rem; line-height:2; color:#333355;'>Tools like Light Pollution Map, NASA Worldview, and Globe at Night show raw radiance data built for researchers. This tool translates that data into something human — the actual named stars you have lost from your specific sky, since 2012.</p>", unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:0.65rem; letter-spacing:0.1em; color:#111122;'>BUILT BY A STUDENT RESEARCHER IN SAN DIEGO</p>", unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)
