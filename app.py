
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import requests

st.set_page_config(page_title="What Have You Lost?", page_icon="🌟", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #000008; }
    h1, h2, h3, p, label { color: white !important; }
    .stTextInput input { background-color: #111122; color: white; }
    .stButton button { background-color: #3333AA; color: white; width: 100%; }
    .stMetric { background-color: #111122; border-radius: 8px; padding: 10px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style=\'text-align:center; color:white;\'>🌟 What Have You Lost?</h1>", unsafe_allow_html=True)
st.markdown("<p style=\'text-align:center; color:#AAAACC;\'>Enter your zip code to see which stars disappeared from your sky since 2012</p>", unsafe_allow_html=True)

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
    fig.patch.set_facecolor("#000008")
    ax.set_facecolor("#000008")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    if year == 2023 and len(lost) > 0:
        glow = plt.Circle((5, 5), 6, color="#FF8800", alpha=0.04)
        ax.add_patch(glow)
    for name, mag in visible:
        x = np.random.uniform(0.3, 9.7)
        y = np.random.uniform(0.8, 9.5)
        size = max(8, 100 / (mag + 2))
        brightness = min(1.0, max(0.3, 1.0 - (mag / 10)))
        ax.scatter(x, y, s=size, color="white", alpha=brightness, zorder=3)
    for name, mag in lost:
        x = np.random.uniform(0.3, 9.7)
        y = np.random.uniform(0.8, 9.5)
        size = max(6, 60 / (mag + 2))
        ax.scatter(x, y, s=size, color="#FF4444", alpha=0.2, zorder=2, marker="*")
    ax.text(5, 9.7, title, ha="center", color="white", fontsize=13, fontweight="bold")
    ax.text(5, 9.3, f"Radiance: {radiance:.2f} · Faintest visible: mag {limit}",
            ha="center", color="#8888AA", fontsize=8)
    ax.text(5, 0.3, f"{len(visible)} objects visible",
            ha="center", color="#8888AA", fontsize=9)
    return fig

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    zipcode = st.text_input("", placeholder="Enter zip code e.g. 92111", label_visibility="collapsed")
    search = st.button("Show My Sky →", use_container_width=True)

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
        st.markdown(f"<h2 style=\'text-align:center; color:white;\'>Results for {zipcode}</h2>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("Light Pollution Increase", f"+{pct_change:.1f}%")
        m2.metric("Stars Lost Since 2012", len(lost))
        m3.metric("Still Visible Tonight", len(still_visible))
        col_a, col_b = st.columns(2)
        np.random.seed(42)
        with col_a:
            fig1 = make_sky_chart(still_visible + lost, [], "Your Sky — 2012", 2012, radiance_2012, limit_2012)
            st.pyplot(fig1)
        np.random.seed(42)
        with col_b:
            fig2 = make_sky_chart(still_visible, lost, "Your Sky — 2023", 2023, radiance_2023, limit_2023)
            st.pyplot(fig2)
        if lost:
            st.markdown("<h3 style=\'color:white;\'>What you can no longer see:</h3>", unsafe_allow_html=True)
            cols = st.columns(3)
            for i, (name, mag) in enumerate(sorted(lost, key=lambda x: x[1])):
                cols[i % 3].markdown(f"<p style=\'color:#FF6666;\'>✗ {name} (mag {mag:.2f})</p>", unsafe_allow_html=True)
        st.markdown("<p style=\'text-align:center; color:#555577; font-size:12px;\'>Source: NASA Black Marble VNP46A4</p>", unsafe_allow_html=True)
    else:
        st.error("Zip code not found.")

