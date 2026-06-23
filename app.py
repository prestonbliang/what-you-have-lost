import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import requests
import math
import plotly.graph_objects as go

st.set_page_config(page_title="What Have You Lost?", page_icon="✦", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Space+Grotesk:wght@300;400;500;600&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #03030a; }
    section[data-testid="stSidebar"] { display: none; }
    header[data-testid="stHeader"] { display: none !important; }
    .main .block-container { max-width: 900px; margin: 0 auto; padding: 5.5rem 2rem 4rem 2rem; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; color: white !important; font-weight: 300 !important; letter-spacing: 0.05em !important; }
    .stTextInput input { background-color: #0d0d1a !important; border: 1px solid #222244 !important; border-radius: 4px !important; color: white !important; padding: 0.75rem 1rem !important; font-size: 16px !important; }
    .stButton button { background-color: transparent !important; border: 1px solid #4444AA !important; border-radius: 4px !important; color: #8888CC !important; padding: 0.75rem 2rem !important; font-size: 14px !important; letter-spacing: 0.15em !important; text-transform: uppercase !important; width: 100% !important; }
    .stButton button:hover { background-color: #4444AA22 !important; color: white !important; }
    .stMetric { background-color: #0d0d1a !important; border: 1px solid #111133 !important; border-radius: 4px !important; padding: 1.5rem !important; }
    .stMetric label { color: #555577 !important; font-size: 11px !important; letter-spacing: 0.15em !important; text-transform: uppercase !important; }
    .stMetric [data-testid="stMetricValue"] { color: white !important; font-size: 2rem !important; font-weight: 300 !important; }
    hr { border-color: #111133 !important; margin: 3rem 0 !important; }
    .wyhl-topnav {
        position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
        height: 52px;
        background: rgba(3,3,10,0.92);
        border-bottom: 1px solid #1a1a3a;
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 2.5rem;
        backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
    }
    .wyhl-brand { font-family: 'Space Grotesk',sans-serif; font-size: 0.7rem; letter-spacing: 0.22em; color: #FF4444; text-decoration: none; }
    .wyhl-navlinks { display: flex; gap: 2.5rem; align-items: center; }
    .wyhl-navlink { font-size: 0.62rem; letter-spacing: 0.18em; color: #44446a; text-decoration: none; padding-bottom: 2px; }
    .wyhl-navlink:hover { color: #9999CC; }
    .wyhl-navlink.active { color: white; border-bottom: 1px solid #FF4444; }
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

STAR_INFO = {
    "Sirius":          {"constellation": "Canis Major",       "distance_ly": 8.6,      "type": "White main-sequence"},
    "Arcturus":        {"constellation": "Boötes",            "distance_ly": 36.7,     "type": "Red giant"},
    "Vega":            {"constellation": "Lyra",              "distance_ly": 25.0,     "type": "White main-sequence"},
    "Rigel":           {"constellation": "Orion",             "distance_ly": 860,      "type": "Blue supergiant"},
    "Procyon":         {"constellation": "Canis Minor",       "distance_ly": 11.5,     "type": "Yellow-white subgiant"},
    "Betelgeuse":      {"constellation": "Orion",             "distance_ly": 700,      "type": "Red supergiant"},
    "Altair":          {"constellation": "Aquila",            "distance_ly": 16.7,     "type": "White main-sequence"},
    "Aldebaran":       {"constellation": "Taurus",            "distance_ly": 65,       "type": "Red giant"},
    "Antares":         {"constellation": "Scorpius",          "distance_ly": 550,      "type": "Red supergiant"},
    "Spica":           {"constellation": "Virgo",             "distance_ly": 250,      "type": "Blue giant"},
    "Pollux":          {"constellation": "Gemini",            "distance_ly": 33.8,     "type": "Orange giant"},
    "Fomalhaut":       {"constellation": "Piscis Austrinus",  "distance_ly": 25,       "type": "White main-sequence"},
    "Deneb":           {"constellation": "Cygnus",            "distance_ly": 2615,     "type": "White supergiant"},
    "Regulus":         {"constellation": "Leo",               "distance_ly": 79,       "type": "Blue-white main-sequence"},
    "Adhara":          {"constellation": "Canis Major",       "distance_ly": 430,      "type": "Blue supergiant"},
    "Castor":          {"constellation": "Gemini",            "distance_ly": 52,       "type": "Sextuple star system"},
    "Bellatrix":       {"constellation": "Orion",             "distance_ly": 250,      "type": "Blue-white giant"},
    "Elnath":          {"constellation": "Taurus",            "distance_ly": 134,      "type": "Blue-white giant"},
    "Alnilam":         {"constellation": "Orion",             "distance_ly": 2000,     "type": "Blue supergiant"},
    "Alioth":          {"constellation": "Ursa Major",        "distance_ly": 81,       "type": "White main-sequence"},
    "Mirfak":          {"constellation": "Perseus",           "distance_ly": 590,      "type": "Yellow supergiant"},
    "Dubhe":           {"constellation": "Ursa Major",        "distance_ly": 124,      "type": "Orange giant"},
    "Alkaid":          {"constellation": "Ursa Major",        "distance_ly": 104,      "type": "Blue-white main-sequence"},
    "Polaris":         {"constellation": "Ursa Minor",        "distance_ly": 433,      "type": "Yellow supergiant (Cepheid variable)"},
    "Hamal":           {"constellation": "Aries",             "distance_ly": 66,       "type": "Orange giant"},
    "Alpheratz":       {"constellation": "Andromeda",         "distance_ly": 97,       "type": "Blue-white subgiant"},
    "Kochab":          {"constellation": "Ursa Minor",        "distance_ly": 131,      "type": "Orange giant"},
    "Algol":           {"constellation": "Perseus",           "distance_ly": 93,       "type": "Eclipsing binary"},
    "Denebola":        {"constellation": "Leo",               "distance_ly": 36,       "type": "White main-sequence"},
    "Alphecca":        {"constellation": "Corona Borealis",   "distance_ly": 75,       "type": "White main-sequence (binary)"},
    "Mintaka":         {"constellation": "Orion",             "distance_ly": 900,      "type": "Blue supergiant (multiple)"},
    "Schedar":         {"constellation": "Cassiopeia",        "distance_ly": 228,      "type": "Orange giant"},
    "Mizar":           {"constellation": "Ursa Major",        "distance_ly": 78,       "type": "White main-sequence (famous double)"},
    "Izar":            {"constellation": "Boötes",            "distance_ly": 203,      "type": "Orange giant (binary)"},
    "Peacock":         {"constellation": "Pavo",              "distance_ly": 183,      "type": "Blue-white subgiant"},
    "Cor Caroli":      {"constellation": "Canes Venatici",    "distance_ly": 110,      "type": "White main-sequence (binary)"},
    "Andromeda Galaxy":{"constellation": "Andromeda",         "distance_ly": 2_537_000,"type": "Spiral galaxy (M31)"},
    "Beehive Cluster": {"constellation": "Cancer",            "distance_ly": 577,      "type": "Open star cluster (M44)"},
    "Omega Centauri":  {"constellation": "Centaurus",         "distance_ly": 17_000,   "type": "Globular cluster"},
    "Orion Nebula":    {"constellation": "Orion",             "distance_ly": 1344,     "type": "Emission nebula (M42)"},
}

STAR_FACTS = {
    "Sirius":          "the brightest star in the entire night sky — at magnitude −1.46 it can cast faint shadows on a moonless night",
    "Arcturus":        "one of the fastest-moving stars visible to the naked eye, hurtling through space at 122 km/s relative to the Sun",
    "Vega":            "so perfectly studied that in 1850 it became the original zero-point anchor for the entire stellar magnitude scale",
    "Rigel":           "a blue supergiant 120,000× more luminous than the Sun — its light now reaching you left before the last mammoths went extinct",
    "Procyon":         "one of our closest stellar neighbors at just 11.5 light-years; its name is Greek for 'before the dog' because it rises just ahead of Sirius",
    "Betelgeuse":      "a red supergiant so vast it would swallow every planet out to Jupiter if placed where our Sun sits — and it could explode any day",
    "Altair":          "one of the fastest-spinning stars known, rotating so quickly its equator bulges visibly — it completes a full rotation in under 9 hours",
    "Aldebaran":       "the 'eye of the Bull' in Taurus, used by sailors for thousands of years as a navigation reference and still 44× the diameter of our Sun",
    "Antares":         "so large that if it replaced our Sun, its surface would extend past Mars — its name means 'rival of Mars' for its fiery red hue",
    "Spica":           "actually two blue stars so close together they distort into an egg shape from mutual gravity, completing an orbit every four days",
    "Pollux":          "the first star confirmed to host an exoplanet; Pollux b is a giant world 2.3× Jupiter's mass orbiting at 1.6 AU",
    "Fomalhaut":       "surrounded by a dramatic debris ring of comets and dust — one of the first stars where a planet was directly photographed",
    "Deneb":           "one of the most luminous stars in the galaxy: if Deneb were as close as Sirius, it would cast shadows at night and be visible in daytime",
    "Regulus":         "the fastest-spinning bright star we can see — if it were just 16% faster it would tear itself apart from centrifugal force",
    "Adhara":          "the brightest source of ultraviolet light in our sky after the Sun — invisible to human eyes but powerful enough to ionize nearby gas",
    "Castor":          "not one star but six — three pairs of binary stars all gravitationally bound together in a single extraordinary system",
    "Bellatrix":       "the 'Amazon Star,' third-brightest in Orion, and one of the hottest stars visible to the naked eye at 22,000 K",
    "Elnath":          "shared between two constellations: officially in Taurus but once counted as the tip of Auriga the Charioteer as well",
    "Alnilam":         "the middle jewel of Orion's Belt, a blue supergiant so luminous its absolute magnitude rivals Rigel — separated from us by 2,000 light-years",
    "Alioth":          "the brightest star in Ursa Major and a known 'peculiar' star whose chemical composition oscillates on a 5-day cycle",
    "Mirfak":          "the heart of the Alpha Persei Moving Group — a cluster of young blue stars traveling together through space since birth",
    "Dubhe":           "one of the two 'pointer stars' that have guided navigators toward Polaris for millennia, yet it is actually moving away from the others in the Big Dipper",
    "Alkaid":          "the end of the Big Dipper's handle is not part of the Ursa Major moving group — it is a stranger, traveling in the opposite direction",
    "Polaris":         "has not always been the North Star and will not always be — Earth's axial precession will pass the pole to Vega around the year 14,000",
    "Hamal":           "the 'head of the ram,' it was the location of the vernal equinox around 2,000 years ago — now drifted away due to precession",
    "Algol":           "the 'Demon Star' of Perseus — every 2.87 days a dimmer companion eclipses it and the system visibly dims for hours, puzzling ancient astronomers",
    "Denebola":        "the tail of Leo; early Islamic astronomers believed its rising foretold bad luck — in reality it is a young star just 400 million years old",
    "Alphecca":        "the gem of Corona Borealis — its name means 'the bright one of the dish,' and it is actually a spectroscopic binary orbiting in 17.36 days",
    "Mizar":           "the first double star ever resolved through a telescope (1617) and the first star system to be discovered photographically to be a binary",
    "Polaris":         "has not always been the North Star — Earth's axial wobble will move the pole toward Vega by the year 14,000",
    "Peacock":         "named by the British Air Ministry in the 1930s when they needed names for southern stars to teach RAF navigators",
    "Cor Caroli":      "named 'Heart of Charles' to commemorate King Charles II of England; its magnetic field is 1,500 times stronger than our Sun's",
    "Andromeda Galaxy":"the most distant object visible to the naked eye — its light has traveled 2.5 million years to reach your eye, longer than our entire species has existed",
    "Beehive Cluster": "contains at least two confirmed exoplanets — both hot Jupiters orbiting Sun-like stars, making it one of the first clusters with known planets",
    "Omega Centauri":  "the largest and most massive globular cluster in the Milky Way — ten million stars packed into a sphere, possibly the stripped core of a ancient dwarf galaxy",
    "Orion Nebula":    "a stellar nursery just 1,344 light-years away where new solar systems are forming right now — the faint smudge below Orion's Belt is visible to the naked eye",
    "Spica":           "so close to the ecliptic that the Moon frequently passes in front of it — Hipparchus used one such occultation in 127 BC to discover the precession of the equinoxes",
}


def star_fun_fact(name, mag, info, lm_2012, lm_2023, place_name, radiance_by_year):
    base = STAR_FACTS.get(name, "")
    if not place_name:
        return f"{name} is {base}." if base else ""
    city = place_name.split(",")[0]
    if mag <= lm_2023:
        if base:
            return f"You can still spot {name} from {city} on a clear night — it is {base}."
        return f"{name} is still visible from {city} on a clear night."
    elif mag <= lm_2012:
        lost_yr = next(
            (yr for yr in range(2012, 2024)
             if radiance_to_limiting_magnitude(radiance_by_year.get(yr, SD_RADIANCE.get(yr, 20))) < mag),
            2023
        )
        if base:
            return f"{name} slipped out of {city}'s sky around {lost_yr} as light pollution grew — and it is {base}."
        return f"{name} has been lost from {city}'s sky since around {lost_yr}."
    else:
        if base:
            return f"{name} has always needed dark skies beyond {city} to see — it is {base}."
        return f"{name} is too faint to see without a telescope from most urban areas."


SD_RADIANCE = {
    2012: 19.77, 2013: 21.00, 2014: 21.17, 2015: 20.64,
    2016: 20.53, 2017: 20.36, 2018: 20.70, 2019: 20.86,
    2020: 21.15, 2021: 21.29, 2022: 21.50, 2023: 22.68
}


def get_sky_description(lm):
    """Returns (quality_label, bortle_class, approx_stars_visible, experience_text)"""
    if lm >= 4.8:
        return (
            "Bright Suburban", "Bortle 6", "200–300",
            "A grey-white glow hugs the horizon in all directions. On clear, moonless nights "
            "you can trace a faint suggestion of the Milky Way as a slightly brighter band — "
            "washed out and colorless, but there. Major constellations are crisp and most "
            "of their stars are visible. Fainter patterns survive."
        )
    elif lm >= 4.5:
        return (
            "Suburban", "Bortle 7", "100–200",
            "A persistent orange or grey dome sits over your neighborhood all night. The "
            "Milky Way is invisible. Familiar patterns — the Big Dipper, Orion, Leo — are "
            "clear, but the sky between their stars is flat and empty. Faint constellations "
            "are mostly gone."
        )
    elif lm >= 4.2:
        return (
            "Urban Fringe", "Bortle 8", "50–100",
            "The sky glows a visible orange from street lights. Major constellation shapes "
            "survive — you can still trace Orion's Belt and the Big Dipper's handle — but "
            "many of their dimmer stars have vanished. The spaces between constellations are "
            "near-empty. No Milky Way is visible under any conditions."
        )
    elif lm >= 3.8:
        return (
            "City Sky", "Bortle 9", "20–50",
            "The sky has color all night — an orange, yellow, or amber glow stretches from "
            "horizon to horizon. Only the 20–50 brightest stars cut through. On humid or "
            "hazy nights even Orion's Belt can be hard to spot. Airplane lights compete "
            "with the stars."
        )
    else:
        return (
            "Inner City", "Bortle 9+", "< 15",
            "The sky never truly darkens. A uniform orange-white glow fills the night from "
            "horizon to horizon — a permanent artificial dawn. Fewer than 15 stars are "
            "reliably visible: mostly the very brightest giants like Sirius, Arcturus, and "
            "Vega, plus the planets. Most constellation patterns are invisible."
        )


def get_change_reason(pct_change):
    """Returns (headline, explanation)"""
    if pct_change > 20:
        return (
            "Sky significantly brightened",
            "Urban expansion, new commercial development, and widespread LED adoption have "
            "all compounded over this period. LED retrofits can increase total lumens even "
            "while saving energy per fixture — and more buildings, roads, and parking lots "
            "means more light escaping upward into the atmosphere each year."
        )
    elif pct_change > 5:
        return (
            "Sky gradually brightened",
            "Steady regional development and population growth are the most likely drivers. "
            "Each new building, parking lot, and roadway adds incrementally to the aggregate "
            "sky glow measured by satellite. Small annual changes compound quietly over a decade."
        )
    elif pct_change >= -5:
        return (
            "Sky largely stable",
            "Your area's light environment has changed little since 2012. Year-to-year "
            "fluctuations in the satellite data can reflect seasonal cloud cover differences "
            "in the NASA composites as much as real changes on the ground."
        )
    elif pct_change >= -20:
        return (
            "Sky slightly improved",
            "Light levels edged downward — possibly from LED efficiency programs that reduced "
            "total lumens, local lighting ordinances, or shifts in commercial activity. "
            "The 2020 COVID lockdowns also left a visible dip in radiance data for many "
            "urban areas worldwide."
        )
    else:
        return (
            "Sky meaningfully improved",
            "A notable reduction in light pollution since 2012. Your area may have adopted "
            "dark sky policies, completed efficiency-focused LED upgrades, or seen significant "
            "changes in commercial or industrial land use over this period."
        )


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
    rad_2012 = radiance_by_year[2012]
    rad_now = radiance_by_year[year]
    lm_2012 = radiance_to_limiting_magnitude(rad_2012)
    lm_now = radiance_to_limiting_magnitude(rad_now)

    lst = compute_lst(lon, year)
    positions = {}
    altitudes = {}
    for name, mag, ra, dec in stars:
        x, y, alt = ra_dec_to_xy(ra, dec, lat, lst)
        positions[name] = (x, y)
        altitudes[name] = alt

    shapes = []
    annotations = []
    traces = []

    # Horizon circle background
    shapes.append(dict(
        type="circle", xref="x", yref="y",
        x0=-1.0, y0=-1.0, x1=1.0, y1=1.0,
        fillcolor="#03030a",
        line=dict(color="#1a2a4a", width=1.5),
        layer="below"
    ))

    # Light pollution glow
    glow_alpha = min(0.05, max(0, (rad_now - rad_2012) / (rad_2012 * 3)))
    if glow_alpha > 0.001:
        shapes.append(dict(
            type="circle", xref="x", yref="y",
            x0=-1.3, y0=-1.6, x1=1.3, y1=1.0,
            fillcolor=f"rgba(255,102,0,{glow_alpha:.3f})",
            line=dict(color="rgba(0,0,0,0)", width=0),
            layer="below"
        ))

    # Altitude rings
    for alt_deg in [20, 40, 60, 80]:
        r = 1.0 - alt_deg / 90
        shapes.append(dict(
            type="circle", xref="x", yref="y",
            x0=-r, y0=-r, x1=r, y1=r,
            fillcolor="rgba(0,0,0,0)",
            line=dict(color="#2a4a7a", width=0.5, dash="dot"),
            layer="above"
        ))

    # Altitude labels
    for alt_deg in [20, 40, 60]:
        r = 1.0 - alt_deg / 90
        lx = r * 0.866 + 0.02
        ly = r * 0.500
        annotations.append(dict(
            x=lx, y=ly, text=f"{alt_deg}°",
            showarrow=False, font=dict(size=9, color="#2a4a7a"),
            xanchor="left", yanchor="middle"
        ))

    # Compass labels
    for label, angle in [("N", 0), ("E", -math.pi / 2), ("S", math.pi), ("W", math.pi / 2)]:
        cx = 1.12 * math.sin(angle)
        cy = 1.12 * math.cos(angle)
        annotations.append(dict(
            x=cx, y=cy, text=f"<b>{label}</b>",
            showarrow=False, font=dict(size=14, color="#7799CC")
        ))

    # Radial grid lines
    grid_x, grid_y = [], []
    for deg in range(0, 360, 30):
        angle = math.radians(deg)
        grid_x += [0, math.sin(angle), None]
        grid_y += [0, math.cos(angle), None]
    traces.append(go.Scatter(
        x=grid_x, y=grid_y, mode='lines',
        line=dict(color="#2a4a7a", width=0.4, dash="dot"),
        showlegend=False, hoverinfo='skip', name='grid'
    ))

    # Constellation lines
    con_x, con_y = [], []
    for star_a, star_b in constellation_lines:
        if star_a in positions and star_b in positions:
            if altitudes[star_a] >= 0 and altitudes[star_b] >= 0:
                xa, ya = positions[star_a]
                xb, yb = positions[star_b]
                con_x += [xa, xb, None]
                con_y += [ya, yb, None]
    if con_x:
        traces.append(go.Scatter(
            x=con_x, y=con_y, mode='lines',
            line=dict(color="#3a5a8a", width=0.8),
            opacity=0.55, showlegend=False, hoverinfo='skip', name='constellations'
        ))

    # Build star point lists
    vis_x, vis_y, vis_sizes, vis_colors, vis_labels, vis_names = [], [], [], [], [], []
    lost_x, lost_y, lost_sizes, lost_colors_list, lost_labels, lost_label_colors, lost_names = [], [], [], [], [], [], []
    bh_x, bh_y, bh_sizes, bh_colors_list, bh_labels, bh_names = [], [], [], [], [], []

    visible_count = 0
    lost_on_chart = []

    for name, mag, ra, dec in stars:
        x, y = positions[name]
        alt = altitudes[name]
        was_visible = mag <= lm_2012
        is_visible = mag <= lm_now

        if alt < 0:
            if was_visible and not is_visible:
                r = math.sqrt(x * x + y * y)
                px, py = (x / r * 0.97, y / r * 0.97) if r > 1e-6 else (0, 0.97)
                color = color_map.get((name, mag), "#FF4444")
                bh_x.append(px)
                bh_y.append(py)
                bh_sizes.append(max(5, (60 / (mag + 2.5)) ** 0.5 * 1.6))
                bh_colors_list.append(color)
                bh_labels.append(name)
                bh_names.append(name)
                lost_on_chart.append((name, color))
            continue

        if is_visible:
            s = max(6, 90 / (mag + 2.5))
            brightness = min(1.0, max(0.3, 1.0 - mag / 9))
            vis_x.append(x)
            vis_y.append(y)
            vis_sizes.append(max(3, s ** 0.5 * 1.1))
            vis_colors.append(f"rgba(255,255,255,{brightness:.2f})")
            vis_labels.append(name if mag < 1.0 else "")
            vis_names.append(name)
            visible_count += 1
        elif was_visible:
            color = color_map.get((name, mag), "#FF4444")
            s = max(8, 80 / (mag + 2.5))
            lost_x.append(x)
            lost_y.append(y)
            lost_sizes.append(max(5, s ** 0.5 * 1.5))
            lost_colors_list.append(color)
            lost_labels.append(name)
            lost_label_colors.append(color)
            lost_names.append(name)
            lost_on_chart.append((name, color))

    # Visible stars
    if vis_x:
        traces.append(go.Scatter(
            x=vis_x, y=vis_y,
            mode='markers+text',
            marker=dict(symbol='circle', size=vis_sizes, color=vis_colors, line=dict(width=0)),
            text=vis_labels,
            textposition='top center',
            textfont=dict(size=8, color="#7799CC"),
            customdata=vis_names,
            hovertemplate='<b>%{customdata}</b><extra></extra>',
            showlegend=False, name='visible'
        ))

    # Lost stars (above horizon)
    if lost_x:
        traces.append(go.Scatter(
            x=lost_x, y=lost_y,
            mode='markers+text',
            marker=dict(symbol='star', size=lost_sizes, color=lost_colors_list,
                        opacity=0.7, line=dict(width=0)),
            text=lost_labels,
            textposition='top center',
            textfont=dict(size=7, color=lost_label_colors),
            customdata=lost_names,
            hovertemplate='<b>%{customdata}</b><br><i>lost since 2012</i><extra></extra>',
            showlegend=False, name='lost'
        ))

    # Below-horizon lost stars (projected to edge)
    if bh_x:
        traces.append(go.Scatter(
            x=bh_x, y=bh_y,
            mode='markers+text',
            marker=dict(symbol='star', size=bh_sizes, color=bh_colors_list, line=dict(width=0)),
            text=bh_labels,
            textposition='bottom center',
            textfont=dict(size=7, color=bh_colors_list),
            customdata=bh_names,
            hovertemplate='<b>%{customdata}</b><br><i>below horizon</i><extra></extra>',
            opacity=0.35,
            showlegend=False, name='below horizon'
        ))

    # Year label
    annotations.append(dict(
        x=0, y=1.25, text=str(year),
        showarrow=False, font=dict(size=18, color="white"), xanchor="center"
    ))

    # Radiance / count footer
    annotations.append(dict(
        x=0, y=-1.27,
        text=f"{rad_now:.1f} nW/cm²/sr  ·  {visible_count} visible",
        showarrow=False, font=dict(size=10, color="#445566"), xanchor="center"
    ))

    # Legend
    annotations.append(dict(
        x=-1.05, y=-1.1, text="● visible",
        showarrow=False, font=dict(size=9, color="#8899BB"), xanchor="left"
    ))
    annotations.append(dict(
        x=-0.4, y=-1.1, text="★ lost since 2012",
        showarrow=False, font=dict(size=9, color="#CC6666"), xanchor="left"
    ))

    # Magnitude scale
    annotations.append(dict(
        x=0.78, y=-1.03, text="mag",
        showarrow=False, font=dict(size=8, color="#334455"), xanchor="center"
    ))
    sc_x, sc_y, sc_sizes, sc_colors = [], [], [], []
    for i, m in enumerate([1, 2, 3, 4]):
        sx = 0.57 + i * 0.14
        s = max(6, 90 / (m + 2.5))
        brightness = min(1.0, max(0.3, 1.0 - m / 9))
        sc_x.append(sx)
        sc_y.append(-1.1)
        sc_sizes.append(max(3, s ** 0.5 * 1.1))
        sc_colors.append(f"rgba(255,255,255,{brightness:.2f})")
        annotations.append(dict(
            x=sx, y=-1.18, text=str(m),
            showarrow=False, font=dict(size=8, color="#445566"), xanchor="center"
        ))
    traces.append(go.Scatter(
        x=sc_x, y=sc_y, mode='markers',
        marker=dict(symbol='circle', size=sc_sizes, color=sc_colors, line=dict(width=0)),
        showlegend=False, hoverinfo='skip', name='scale'
    ))

    # Click hint annotation
    annotations.append(dict(
        x=0, y=-1.38,
        text="tap a star to explore it",
        showarrow=False, font=dict(size=9, color="#2a3a5a"), xanchor="center"
    ))

    fig = go.Figure(data=traces)
    fig.update_layout(
        paper_bgcolor="#03030a",
        plot_bgcolor="#03030a",
        shapes=shapes,
        annotations=annotations,
        xaxis=dict(range=[-1.2, 1.2], visible=False, fixedrange=True,
                   scaleanchor="y", scaleratio=1),
        yaxis=dict(range=[-1.45, 1.35], visible=False, fixedrange=True),
        margin=dict(l=0, r=0, t=10, b=0),
        showlegend=False,
        dragmode='select',
        clickmode='event+select',
        height=560,
        modebar_remove=["zoom", "pan", "zoomIn", "zoomOut", "autoScale",
                        "resetScale", "select2d", "lasso2d"],
    )

    return fig, lost_on_chart


if "page" not in st.session_state:
    st.session_state.page = "landing"


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
if "star_result" not in st.session_state:
    st.session_state.star_result = None

# Sync page from URL query param
_qp = st.query_params.get("page", None)
if _qp in ("landing", "finder", "stars") and _qp != st.session_state.page:
    st.session_state.page = _qp

# ── Nav bar (fixed, full-width) ───────────────────────────────────────────────
_p = st.session_state.page
st.markdown(f"""
<div class='wyhl-topnav'>
  <a href='?page=landing' target='_self' class='wyhl-brand'>✦ &nbsp;WHAT HAVE YOU LOST</a>
  <div class='wyhl-navlinks'>
    <a href='?page=landing' target='_self' class='wyhl-navlink {"active" if _p == "landing" else ""}'>HOME</a>
    <a href='?page=finder'  target='_self' class='wyhl-navlink {"active" if _p == "finder"  else ""}'>EXPLORE</a>
    <a href='?page=stars'   target='_self' class='wyhl-navlink {"active" if _p == "stars"   else ""}'>STARS</a>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Landing page ──────────────────────────────────────────────────────────────
if st.session_state.page == "landing":
    st.markdown("""
<style>
.stApp {
    background-image:
        linear-gradient(to bottom, rgba(3,3,10,0.55) 0%, rgba(3,3,10,0.75) 55%, rgba(3,3,10,0.97) 100%),
        url('https://science.nasa.gov/wp-content/uploads/2023/09/m31-layered-uv-and-optical.jpg') !important;
    background-size: cover !important;
    background-position: center 30% !important;
    background-attachment: fixed !important;
}
</style>
""", unsafe_allow_html=True)

    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; font-size:3.5rem; letter-spacing:0.25em; color:#FF4444;'>WHAT HAVE YOU LOST</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:0.8rem; letter-spacing:0.3em; color:#6666AA;'>A LIGHT POLLUTION OBSERVATORY</p>", unsafe_allow_html=True)

    st.markdown("""
<p style='text-align:center; max-width:560px; margin:0 auto; font-size:1.05rem; line-height:2.2; color:#8899BB; letter-spacing:0.02em;'>
Every year, artificial light drowns out more of the night sky. Stars that your grandparents could name from memory have silently vanished — not from the universe, but from your view.
</p>
""", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown("""
<div style='display:grid; grid-template-columns:1fr 1fr 1fr; gap:2px; max-width:680px; margin:0 auto;'>
  <div style='background:rgba(10,10,24,0.7); border:1px solid #111133; padding:2rem 1rem; text-align:center; backdrop-filter:blur(4px);'>
    <div style='font-size:2.2rem; font-weight:300; color:white; font-family:"Space Grotesk",sans-serif;'>10+</div>
    <div style='font-size:0.65rem; letter-spacing:0.15em; color:#444466; margin-top:0.5rem;'>YEARS OF DATA</div>
  </div>
  <div style='background:rgba(10,10,24,0.7); border:1px solid #111133; padding:2rem 1rem; text-align:center; backdrop-filter:blur(4px);'>
    <div style='font-size:2.2rem; font-weight:300; color:white; font-family:"Space Grotesk",sans-serif;'>~30K</div>
    <div style='font-size:0.65rem; letter-spacing:0.15em; color:#444466; margin-top:0.5rem;'>US ZIP CODES</div>
  </div>
  <div style='background:rgba(10,10,24,0.7); border:1px solid #111133; padding:2rem 1rem; text-align:center; backdrop-filter:blur(4px);'>
    <div style='font-size:2.2rem; font-weight:300; color:#FF4444; font-family:"Space Grotesk",sans-serif;'>↑ 15%</div>
    <div style='font-size:0.65rem; letter-spacing:0.15em; color:#444466; margin-top:0.5rem;'>AVG SKY GLOW SINCE 2012</div>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br><br><br>", unsafe_allow_html=True)

    st.markdown("""
<p style='text-align:center; max-width:500px; margin:0 auto; font-size:0.85rem; line-height:2; color:#556688;'>
This tool uses NASA Black Marble satellite data to translate raw light radiance into something human — the actual named stars you can no longer see from your backyard, mapped year by year since 2012.
</p>
""", unsafe_allow_html=True)

    st.markdown("<br><br><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("EXPLORE YOUR SKY  →", use_container_width=True):
            st.session_state.page = "finder"
            st.query_params["page"] = "finder"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:0.65rem; letter-spacing:0.1em; color:#333355;'>ENTER YOUR ZIP CODE TO BEGIN</p>", unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; letter-spacing:0.15em; font-size:0.65rem; color:#444466;'>WHY DOES THE DATA STOP AT 2023?</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
<p style='text-align:center; max-width:560px; margin:0 auto; font-size:0.8rem; line-height:2; color:#445566;'>
This tool is built on NASA's Black Marble VNP46A4 dataset — annual composites of nighttime light radiance captured by the VIIRS sensor aboard the Suomi-NPP satellite. 2023 is the most recent complete annual composite currently released by NASA. As new years are published, the data here can be updated to match.
</p>
""", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:0.65rem; letter-spacing:0.1em; color:#334455;'>NASA BLACK MARBLE VNP46A4  ·  BACKGROUND: NASA/GALEX M31</p>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.stop()

# ── Zip code finder ───────────────────────────────────────────────────────────
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

    # Sky quality + change explanation cards
    sky_label_now, sky_bortle_now, sky_stars_now, sky_exp_now = get_sky_description(lm_2023)
    change_headline, change_text = get_change_reason(pct_change)
    sky_color_map = {
        "Inner City": "#FF4444", "City Sky": "#FF9943",
        "Urban Fringe": "#FECA57", "Suburban": "#48DBFB", "Bright Suburban": "#2ED573",
    }
    sky_color_now = sky_color_map.get(sky_label_now, "#8899BB")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
<div style='display:grid; grid-template-columns:1fr 1fr; gap:10px; max-width:860px; margin:0 auto;'>
  <div style='background:#080818; border:1px solid #111133; border-left:2px solid {sky_color_now}; padding:1.4rem 1.5rem;'>
    <p style='font-size:0.58rem; letter-spacing:0.18em; color:#334455; margin:0 0 0.45rem 0;'>WHAT YOUR SKY LOOKS LIKE</p>
    <p style='font-size:1.05rem; color:{sky_color_now}; font-family:"Space Grotesk",sans-serif; font-weight:300; margin:0 0 0.2rem 0;'>{sky_label_now}</p>
    <p style='font-size:0.62rem; letter-spacing:0.08em; color:#334466; margin:0 0 0.9rem 0;'>{sky_bortle_now} &nbsp;·&nbsp; ~{sky_stars_now} stars visible to the naked eye</p>
    <p style='font-size:0.8rem; line-height:1.9; color:#7788AA; margin:0;'>{sky_exp_now}</p>
  </div>
  <div style='background:#080818; border:1px solid #111133; border-left:2px solid #2a3a6a; padding:1.4rem 1.5rem;'>
    <p style='font-size:0.58rem; letter-spacing:0.18em; color:#334455; margin:0 0 0.45rem 0;'>WHY YOUR VISIBILITY CHANGED</p>
    <p style='font-size:1.05rem; color:#8899BB; font-family:"Space Grotesk",sans-serif; font-weight:300; margin:0 0 0.9rem 0;'>{change_headline}</p>
    <p style='font-size:0.8rem; line-height:1.9; color:#7788AA; margin:0;'>{change_text}</p>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; letter-spacing:0.1em; font-size:0.7rem; color:#334466;'>DRAG TO TRAVEL THROUGH TIME</p>",
                unsafe_allow_html=True)

    year = st.slider("", min_value=2012, max_value=2023, value=2012,
                      label_visibility="collapsed")

    col_center = st.columns([1, 6, 1])[1]
    with col_center:
        fig, lost_on_chart = make_sky_chart(STARS, year, radiance_by_year,
                                             color_map, lat, lon, CONSTELLATION_LINES)
        chart_event = st.plotly_chart(
            fig, use_container_width=True,
            on_select="rerun", key="star_chart",
            config={"displayModeBar": False, "responsive": True},
            theme=None
        )

    # Navigate to star info page when a star is tapped
    if chart_event and chart_event.selection and chart_event.selection.points:
        pt = chart_event.selection.points[0]
        raw = getattr(pt, "customdata", None)
        if raw is not None:
            star_name = raw[0] if isinstance(raw, (list, tuple)) else raw
            if star_name and any(s[0] == star_name for s in STARS):
                st.session_state["star_search_input"] = star_name
                st.session_state.page = "stars"
                st.query_params["page"] = "stars"
                st.rerun()

    st.markdown("<p style='text-align:center; font-size:0.7rem; color:#334455; margin-top:-10px;'>face south · center is straight up · stars near the edge sit low on the horizon</p>",
                unsafe_allow_html=True)

    lm_year = radiance_to_limiting_magnitude(radiance_by_year[year])
    sky_label_yr, sky_bortle_yr, sky_stars_yr, sky_exp_yr = get_sky_description(lm_year)
    sky_color_yr = sky_color_map.get(sky_label_yr, "#8899BB")
    st.markdown(f"""
<div style='text-align:center; margin:1.2rem auto 0.2rem; padding:1rem 1.5rem;
     background:#080818; border:1px solid #0e0e2a; max-width:600px; border-radius:2px;'>
  <span style='font-size:0.58rem; letter-spacing:0.18em; color:#334455;'>IN {year} YOUR SKY WAS</span>
  &nbsp;
  <span style='font-size:0.9rem; color:{sky_color_yr}; font-family:"Space Grotesk",sans-serif; font-weight:300;'>{sky_label_yr}</span>
  &nbsp;
  <span style='font-size:0.62rem; color:#334466;'>{sky_bortle_yr} · ~{sky_stars_yr} stars visible</span>
  <p style='font-size:0.78rem; line-height:1.85; color:#556677; margin:0.6rem 0 0; text-align:left;'>{sky_exp_yr}</p>
</div>
""", unsafe_allow_html=True)
    all_lost_for_year = sorted(
        [(n, m) for n, m in star_mags if lm_year < m <= lm_2012],
        key=lambda x: x[1]
    )
    on_chart_names = {name for name, _ in lost_on_chart}

    if all_lost_for_year:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<p style='letter-spacing:0.15em; font-size:0.7rem; color:#333355;'>LOST FROM YOUR SKY BY {year}</p>",
                    unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        html = "<div style='display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px;'>"
        for name, mag in all_lost_for_year:
            color = color_map.get((name, mag), "#FF4444")
            if name in on_chart_names:
                html += f"<div style='color:{color}; font-size:0.85rem;'>★ {name}</div>"
            else:
                html += f"<div style='color:{color}; font-size:0.85rem; opacity:0.4;'>★ {name} <span style='font-size:0.65rem; letter-spacing:0.05em;'>below horizon</span></div>"
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:0.65rem; letter-spacing:0.1em; color:#445566;'>NASA BLACK MARBLE VNP46A4</p>",
                unsafe_allow_html=True)

# ── Stars page ────────────────────────────────────────────────────────────────
if st.session_state.page == "stars":
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; font-size:2.5rem; letter-spacing:0.18em;'>STAR ATLAS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:0.72rem; letter-spacing:0.2em; color:#444466;'>SEARCH THE CATALOG — 68 OBJECTS</p>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        query = st.text_input("", placeholder="try  Sirius · Vega · Betelgeuse · Orion Nebula",
                              label_visibility="collapsed", key="star_search_input")
        searched = st.button("SEARCH", use_container_width=True, key="star_search_btn")

    star_names_lower = {s[0].lower(): s for s in STARS}

    if query:
        matches = [s for s in STARS if query.lower() in s[0].lower()]

        if not matches:
            st.markdown("<p style='text-align:center; color:#442222; margin-top:2rem;'>no match found — try a different name</p>",
                        unsafe_allow_html=True)
        else:
            if len(matches) > 1:
                exact = [s for s in matches if s[0].lower() == query.lower()]
                star = exact[0] if exact else matches[0]
                others = [s[0] for s in matches if s[0] != star[0]][:5]
            else:
                star = matches[0]
                others = []

            name, mag, ra, dec = star
            info = STAR_INFO.get(name, {})

            try:
                wiki_resp = requests.get(
                    f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(name)}",
                    headers={"User-Agent": "WhatHaveYouLost/1.0"},
                    timeout=8
                )
                wiki = wiki_resp.json() if wiki_resp.ok else {}
            except Exception:
                wiki = {}

            description = wiki.get("extract", "")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='text-align:center; font-size:2.8rem; letter-spacing:0.12em; color:white;'>{name}</h2>",
                        unsafe_allow_html=True)
            if info.get("constellation"):
                st.markdown(f"<p style='text-align:center; font-size:0.65rem; letter-spacing:0.2em; color:#445566; margin-top:-0.5rem;'>{info['constellation'].upper()}</p>",
                            unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            ncols = 4 if info.get("distance_ly") else 3
            scols = st.columns(ncols)
            scols[0].metric("Apparent Magnitude", f"{mag:.2f}")
            scols[1].metric("Right Ascension", f"{ra:.3f} h")
            scols[2].metric("Declination", f"{dec:+.2f}°")
            if info.get("distance_ly"):
                d = info["distance_ly"]
                scols[3].metric("Distance", f"{d:,.0f} ly" if d >= 1000 else f"{d} ly")

            if info.get("type"):
                st.markdown("<br>", unsafe_allow_html=True)
                tcols = st.columns(3)
                tcols[0].metric("Classification", info["type"])
                if st.session_state.searched:
                    rb = st.session_state.radiance_by_year
                    lm12 = radiance_to_limiting_magnitude(rb.get(2012, SD_RADIANCE[2012]))
                    lm23 = radiance_to_limiting_magnitude(rb.get(2023, SD_RADIANCE[2023]))
                    if mag <= lm23:
                        vis_label, vis_color = "Visible from your sky", "#2ED573"
                    elif mag <= lm12:
                        vis_label, vis_color = "Lost since 2012", "#FF6B6B"
                    else:
                        vis_label, vis_color = "Too faint for naked eye", "#445566"
                    tcols[1].metric("Visibility", vis_label)
                    st.markdown(f"<p style='font-size:0.65rem; letter-spacing:0.1em; color:{vis_color}; margin-top:-1rem;'>{st.session_state.place_name.upper() if st.session_state.place_name else ''}</p>",
                                unsafe_allow_html=True)

            if others:
                st.markdown(f"<p style='font-size:0.7rem; color:#334455; margin-top:1.5rem;'>other matches: "
                            + "  ·  ".join(f"<span style='color:#556688;'>{o}</span>" for o in others)
                            + "</p>", unsafe_allow_html=True)

            rb = st.session_state.radiance_by_year if st.session_state.searched else SD_RADIANCE
            lm12 = radiance_to_limiting_magnitude(rb.get(2012, SD_RADIANCE[2012]))
            lm23 = radiance_to_limiting_magnitude(rb.get(2023, SD_RADIANCE[2023]))
            fun = star_fun_fact(name, mag, info, lm12, lm23,
                                st.session_state.place_name, rb)
            if fun:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"""
<div style='max-width:680px; margin:0 auto; background:#0a0a18;
     border-left:2px solid #FF4444; padding:1rem 1.5rem; border-radius:0 4px 4px 0;'>
  <p style='font-size:0.65rem; letter-spacing:0.18em; color:#FF4444; margin:0 0 0.4rem 0;'>FUN FACT</p>
  <p style='font-size:0.88rem; line-height:1.9; color:#8899BB; margin:0;'>{fun}</p>
</div>""", unsafe_allow_html=True)

            if description:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"<p style='max-width:680px; margin:0 auto; font-size:0.9rem; line-height:2.1; color:#7788AA;'>{description}</p>",
                            unsafe_allow_html=True)
                st.markdown(f"<p style='max-width:680px; margin:0.5rem auto 0; font-size:0.6rem; letter-spacing:0.08em; color:#334455;'>SOURCE: WIKIPEDIA</p>",
                            unsafe_allow_html=True)

    st.stop()

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; letter-spacing:0.15em; font-size:0.7rem; color:#6666AA;'>HOW IS THIS DIFFERENT</p>",
            unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; max-width:600px; margin:0 auto; font-size:0.9rem; line-height:2; color:#7788AA;'>Tools like Light Pollution Map, NASA Worldview, and Globe at Night show raw radiance data built for researchers. This tool translates that data into something human — the actual named stars you have lost from your specific sky, since 2012.</p>",
            unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)
