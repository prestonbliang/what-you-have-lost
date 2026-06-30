import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import requests
import math
import plotly.graph_objects as go

st.set_page_config(page_title="What Have You Lost?", page_icon="✦", layout="wide")


def inject_js(js: str):
    """Run JS against the parent document (landing page canvas + scroll observer)."""
    components.html(
        f"""<style>html,body{{margin:0;padding:0;background:transparent;overflow:hidden;}}</style>
<script>
(function(window) {{
  var document = window.document;
  var requestAnimationFrame = window.requestAnimationFrame.bind(window);
  var IntersectionObserver = window.IntersectionObserver;
{js}
}})(window.parent);
</script>""",
        height=0,
    )


def canvas_bg(js: str, bg: str = '#03030a'):
    """Full-screen animated canvas background injected into the parent Streamlit DOM."""
    inject_js(f"""
  var _BG_SELS = ['body','#root','.stApp','[data-testid="stApp"]',
    '[data-testid="stAppViewContainer"]','[data-testid="stMain"]','.main',
    '[data-testid="stMainBlockContainer"]','.block-container','section.main'];
  function _applyBg() {{
    document.documentElement.style.setProperty('background','{bg}','important');
    document.documentElement.style.setProperty('background-color','{bg}','important');
    _BG_SELS.forEach(function(s) {{
      document.querySelectorAll(s).forEach(function(el) {{
        el.style.setProperty('background','transparent','important');
        el.style.setProperty('background-color','transparent','important');
        el.style.setProperty('background-image','none','important');
      }});
    }});
  }}
  _applyBg();
  new MutationObserver(_applyBg).observe(document.body, {{childList:true,subtree:true,attributes:true,attributeFilter:['style','class']}});
  var _old = document.getElementById('wyhl-bg');
  if (_old) _old.remove();
  var cv = document.createElement('canvas');
  cv.id = 'wyhl-bg';
  cv.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:-1;pointer-events:none;';
  document.body.insertBefore(cv, document.body.firstChild);
  var ctx = cv.getContext('2d');
  var W, H;
  function resize() {{ W = cv.width = window.innerWidth; H = cv.height = window.innerHeight; }}
  resize();
  window.addEventListener('resize', resize);
{js}
""")


def anim_bg(js: str):
    """Full-screen canvas animation that lives inside its own iframe.

    Uses frameElement to resize the Streamlit component iframe to 100vw x 100vh at
    z-index:-1 so the browser does not throttle requestAnimationFrame. The canvas
    lives inside the iframe; js receives cv, ctx, W, H and a resize() helper.
    """
    components.html(
        f"""<style>html,body{{margin:0;padding:0;overflow:hidden;background:transparent;}}</style>
<script>
(function(){{
  var fe = window.frameElement;
  if (fe) {{
    fe.style.cssText = 'position:fixed!important;top:0!important;left:0!important;' +
      'width:100vw!important;height:100vh!important;z-index:-1!important;' +
      'border:none!important;margin:0!important;padding:0!important;pointer-events:none!important;background:transparent!important;';
  }}
  try {{
    var _ps = window.parent.document.getElementById('wyhl-page-style');
    if (_ps) _ps.remove();
    var _st = window.parent.document.createElement('style');
    _st.id = 'wyhl-page-style';
    _st.textContent = 'body,#root,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMainBlockContainer"],.main,.block-container,section.main{{background:transparent!important}}';
    window.parent.document.head.appendChild(_st);
  }} catch(e) {{}}
  var cv = document.createElement('canvas');
  cv.style.cssText = 'position:fixed;top:0;left:0;display:block;';
  document.body.appendChild(cv);
  var ctx = cv.getContext('2d');
  var W, H;
  var pw = (window.parent !== window) ? window.parent : window;
  function resize() {{ W = cv.width = pw.innerWidth; H = cv.height = pw.innerHeight; }}
  resize();
  pw.addEventListener('resize', resize);
{js}
}})();
</script>""",
        height=0,
    )

st.html("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Space+Grotesk:wght@300;400;500;600&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #03030a; }
    section[data-testid="stSidebar"] { display: none; }
    header[data-testid="stHeader"] { display: none !important; }
    @keyframes pageEnter {
        from { opacity: 0; transform: translateY(18px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .main .block-container {
        max-width: 100%; margin: 0 auto; padding: 5.5rem 2rem 4rem 2rem;
        animation: pageEnter 0.55s cubic-bezier(0.22, 1, 0.36, 1) both;
    }
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
    .wyhl-brand { font-family: 'Space Grotesk',sans-serif; font-size: 0.7rem; letter-spacing: 0.22em; color: #FF4444; text-decoration: none; white-space: nowrap; }
    .wyhl-navlinks { display: flex; gap: 2.5rem; align-items: center; }
    .wyhl-navlink { font-size: 0.62rem; letter-spacing: 0.18em; color: #44446a; text-decoration: none; padding-bottom: 2px; white-space: nowrap; }
    .wyhl-navlink:hover { color: #9999CC; }
    .wyhl-navlink.active { color: white; border-bottom: 1px solid #FF4444; }
    /* Custom right-opening tooltip */
    .tt-wrap { position: relative; display: inline-flex; align-items: center; cursor: help; }
    .tt-icon {
        display: inline-flex; align-items: center; justify-content: center;
        width: 14px; height: 14px; border: 1px solid #333355; border-radius: 50%;
        color: #445566; font-size: 9px; line-height: 1; flex-shrink: 0;
        font-family: 'Inter', sans-serif; font-weight: 400;
    }
    .tt-box {
        display: none; position: absolute; left: calc(100% + 8px); top: 50%;
        transform: translateY(-50%); width: 260px; background: #0a0a18;
        border: 1px solid #222244; border-radius: 4px; padding: 0.8rem 1rem;
        font-size: 0.72rem; line-height: 1.75; color: #8899BB; z-index: 99999;
        pointer-events: none; font-family: 'Inter', sans-serif; text-transform: none;
        letter-spacing: 0; font-weight: 300; white-space: normal;
    }
    .tt-wrap:hover .tt-box { display: block; }
    /* Responsive grid classes */
    .wyhl-grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; }
    .wyhl-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; max-width: 860px; margin: 0 auto; }
    .wyhl-metric-row { display: grid; gap: 1rem; margin-bottom: 1rem; }
    .wyhl-metric-row-1 { grid-template-columns: 1fr; }
    .wyhl-metric-row-2 { grid-template-columns: 1fr 1fr; }
    .wyhl-metric-row-3 { grid-template-columns: 1fr 1fr 1fr; }
    .wyhl-metric-row-4 { grid-template-columns: 1fr 1fr 1fr 1fr; }
    /* Mobile breakpoint */
    @media (max-width: 640px) {
        .main .block-container { padding: 4.5rem 0.75rem 3rem 0.75rem !important; animation: pageEnter 0.55s cubic-bezier(0.22, 1, 0.36, 1) both !important; }
        .wyhl-topnav { padding: 0 0.85rem; }
        .wyhl-brand { font-size: 0.58rem; letter-spacing: 0.1em; }
        .wyhl-navlinks { gap: 1.1rem; }
        .wyhl-navlink { font-size: 0.56rem; letter-spacing: 0.1em; }
        .wyhl-grid-3 { grid-template-columns: 1fr; }
        .wyhl-grid-2 { grid-template-columns: 1fr; }
        .wyhl-metric-row-2 { grid-template-columns: 1fr; }
        .wyhl-metric-row-3 { grid-template-columns: 1fr; }
        .wyhl-metric-row-4 { grid-template-columns: 1fr 1fr; }
        .tt-box {
            left: 50% !important;
            top: auto !important;
            bottom: calc(100% + 8px) !important;
            transform: translateX(-50%) !important;
            width: 220px !important;
        }
    }
</style>
""")

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
    "Sirius":          {"constellation": "Canis Major",       "distance_ly": 8.6,        "type": "White main-sequence",                  "spectral": "A1V",       "temp_k": 9_940,   "luminosity_sun": 25.4,    "radius_sun": 1.71},
    "Arcturus":        {"constellation": "Boötes",            "distance_ly": 36.7,       "type": "Red giant",                            "spectral": "K1.5III",   "temp_k": 4_286,   "luminosity_sun": 170,     "radius_sun": 25.4},
    "Vega":            {"constellation": "Lyra",              "distance_ly": 25.0,       "type": "White main-sequence",                  "spectral": "A0Va",      "temp_k": 9_602,   "luminosity_sun": 40.12,   "radius_sun": 2.36},
    "Rigel":           {"constellation": "Orion",             "distance_ly": 860,        "type": "Blue supergiant",                      "spectral": "B8Ia",      "temp_k": 12_100,  "luminosity_sun": 120_000, "radius_sun": 78.9},
    "Procyon":         {"constellation": "Canis Minor",       "distance_ly": 11.5,       "type": "Yellow-white subgiant",                "spectral": "F5IV-V",    "temp_k": 6_530,   "luminosity_sun": 6.93,    "radius_sun": 2.05},
    "Betelgeuse":      {"constellation": "Orion",             "distance_ly": 700,        "type": "Red supergiant",                       "spectral": "M1-M2Ia",   "temp_k": 3_500,   "luminosity_sun": 100_000, "radius_sun": 887},
    "Altair":          {"constellation": "Aquila",            "distance_ly": 16.7,       "type": "White main-sequence",                  "spectral": "A7V",       "temp_k": 7_550,   "luminosity_sun": 10.6,    "radius_sun": 1.63},
    "Aldebaran":       {"constellation": "Taurus",            "distance_ly": 65,         "type": "Red giant",                            "spectral": "K5III",     "temp_k": 3_910,   "luminosity_sun": 518,     "radius_sun": 44.2},
    "Antares":         {"constellation": "Scorpius",          "distance_ly": 550,        "type": "Red supergiant",                       "spectral": "M1.5Iab",   "temp_k": 3_400,   "luminosity_sun": 75_900,  "radius_sun": 700},
    "Spica":           {"constellation": "Virgo",             "distance_ly": 250,        "type": "Blue giant",                           "spectral": "B1III-IV",  "temp_k": 25_300,  "luminosity_sun": 20_000,  "radius_sun": 7.4},
    "Pollux":          {"constellation": "Gemini",            "distance_ly": 33.8,       "type": "Orange giant",                         "spectral": "K0IIIb",    "temp_k": 4_586,   "luminosity_sun": 32.7,    "radius_sun": 9.06},
    "Fomalhaut":       {"constellation": "Piscis Austrinus",  "distance_ly": 25,         "type": "White main-sequence",                  "spectral": "A3Va",      "temp_k": 8_590,   "luminosity_sun": 16.63,   "radius_sun": 1.84},
    "Deneb":           {"constellation": "Cygnus",            "distance_ly": 2615,       "type": "White supergiant",                     "spectral": "A2Ia",      "temp_k": 8_525,   "luminosity_sun": 196_000, "radius_sun": 203},
    "Regulus":         {"constellation": "Leo",               "distance_ly": 79,         "type": "Blue-white main-sequence",             "spectral": "B8IVn",     "temp_k": 11_060,  "luminosity_sun": 363,     "radius_sun": 3.09},
    "Adhara":          {"constellation": "Canis Major",       "distance_ly": 430,        "type": "Blue supergiant",                      "spectral": "B2Ia",      "temp_k": 22_200,  "luminosity_sun": 38_700,  "radius_sun": 13.9},
    "Castor":          {"constellation": "Gemini",            "distance_ly": 52,         "type": "Sextuple star system",                 "spectral": "A2V",       "temp_k": 10_286,  "luminosity_sun": 52,      "radius_sun": 2.09},
    "Bellatrix":       {"constellation": "Orion",             "distance_ly": 250,        "type": "Blue-white giant",                     "spectral": "B2III",     "temp_k": 22_000,  "luminosity_sun": 6_400,   "radius_sun": 5.75},
    "Elnath":          {"constellation": "Taurus",            "distance_ly": 134,        "type": "Blue-white giant",                     "spectral": "B7III",     "temp_k": 13_600,  "luminosity_sun": 700,     "radius_sun": 4.5},
    "Alnilam":         {"constellation": "Orion",             "distance_ly": 2000,       "type": "Blue supergiant",                      "spectral": "B0Ia",      "temp_k": 27_000,  "luminosity_sun": 400_000, "radius_sun": 42},
    "Alioth":          {"constellation": "Ursa Major",        "distance_ly": 81,         "type": "White main-sequence",                  "spectral": "A0p",       "temp_k": 9_020,   "luminosity_sun": 108,     "radius_sun": 4.15},
    "Mirfak":          {"constellation": "Perseus",           "distance_ly": 590,        "type": "Yellow supergiant",                    "spectral": "F5Ib",      "temp_k": 6_350,   "luminosity_sun": 5_000,   "radius_sun": 60},
    "Dubhe":           {"constellation": "Ursa Major",        "distance_ly": 124,        "type": "Orange giant",                         "spectral": "K0III",     "temp_k": 4_960,   "luminosity_sun": 316,     "radius_sun": 17.0},
    "Alkaid":          {"constellation": "Ursa Major",        "distance_ly": 104,        "type": "Blue-white main-sequence",             "spectral": "B3V",       "temp_k": 20_600,  "luminosity_sun": 594,     "radius_sun": 3.4},
    "Peacock":         {"constellation": "Pavo",              "distance_ly": 183,        "type": "Blue-white subgiant",                  "spectral": "B2IV",      "temp_k": 17_711,  "luminosity_sun": 2_200,   "radius_sun": 4.83},
    "Polaris":         {"constellation": "Ursa Minor",        "distance_ly": 433,        "type": "Yellow supergiant (Cepheid variable)", "spectral": "F7Ib",      "temp_k": 6_015,   "luminosity_sun": 2_500,   "radius_sun": 46},
    "Hamal":           {"constellation": "Aries",             "distance_ly": 66,         "type": "Orange giant",                         "spectral": "K2III",     "temp_k": 4_480,   "luminosity_sun": 91,      "radius_sun": 14.9},
    "Alpheratz":       {"constellation": "Andromeda",         "distance_ly": 97,         "type": "Blue-white subgiant",                  "spectral": "B8IVpMnHg", "temp_k": 13_800,  "luminosity_sun": 200,     "radius_sun": 2.7},
    "Kochab":          {"constellation": "Ursa Minor",        "distance_ly": 131,        "type": "Orange giant",                         "spectral": "K4III",     "temp_k": 4_030,   "luminosity_sun": 450,     "radius_sun": 42},
    "Algol":           {"constellation": "Perseus",           "distance_ly": 93,         "type": "Eclipsing binary",                     "spectral": "B8V",       "temp_k": 12_000,  "luminosity_sun": 98,      "radius_sun": 2.73},
    "Denebola":        {"constellation": "Leo",               "distance_ly": 36,         "type": "White main-sequence",                  "spectral": "A3V",       "temp_k": 8_500,   "luminosity_sun": 15.6,    "radius_sun": 1.73},
    "Alphecca":        {"constellation": "Corona Borealis",   "distance_ly": 75,         "type": "White main-sequence (binary)",         "spectral": "A0V",       "temp_k": 9_700,   "luminosity_sun": 74,      "radius_sun": 3.04},
    "Mintaka":         {"constellation": "Orion",             "distance_ly": 900,        "type": "Blue supergiant (multiple)",           "spectral": "O9.5II",    "temp_k": 29_500,  "luminosity_sun": 90_000,  "radius_sun": 16.5},
    "Schedar":         {"constellation": "Cassiopeia",        "distance_ly": 228,        "type": "Orange giant",                         "spectral": "K0IIIa",    "temp_k": 4_530,   "luminosity_sun": 676,     "radius_sun": 45.1},
    "Phad":            {"constellation": "Ursa Major",        "distance_ly": 84,         "type": "White main-sequence",                  "spectral": "A0Ve",      "temp_k": 9_355,   "luminosity_sun": 63,      "radius_sun": 3.04},
    "Izar":            {"constellation": "Boötes",            "distance_ly": 203,        "type": "Orange giant (binary)",                "spectral": "K0II",      "temp_k": 4_287,   "luminosity_sun": 500,     "radius_sun": 33},
    "Mizar":           {"constellation": "Ursa Major",        "distance_ly": 78,         "type": "White main-sequence (famous double)",  "spectral": "A2V",       "temp_k": 9_000,   "luminosity_sun": 71,      "radius_sun": 2.4},
    "Muphrid":         {"constellation": "Boötes",            "distance_ly": 37,         "type": "Yellow subgiant",                      "spectral": "G0IV",      "temp_k": 6_100,   "luminosity_sun": 9.4,     "radius_sun": 2.67},
    "Porrima":         {"constellation": "Virgo",             "distance_ly": 38,         "type": "Binary (two F-type stars)",            "spectral": "F0V",       "temp_k": 7_124,   "luminosity_sun": 6.9,     "radius_sun": 1.56},
    "Sabik":           {"constellation": "Ophiuchus",         "distance_ly": 88,         "type": "Binary star system",                   "spectral": "A2V",       "temp_k": 8_900,   "luminosity_sun": 43,      "radius_sun": 2.1},
    "Cor Caroli":      {"constellation": "Canes Venatici",    "distance_ly": 110,        "type": "White main-sequence (binary)",         "spectral": "A0Vp",      "temp_k": 11_600,  "luminosity_sun": 48,      "radius_sun": 2.49},
    "Megrez":          {"constellation": "Ursa Major",        "distance_ly": 81,         "type": "White main-sequence",                  "spectral": "A3V",       "temp_k": 9_480,   "luminosity_sun": 14,      "radius_sun": 1.4},
    "Segin":           {"constellation": "Cassiopeia",        "distance_ly": 440,        "type": "Blue-white giant",                     "spectral": "B2IV",      "temp_k": 15_174,  "luminosity_sun": 2_500,   "radius_sun": 6.0},
    "Tania Borealis":  {"constellation": "Ursa Major",        "distance_ly": 133,        "type": "White main-sequence",                  "spectral": "A2V",       "temp_k": 9_050,   "luminosity_sun": 44,      "radius_sun": 2.2},
    "Alula Australis": {"constellation": "Ursa Major",        "distance_ly": 27,         "type": "Yellow dwarf (binary)",                "spectral": "G0V",       "temp_k": 5_900,   "luminosity_sun": 1.4,     "radius_sun": 1.06},
    "Fulu":            {"constellation": "Cassiopeia",        "distance_ly": 630,        "type": "Blue-white giant",                     "spectral": "B2III",     "temp_k": 20_700,  "luminosity_sun": 4_600,   "radius_sun": 7.0},
    "Albali":          {"constellation": "Aquarius",          "distance_ly": 208,        "type": "White main-sequence",                  "spectral": "A7V",       "temp_k": 7_950,   "luminosity_sun": 27,      "radius_sun": 2.5},
    "Andromeda Galaxy":{"constellation": "Andromeda",         "distance_ly": 2_537_000,  "type": "Spiral galaxy (M31)"},
    "Beehive Cluster": {"constellation": "Cancer",            "distance_ly": 577,        "type": "Open star cluster (M44)"},
    "Omega Centauri":  {"constellation": "Centaurus",         "distance_ly": 17_000,     "type": "Globular cluster"},
    "Acubens":         {"constellation": "Cancer",            "distance_ly": 174,        "type": "White main-sequence (binary)",         "spectral": "A5m",       "temp_k": 7_950,   "luminosity_sun": 23,      "radius_sun": 2.27},
    "Propus":          {"constellation": "Gemini",            "distance_ly": 352,        "type": "Red giant",                            "spectral": "M3III",     "temp_k": 3_450,   "luminosity_sun": 2_800,   "radius_sun": 173},
    "Castula":         {"constellation": "Cassiopeia",        "distance_ly": 440,        "type": "Blue-white giant",                     "spectral": "B2IV",      "temp_k": 15_174,  "luminosity_sun": 2_500,   "radius_sun": 6.0},
    "Marfak":          {"constellation": "Perseus",           "distance_ly": 780,        "type": "Blue-white supergiant",                "spectral": "B9Ib",      "temp_k": 10_500,  "luminosity_sun": 6_200,   "radius_sun": 40},
    "Alzirr":          {"constellation": "Gemini",            "distance_ly": 57,         "type": "Yellow-white main-sequence",           "spectral": "F5IV",      "temp_k": 6_630,   "luminosity_sun": 10,      "radius_sun": 1.78},
    "Alula Borealis":  {"constellation": "Ursa Major",        "distance_ly": 400,        "type": "Yellow giant",                         "spectral": "K3III",     "temp_k": 4_100,   "luminosity_sun": 316,     "radius_sun": 34},
    "Jabbah":          {"constellation": "Scorpius",          "distance_ly": 470,        "type": "Multiple star system",                 "spectral": "B2.5III",   "temp_k": 20_000,  "luminosity_sun": 1_900,   "radius_sun": 6.5},
    "Orion Nebula":    {"constellation": "Orion",             "distance_ly": 1344,       "type": "Emission nebula (M42)"},
    "Mekbuda":         {"constellation": "Gemini",            "distance_ly": 1_100,      "type": "Yellow supergiant (Cepheid)",          "spectral": "G0Ib",      "temp_k": 5_800,   "luminosity_sun": 2_600,   "radius_sun": 60},
    "Deneb el Okab":   {"constellation": "Aquila",            "distance_ly": 83,         "type": "White main-sequence",                  "spectral": "A0V",       "temp_k": 9_979,   "luminosity_sun": 29,      "radius_sun": 1.9},
    "47 Tucanae":      {"constellation": "Tucana",            "distance_ly": 14_764,     "type": "Globular cluster"},
    "Ancha":           {"constellation": "Aquarius",          "distance_ly": 181,        "type": "Yellow giant",                         "spectral": "G8III",     "temp_k": 4_870,   "luminosity_sun": 99,      "radius_sun": 12.0},
    "Chara":           {"constellation": "Canes Venatici",    "distance_ly": 27,         "type": "Yellow dwarf (Sun-like)",              "spectral": "G0V",       "temp_k": 5_930,   "luminosity_sun": 1.16,    "radius_sun": 1.09},
    "Asterion":        {"constellation": "Canes Venatici",    "distance_ly": 27,         "type": "Yellow dwarf",                         "spectral": "G0V",       "temp_k": 5_860,   "luminosity_sun": 1.1,     "radius_sun": 1.06},
    "NGC 869":         {"constellation": "Perseus",           "distance_ly": 7_500,      "type": "Open cluster (h Persei)"},
    "Paikauhale":      {"constellation": "Scorpius",          "distance_ly": 430,        "type": "Red supergiant",                       "spectral": "M1Iab",     "temp_k": 3_640,   "luminosity_sun": 45_000,  "radius_sun": 390},
    "Situla":          {"constellation": "Aquarius",          "distance_ly": 199,        "type": "Yellow giant",                         "spectral": "K1III",     "temp_k": 4_760,   "luminosity_sun": 65,      "radius_sun": 10.5},
    "Iota Leporis":    {"constellation": "Lepus",             "distance_ly": 230,        "type": "Blue-white main-sequence",             "spectral": "B3V",       "temp_k": 18_900,  "luminosity_sun": 1_000,   "radius_sun": 3.7},
    "M41":             {"constellation": "Canis Major",       "distance_ly": 2_336,      "type": "Open star cluster"},
    "Gamma Pictoris":  {"constellation": "Pictor",            "distance_ly": 174,        "type": "Yellow-white giant",                   "spectral": "F0III",     "temp_k": 7_000,   "luminosity_sun": 61,      "radius_sun": 5.0},
}

STAR_FACTS = {
    "Sirius":          "the brightest star in the entire night sky — at magnitude −1.46 it can cast faint shadows on a moonless night",
    "Arcturus":        "one of the fastest-moving stars visible to the naked eye, hurtling through space at 122 km/s relative to the Sun",
    "Vega":            "so perfectly studied that in 1850 it became the original zero-point anchor for the entire stellar magnitude scale",
    "Rigel":           "a blue supergiant 120,000× more luminous than the Sun — its light took 860 years to reach your eye, leaving this star around the time the first Gothic cathedrals were being raised in Europe",
    "Procyon":         "one of our closest stellar neighbors at just 11.5 light-years; its name is Greek for 'before the dog' because it rises just ahead of Sirius",
    "Betelgeuse":      "a red supergiant so vast it would swallow every planet out to Jupiter if placed where our Sun sits — and it could explode any day",
    "Altair":          "one of the fastest-spinning stars known, rotating so quickly its equator bulges visibly — it completes a full rotation in under 9 hours",
    "Aldebaran":       "the 'eye of the Bull' in Taurus, used by sailors for thousands of years as a navigation reference and still 44× the diameter of our Sun",
    "Antares":         "so large that if it replaced our Sun, its surface would extend past Mars — its name means 'rival of Mars' for its fiery red hue",
    "Spica":           "actually two blue stars so close their mutual gravity distorts them into an egg shape — they orbit each other every four days, and Spica sits so near the ecliptic that Hipparchus used a lunar occultation of it in 127 BC to discover the precession of the equinoxes",
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
    "Peacock":         "named by the British Air Ministry in the 1930s when they needed names for southern stars to teach RAF navigators",
    "Cor Caroli":      "named 'Heart of Charles' to commemorate King Charles II of England; as a chemically peculiar Ap star its magnetic field is thousands of times stronger than our Sun's",
    "Andromeda Galaxy":"the most distant object visible to the naked eye — its light has traveled 2.5 million years to reach your eye, longer than our entire species has existed",
    "Beehive Cluster": "contains at least two confirmed exoplanets — both hot Jupiters orbiting Sun-like stars, making it one of the first clusters with known planets",
    "Omega Centauri":  "the largest and most massive globular cluster in the Milky Way — ten million stars packed into a sphere, possibly the stripped core of an ancient dwarf galaxy",
    "Orion Nebula":    "a stellar nursery just 1,344 light-years away where new solar systems are forming right now — the faint smudge below Orion's Belt is visible to the naked eye",
}

STAR_HISTORY = {
    "Sirius": (
        "The ancient Egyptians called it Sopdet and built temples aligned to its heliacal rising — "
        "the moment it reappeared before dawn after seventy days of invisibility. That rising announced "
        "the flooding of the Nile and the new year. Sopdet was worshipped as a goddess of fertility for "
        "three thousand years. Greeks and Romans called it the Dog Star, believing its summer appearance "
        "brought the oppressive heat of the 'dog days.' Homer called it an evil omen of autumn. "
        "Polynesian navigators used it to cross the Pacific. No star has been named in more languages "
        "or shaped more calendars than Sirius."
    ),
    "Arcturus": (
        "In 1933, astronomers directed light from Arcturus through a telescope onto a photoelectric cell "
        "to switch on the floodlights at the Chicago World's Fair. The choice was deliberate: the light "
        "arriving that night had left the star in 1883, the same year the previous World's Fair had "
        "ended. To ancient Greeks, Arcturus — 'Bear Watcher' — rose in spring and meant plowing season "
        "had begun. Odysseus navigated by it. It was one of the first stars confirmed to have measurable "
        "proper motion, in 1718, proving that the 'fixed stars' were not fixed at all."
    ),
    "Vega": (
        "From about 12,000 BC to 10,000 BC, Vega was Earth's North Star — long before any human "
        "civilization had writing. Due to the slow wobble of Earth's axis, it will return to that role "
        "around AD 13,727. In 1850, astronomers designated it the original zero-point of the stellar "
        "magnitude scale: when you say a star is magnitude 0.0, you are comparing it to Vega. Its "
        "spectrum was among the first ever photographed, in 1872, opening the era of stellar "
        "spectroscopy."
    ),
    "Rigel": (
        "Arabic astronomers called it Rijl Jauzah — 'the foot of the central one' — and their name, "
        "compressed by medieval Latin scribes, became Rigel. It marked the left foot of Orion, and for "
        "sailors and navigators across every seafaring civilization, finding Orion meant finding Rigel. "
        "It is one of the 58 navigational stars still listed in the Nautical Almanac today. If Rigel "
        "were as close as Sirius, it would shine brighter than a quarter moon and cast sharp shadows "
        "across the landscape."
    ),
    "Procyon": (
        "Its name means 'before the dog' in Greek — Procyon rises about an hour before Sirius, the "
        "Dog Star, and heralds its arrival. Egyptian priests used this sequence as an agricultural "
        "clock: Procyon's appearance meant the Nile flood was imminent. At 11.5 light-years away, "
        "it is one of our closest stellar neighbors. The light you see from Procyon tonight left "
        "during the early 2010s."
    ),
    "Betelgeuse": (
        "Arabic scholars called it Yad al-Jauzā — 'the hand of the central one' — but a medieval "
        "scribe misread the 'y' as a 'b', giving us Betelgeuse. In late 2019, it suddenly dimmed to "
        "its faintest level ever recorded — the 'Great Dimming' — triggering widespread speculation "
        "that it might be about to explode. It was not. But it will. Sometime in the next 100,000 "
        "years, Betelgeuse will ignite as a supernova visible in broad daylight, outshining the full "
        "moon for weeks."
    ),
    "Altair": (
        "In Chinese and Japanese mythology, Altair is the Cowherd Star (Niulang / Hikoboshi), "
        "separated from the Weaver Girl (Vega) by the River of Heaven — the Milky Way. Once a year, "
        "on the seventh night of the seventh lunar month, magpies form a bridge across the stars so "
        "the lovers can meet. This story is still celebrated as Qixi in China and Tanabata in Japan. "
        "Astronomers have directly imaged Altair's surface and confirmed it bulges noticeably at its "
        "equator, flattened by its 9-hour rotation."
    ),
    "Aldebaran": (
        "Its name is Arabic for 'the follower' — Aldebaran rises after, and seems to chase, the "
        "Pleiades across the sky. Ancient Persian astronomers placed it among the four Royal Stars, "
        "cosmic guardians of the seasons, calling it Tascheter, Watcher of the East. It marks the "
        "bloodshot eye of Taurus the Bull. The Pioneer 10 spacecraft, launched in 1972, is currently "
        "drifting in its general direction. In about two million years, it will make a distant flyby."
    ),
    "Antares": (
        "The Greeks named it Antares — 'rival of Ares' — because its ruddy glow so closely mimics "
        "the color of Mars, the war planet. Ancient Persians called it Satevis, Royal Star of the "
        "West, one of four celestial guardians. In Greek sky lore, Orion and Scorpius were ancient "
        "enemies: they were placed on opposite sides of the sky so they could never meet, and Antares "
        "— the Scorpion's heart — rises only as Orion sets. They have been running from each other "
        "since the first myths were told."
    ),
    "Spica": (
        "Around 130 BC, the Greek astronomer Hipparchus compared Spica's position against older "
        "Egyptian records and found it had shifted by about 2 degrees over 150 years. This single "
        "observation led him to discover the precession of Earth's axis — the slow, 26,000-year wobble "
        "that makes the pole stars change over millennia. It was one of the most important astronomical "
        "discoveries of antiquity, and it was made by carefully watching this one star night after "
        "night."
    ),
    "Pollux": (
        "In Greek mythology, Castor and Pollux were twins with different fathers: Pollux was the "
        "immortal son of Zeus, Castor the mortal son of a Spartan king. When Castor died, Pollux was "
        "so grief-stricken he asked Zeus to let them share immortality — so Zeus placed them both in "
        "the sky as Gemini, eternally side by side. In 2006, astronomers discovered that Pollux has "
        "a planet: a giant world 2.3 times Jupiter's mass, making it one of the first confirmed "
        "planets orbiting a giant star."
    ),
    "Fomalhaut": (
        "The 'mouth of the southern fish,' Fomalhaut is the loneliest bright star in the Northern "
        "autumn sky — no comparably bright star lies anywhere near it, earning it the nickname 'the "
        "Autumn Star.' Ancient Persians called it Hastorang, one of the four Royal Stars, guardian "
        "of the South. In 2008, the Hubble Space Telescope photographed what appeared to be a planet "
        "in its dust disk — one of the first direct images of an exoplanet ever taken, still debated "
        "today."
    ),
    "Deneb": (
        "Deneb means 'tail of the hen' in Arabic, marking the tail of Cygnus the Swan. Its exact "
        "distance is uncertain — somewhere between 1,400 and 2,600 light-years — which makes it hard "
        "to pin down its true luminosity, but estimates put it among the most intrinsically bright "
        "stars in the entire galaxy. If Deneb were as close to Earth as Sirius, it would be brighter "
        "than a half-moon and cast crisp shadows. We see it as just another first-magnitude star only "
        "because of the vast distance."
    ),
    "Regulus": (
        "Its name means 'little king' in Latin, a diminutive of Rex. It sits almost exactly on the "
        "ecliptic — the Sun's annual path across the sky — meaning the Moon and planets regularly "
        "pass in front of it, and the Sun comes within half a degree of it every August. Ancient "
        "Babylonian astronomers listed it among their most sacred stars as one of four 'fixed' "
        "anchors of the cosmos. Regulus spins so fast that if it were only 16 percent faster, "
        "centrifugal force would tear it apart."
    ),
    "Adhara": (
        "Adhara is the brightest ultraviolet star in the sky after the Sun — if human eyes could see "
        "UV light, it would outshine every other star. Its name comes from Arabic for 'virgins,' "
        "referring to a group of stars in Canis Major. For observers in the ancient Near East at "
        "certain historical epochs, Adhara briefly served as the south polar star — the southern "
        "counterpart of Polaris — as Earth's axial precession slowly swept the celestial poles "
        "around the sky."
    ),
    "Castor": (
        "Castor appears as one star to the naked eye but is actually six. Through a small telescope "
        "it splits into a pair. Each of those is a spectroscopic binary. A third distant pair of red "
        "dwarfs also orbits the system. Six stars, three pairs, all gravitationally bound. In Greek "
        "mythology, Castor was the mortal twin — the son of a Spartan king — while Pollux was "
        "immortal. When Castor died, Pollux refused to remain in heaven alone, and Zeus honored his "
        "grief by placing them both forever in the sky."
    ),
    "Bellatrix": (
        "Bellatrix means 'the female warrior' in Latin. In medieval European astrology it was a star "
        "of military glory and bold action. It marks the left shoulder of Orion the Hunter, facing "
        "Betelgeuse across the giant's chest. Its name was borrowed in the 20th century by J.K. "
        "Rowling for a character in the Harry Potter series — arguably the most culturally resonant "
        "star name of recent decades. At 22,000 K, Bellatrix is one of the hottest stars visible "
        "to the naked eye."
    ),
    "Elnath": (
        "Elnath means 'the butting one' in Arabic, referring to the tip of one of Taurus the Bull's "
        "horns that it marks. It was formerly shared between two constellations: officially in Taurus "
        "but also counted as Gamma Aurigae in Auriga the Charioteer, until the International "
        "Astronomical Union standardized constellation boundaries in 1930. For centuries, it "
        "simultaneously belonged to two different star stories."
    ),
    "Alnilam": (
        "Alnilam is the middle star of Orion's Belt, and its name comes from Arabic for 'string of "
        "pearls.' These three belt stars are among the most recognized star patterns in all of human "
        "history, appearing in the cosmologies of cultures from the Amazon to Polynesia. Ancient "
        "Egyptians aligned the three great pyramids at Giza to mirror them, and built entrance shafts "
        "angled toward specific stars — a monumental act of sky worship that has lasted 4,500 years."
    ),
    "Alioth": (
        "The brightest star in the Big Dipper, Alioth has an unusual spectrum caused by a strong "
        "magnetic field that creates patches of different chemical abundances on its surface. In Chinese "
        "astronomy it was the fifth star of the Northern Dipper and represented one of the Seven Sages "
        "of the Bamboo Grove. Most of the Big Dipper stars were born together and drift through space "
        "as a family — but Dubhe and Alkaid at either end of the formation are strangers, passing "
        "through by chance."
    ),
    "Mirfak": (
        "Mirfak sits at the heart of the Alpha Persei Moving Group — a loose family of a few hundred "
        "young blue stars that were born together from the same gas cloud about 50 million years ago "
        "and are still traveling in formation through the galaxy. Its name comes from Arabic for 'the "
        "elbow.' In the Perseus myth, the hero holds the severed head of Medusa in one hand — marked "
        "by the blinking demon star Algol — while Mirfak marks his shoulder or elbow, depending on "
        "which ancient map you follow."
    ),
    "Dubhe": (
        "Dubhe and Merak are the two 'pointer stars' of the Big Dipper: a line drawn through them "
        "and extended five times leads directly to Polaris. This navigational trick was known across "
        "the ancient world — Arctic peoples, sailors, and desert travelers all used it independently "
        "before they had words for one another. Dubhe means 'back of the greater bear' in Arabic. "
        "Unlike most Big Dipper stars, Dubhe is not part of the Ursa Major Moving Group and is "
        "slowly drifting away, meaning the Big Dipper's shape is changing over the millennia."
    ),
    "Alkaid": (
        "Alkaid marks the end of the Big Dipper's handle and the tip of Ursa Major's tail. In Arabic "
        "it was called the 'leader of the daughters of the bier' — the three handle stars were the "
        "daughters, leading a funeral procession of the bier (the bowl) around the pole. The Chinese "
        "called the seven Dipper stars Bei Dou and used the direction the handle pointed at dusk as "
        "a seasonal clock — a practice continuous for over two thousand years."
    ),
    "Peacock": (
        "Peacock is one of the few bright stars whose common name comes from a modern constellation "
        "rather than ancient tradition. Pavo the Peacock was invented by the Dutch navigators Pieter "
        "Dirkszoon Keyser and Frederick de Houtman in the 1590s, during the Age of Exploration, to "
        "fill the southern sky that Greek astronomers had never mapped. In the 1930s, the British "
        "Air Ministry needed simple names for southern stars to teach RAF navigators and simply called "
        "it 'Peacock' — so the star's name comes from both the Age of Exploration and the Royal "
        "Air Force."
    ),
    "Polaris": (
        "Polaris was not always the North Star. In ancient Egypt, the pole was marked by Thuban in "
        "Draco. During the classical Greek era, no bright star sat close to the pole at all. Earth's "
        "axis precesses in a slow 26,000-year circle, sweeping the pole among different stars. Polaris "
        "will be closest to true north around the year 2100, then drift away. Centuries from now, the "
        "sky will need a new fixed point — and in about 12,000 years, Vega will hold the title again, "
        "as it did when the first humans crossed into the Americas."
    ),
    "Hamal": (
        "Around 2000 BC, the Sun was in Aries at the spring equinox — meaning the first day of spring "
        "was heralded by the Hamal rising with the Sun. Aries was therefore the first constellation, "
        "and 'The First Point of Aries' still designates the vernal equinox in celestial coordinates, "
        "even though precession has since moved it into Pisces. Ancient Babylonian astronomers treated "
        "Hamal — 'the head of the ram' — as one of the key markers of the year, a role it held for "
        "centuries."
    ),
    "Alpheratz": (
        "Alpheratz marks the head of Andromeda and was historically shared between two constellations: "
        "it was simultaneously the head of Andromeda and the navel of Pegasus (as Delta Pegasi), "
        "until the IAU fixed constellation boundaries in 1930. It anchors both the chain of Andromeda "
        "and the Great Square of Pegasus. Its name comes from Arabic for 'the navel of the horse.' "
        "When you find this star, you are standing at the junction of two ancient star stories."
    ),
    "Kochab": (
        "Kochab was Earth's North Star from roughly 1500 BC to AD 500 — the era spanning the height "
        "of pharaonic Egypt, classical Greece, the Roman Republic and Empire, and the birth of the "
        "world's major religions. Every navigator, soldier, astronomer, and traveler who looked north "
        "during that span of fifteen centuries was looking at Kochab. The Greek astronomer Hipparchus "
        "noticed the pole had shifted since older records and used this to deduce the precession of "
        "Earth's axis in 130 BC — among the most profound observations in the history of science."
    ),
    "Algol": (
        "Ra's al-Ghul — 'the head of the ogre' in Arabic — became Algol through medieval Latin "
        "translation. Ancient observers noticed its periodic, ominous dimming every 2.87 days and "
        "feared it. In 1783, John Goodricke, an 18-year-old deaf English astronomer, watched it "
        "patiently night after night and deduced the truth: a dimmer companion star was regularly "
        "passing in front of a brighter one. He had discovered the eclipsing binary, and with it "
        "revolutionized stellar astronomy. Two years later, aged 21, Goodricke died — before he "
        "learned the Royal Society had awarded him its highest honor."
    ),
    "Denebola": (
        "Denebola marks the tail of Leo the Lion, its name meaning 'tail of the lion' in Arabic. "
        "In medieval European and Arabic astrology it was one of fifteen Behenian fixed stars — a "
        "select group considered particularly powerful for magical and medicinal purposes. Ancient "
        "astrologers considered it unfortunate, associated with disgrace and illness. Modern "
        "astronomers have found it surrounded by a debris disk suggesting a young planetary system "
        "is still forming — a star with a future, not a cursed past."
    ),
    "Alphecca": (
        "Alphecca means 'the bright one of the dish' in Arabic — the dish being the horseshoe shape "
        "of Corona Borealis, the Northern Crown. It was also called Gemma, 'the gem,' for being the "
        "crown's brightest jewel. In Greek mythology, the crown was given to Ariadne by Dionysus "
        "after she was abandoned by Theseus on the island of Naxos, and was placed in the sky as a "
        "memorial to her. Medieval astronomers associated Alphecca with artistic talent and honors "
        "bestowed."
    ),
    "Mintaka": (
        "Mintaka is the westernmost of Orion's Belt stars, and it lies almost exactly on the celestial "
        "equator — meaning it rises almost due east and sets almost due west from virtually any "
        "location on Earth. Ancient architects used this property to orient buildings: the equatorial "
        "rising and setting of Mintaka allowed precise east-west alignment without any instruments "
        "beyond patient observation. The three Belt stars were called the Three Kings, the Three "
        "Sisters, and the String of Pearls by different traditions around the globe."
    ),
    "Mizar": (
        "Mizar was the first double star to be resolved through a telescope, by Giovanni Battista "
        "Riccioli in 1617. Just four decades after Galileo pointed a telescope at the sky, "
        "astronomers were discovering that many 'stars' were actually pairs. In 1889, Mizar became "
        "the first spectroscopic binary ever found — its companion detected not visually but by the "
        "splitting of spectral lines, revealing an unseen companion through the Doppler effect. "
        "Its naked-eye companion Alcor was called 'the horse and rider' and used as an eyesight test "
        "across Arab, Persian, and Indigenous American astronomical traditions."
    ),
    "Muphrid": (
        "Muphrid lies just 3.2 degrees from Arcturus on the sky — close enough that they almost "
        "appear to touch. Despite this, they are not physically related: Arcturus is 37 light-years "
        "from Earth, while Muphrid is about 37.2 — a near-coincidence in distance that places them "
        "in the same neighborhood but on different paths. Its name comes from Arabic for 'the solitary "
        "one of the lance-bearer,' from the figure of Boötes the herdsman in whose constellation both "
        "stars reside."
    ),
    "Porrima": (
        "Porrima was a Roman goddess of prophecy and childbirth, one of the Carmentes, and ancient "
        "Romans named this star for her. In a small telescope, Porrima splits into two nearly "
        "identical yellow-white stars — one of the finest visual binaries in the sky — orbiting each "
        "other once every 169 years. They were closest together as seen from Earth around 2005 and "
        "are now slowly separating again. Through the 18th and 19th centuries, observing their orbit "
        "helped confirm that Newton's law of gravity applied to stars light-years away."
    ),
    "Sabik": (
        "Sabik is in Ophiuchus, the Serpent-Bearer — a constellation that straddles the ecliptic, "
        "meaning the Sun passes through it each year for about eighteen days in late November. "
        "Ophiuchus has sometimes been proposed as a '13th zodiac sign,' though this was never "
        "formally adopted. Its name comes from Arabic for 'the preceding one.' The constellation's "
        "figure, a man wrestling a giant serpent, is ancient: Babylonian star catalogs listed "
        "Ophiuchus's stars over three thousand years ago."
    ),
    "Cor Caroli": (
        "Cor Caroli — 'Heart of Charles' — was named in 1725 by the astronomer Edmond Halley to "
        "honor King Charles II of England, who had restored the monarchy after the English Civil War "
        "and founded the Royal Observatory at Greenwich. It is the prototype of a class of magnetic "
        "stars — Alpha-2 Canum Venaticorum variables — whose strong, organized magnetic fields "
        "concentrate rare elements into patches on their surfaces, causing them to pulse slightly in "
        "brightness as they rotate. Halley is better known for the comet, but his star-naming "
        "legacy endures in Cor Caroli."
    ),
    "Megrez": (
        "Megrez is the faintest of the seven Big Dipper stars, marking the point where the handle "
        "meets the bowl. Its name means 'root of the tail' in Arabic. Despite its relative "
        "faintness, Megrez plays a structural role: it is one of the four bowl stars whose "
        "arrangement defines the Big Dipper's distinctive shape. All four bowl stars — Dubhe, "
        "Merak, Phad, and Megrez — are members of the Ursa Major Moving Group, born from the "
        "same ancient star cluster."
    ),
    "Segin": (
        "Segin is the westernmost of the five main stars forming Cassiopeia's famous W-shape in the "
        "sky. It belongs to the Perseus OB1 stellar association — a sprawling family of young, hot "
        "stars including the Perseus Double Cluster, all born from the same enormous gas cloud a "
        "few million years ago. Cassiopeia herself, in Greek myth, was a vain Ethiopian queen "
        "chained to her throne in the sky as punishment for boasting that her daughter Andromeda "
        "was more beautiful than the sea nymphs."
    ),
    "Tania Borealis": (
        "Tania Borealis means 'northern paw' — it represents one of the front paws of Ursa Major "
        "the Great Bear. In traditional sky maps, the bear's hindquarters and tail form the Big "
        "Dipper, while her paws and feet extend further south in fainter stars. The Arabic names "
        "Tania Borealis ('northern second spring') and Tania Australis ('southern second spring') "
        "come from a centuries-old tradition of describing the bear's anatomy with precise compass "
        "references."
    ),
    "Alula Australis": (
        "Alula Australis was the first binary star to have its orbit computed from observations. "
        "In 1828, French mathematician Félix Savary analyzed decades of measurements and calculated "
        "the orbital elements of Xi Ursae Majoris — demonstrating for the first time that Newton's "
        "law of universal gravitation held between stars trillions of kilometers apart. It was a "
        "landmark moment: the laws that governed falling apples and orbiting planets were confirmed "
        "to govern the stars themselves."
    ),
    "Fulu": (
        "Fulu is an unusual star in Cassiopeia whose common name comes from Chinese astronomy — "
        "where it represented one of the stars in the asterism Teng She, the Flying Serpent. Most "
        "star names reaching the modern era are filtered through Arabic and Latin translations of "
        "Greek sources. Fulu is a rare example of a Chinese astronomical name surviving in common "
        "use, a reminder that the sky was mapped and named by many civilizations independently."
    ),
    "Albali": (
        "Albali is part of Aquarius the Water Bearer, one of the oldest constellations in human "
        "history. Babylonian astronomers identified it over 3,000 years ago and associated it with "
        "the god Ea, who poured water from a vase to cause the great flood. The name Albali comes "
        "from Arabic for 'the good fortune of the swallower,' one of a series of stars in Aquarius "
        "that ancient Arab astronomers labeled with auspicious fortune-telling names tied to the "
        "rainy season."
    ),
    "Andromeda Galaxy": (
        "The Andromeda Galaxy — M31 — is the most distant object visible to the naked eye without "
        "optical aid. At 2.537 million light-years, the light reaching your eyes tonight left before "
        "our species existed. Persian astronomers documented it as early as AD 964, describing it "
        "as 'a little cloud.' It contains roughly a trillion stars — more than the Milky Way — and "
        "is currently approaching us. In about 4.5 billion years, the two galaxies will begin to "
        "merge in a slow, billion-year collision."
    ),
    "Beehive Cluster": (
        "Known as Praesepe — 'the manger' — since antiquity, the Beehive Cluster was used by "
        "ancient Greek and Roman writers as a weather oracle: if the cluster was invisible when the "
        "sky appeared clear, hidden clouds were scattering its combined light, and rain was coming. "
        "Galileo observed it in 1609 and counted at least 40 stars where the naked eye sees only a "
        "soft glow. Modern surveys have found over a thousand stars in the cluster — including at "
        "least two confirmed hot Jupiters, among the first planets found in an open cluster."
    ),
    "Omega Centauri": (
        "Omega Centauri is the largest and most massive globular cluster in the Milky Way — a ball "
        "of roughly ten million stars packed into a sphere 150 light-years across. Edmond Halley "
        "catalogued it as a nebula in 1677 from Saint Helena. Many astronomers suspect it is the "
        "stripped core of a dwarf galaxy absorbed by the Milky Way billions of years ago. At its "
        "center, stars are so densely packed that any planets there would have skies perpetually "
        "bright with stars as brilliant as our full moon."
    ),
    "Acubens": (
        "Acubens marks one of the claws of Cancer the Crab. Its name comes from Arabic for 'the "
        "claws.' Cancer is the faintest of the zodiac constellations — its brightest star barely "
        "reaches magnitude 3.5 — making it one of the first constellations to vanish entirely from "
        "city skies as light pollution grew. Despite its faintness, Cancer held great importance "
        "in ancient astrology: the Sun entered Cancer at the summer solstice from roughly 2000 BC "
        "to 100 BC, giving the Tropic of Cancer its enduring name."
    ),
    "Propus": (
        "Propus means 'forward foot' in Greek — it marks the foot of Castor in Gemini. On March 13, "
        "1781, the astronomer William Herschel was sweeping this area of sky when he noticed a "
        "small disk-shaped object that he first took for a comet. Over following nights he realized "
        "it wasn't moving like a comet and had no tail: he had discovered Uranus, the first new "
        "planet found in recorded history. Propus was simply the signpost that pointed him to the "
        "right patch of sky."
    ),
    "Castula": (
        "Castula is a faint star in Cassiopeia whose name is a modern Latin coinage, approved by "
        "the International Astronomical Union's Working Group on Star Names as part of a 21st-century "
        "effort to give official proper names to the brightest stars without them. The project "
        "drew on historical star catalogs, cultural traditions, and proposals from astronomers "
        "worldwide — acknowledging that the sky belongs to all of humanity."
    ),
    "Marfak": (
        "Marfak is one of several stars sharing this name or close variants — from Arabic al-marfiq, "
        "'the elbow.' This one sits in Perseus near Mirfak (also 'elbow') and belongs to the Alpha "
        "Persei Moving Group, the extended family of young stars born together from the same gas "
        "cloud some 50 million years ago. In the myth of Perseus, this region of the sky represents "
        "the hero's arm or elbow as he holds aloft Medusa's severed head."
    ),
    "Alzirr": (
        "Alzirr sits near the foot of Pollux in Gemini. Its name comes from Arabic for 'the button' "
        "or possibly 'the seed,' from an older star-group designation in that region. In Chinese "
        "astronomy, the area around Alzirr was part of the Well lunar mansion — one of the 28 "
        "segments into which Chinese astronomers divided the sky along the Moon's monthly path. "
        "The Chinese Well asterism was associated with water, wells, and irrigation."
    ),
    "Alula Borealis": (
        "Alula Borealis is the 'northern first spring' — the companion to Alula Australis in "
        "Ursa Major's hind paw. Though they appear close in the sky and share a name, the two "
        "Alula stars are not physically related: Alula Australis is 28 light-years away, while "
        "Alula Borealis lies some 150 light-years distant. Their apparent proximity is a projection "
        "effect — a visual coincidence written across depth of space."
    ),
    "Jabbah": (
        "Jabbah is a multiple star system in Scorpius, its name coming from Arabic for 'the "
        "forehead' of the Scorpion. It contains at least five stars in a complex gravitational "
        "arrangement. The forehead of Scorpius arcs across some of the richest star fields in the "
        "Milky Way — this entire region of sky was deeply important to Mesopotamian astronomers, "
        "who mapped the Scorpion's stars over four thousand years ago in clay tablets still "
        "surviving today."
    ),
    "Orion Nebula": (
        "The Orion Nebula — M42 — is a stellar nursery 1,344 light-years away where new suns and "
        "planetary systems are forming at this moment. It has been observed since antiquity but its "
        "nature was unknown: Christiaan Huygens first described it as a nebula in 1659, and "
        "subsequent observers found it grew steadily more complex with better telescopes. The Hubble "
        "Space Telescope photographed hundreds of protoplanetary disks within it — the raw material "
        "of future worlds — making the Orion Nebula the closest and best-studied cradle of "
        "star birth."
    ),
    "Mekbuda": (
        "Mekbuda is a Cepheid variable star — it pulsates in brightness every 10.15 days as the "
        "star physically expands and contracts. The name comes from Arabic for 'folded paw.' "
        "Cepheid variables are among the most important tools in astronomy: the period of their "
        "pulsation is directly proportional to their true luminosity. Discovered by Henrietta Swan "
        "Leavitt in 1908, this relationship — the period-luminosity law — allowed Edwin Hubble to "
        "measure the distance to galaxies and prove the universe was far larger than anyone had "
        "imagined."
    ),
    "Deneb el Okab": (
        "Deneb el Okab means 'tail of the eagle' in Arabic, and it marks the tail of Aquila the "
        "Eagle. In Greek mythology, Aquila was Zeus's eagle, the bearer of his thunderbolts and "
        "the abductor of the beautiful youth Ganymede, who was brought to Olympus to serve as "
        "cup-bearer to the gods. The entire region of Aquila sits in one of the richest parts of "
        "the Milky Way visible from Earth's northern hemisphere."
    ),
    "47 Tucanae": (
        "47 Tucanae is one of the most massive globular clusters known — millions of stars packed "
        "into a sphere 120 light-years across, roughly 16,000 light-years from Earth. It appears "
        "in the southern sky adjacent to the Small Magellanic Cloud, a visual coincidence that masks "
        "an enormous difference in distance. Its stars are among the oldest known, roughly 13 "
        "billion years old, meaning they formed when the universe itself was barely 700 million years "
        "old. Early SETI researchers searched 47 Tucanae for radio signals from intelligent life."
    ),
    "Ancha": (
        "Ancha is part of Aquarius the Water Bearer. Its name means 'the haunch' in Arabic. "
        "Aquarius is one of the oldest documented constellations, traced to Babylonian star lists "
        "from before 1200 BC where it was associated with the god Ea, bringer of floods. The "
        "ancient association between this region of sky and water is not arbitrary: the Sun passes "
        "through Aquarius during the Southern Hemisphere's rainy season, and various ancient "
        "cultures connected the celestial water-pourer to the rains that sustained agriculture."
    ),
    "Chara": (
        "Chara means 'joy' in Greek. Together with Cor Caroli and its nearby companion Asterion, "
        "it represents one of the two hunting dogs held on a leash by Boötes the herdsman in the "
        "constellation Canes Venatici. Johannes Hevelius invented this constellation in 1687, and "
        "the Greek names he chose have a certain poetry: one dog is 'joy,' the other 'the starry "
        "one,' and their leash is held by an eternal guardian of the sky."
    ),
    "Asterion": (
        "Asterion means 'little star' or 'starry one' in Greek — the other of the two hunting "
        "dogs in Canes Venatici. The pair of dogs were described in early sky atlases as Asterion "
        "and Chara, straining forward on their leash as Boötes drives the Great Bear around the "
        "pole. The constellation was invented in the 17th century by the Polish astronomer Johannes "
        "Hevelius, one of the last figures to create new constellations that are still recognized "
        "today."
    ),
    "NGC 869": (
        "NGC 869 is the brighter component of the Perseus Double Cluster — two young, rich open "
        "clusters side by side, both visible to the naked eye as a hazy double glow. The Greek "
        "astronomer Hipparchus catalogued them around 130 BC. The two clusters are physically "
        "close — separated by only about 100 light-years — and were born from the same vast cloud "
        "of gas roughly 12 million years ago. On dark nights they are among the finest naked-eye "
        "objects in the northern sky. From light-polluted cities, they are completely invisible."
    ),
    "Paikauhale": (
        "Paikauhale is a star in Scorpius whose name comes from Hawaiian astronomical tradition "
        "— one of a growing number of stars given names from non-European sky cultures by the "
        "International Astronomical Union's Working Group on Star Names, which since 2016 has "
        "approved names from Chinese, Arabic, Polynesian, Indigenous Australian, Māori, and "
        "other traditions. This effort recognizes that every civilization that could see the sky "
        "developed a relationship with it — and that those relationships deserve to be remembered."
    ),
    "Situla": (
        "Situla means 'water bucket' or 'urn' in Latin. It marks one of the water vessels in "
        "Aquarius the Water Bearer. In ancient Babylonian star lore, the region of Aquarius was "
        "called 'The Great One,' and its stars were associated with the god Ea's gift of water "
        "to humankind. The constellation's water-pouring figure has persisted in sky mythology "
        "for over four thousand years, across Babylonian, Egyptian, Greek, and Arabic traditions."
    ),
    "Iota Leporis": (
        "Iota Leporis is a star in Lepus the Hare — the small constellation crouching under "
        "Orion's feet, perpetually fleeing the Hunter and his dogs. Lepus is one of the 48 original "
        "constellations listed by the Greek astronomer Claudius Ptolemy in his 2nd-century "
        "Almagest, and it has remained unchanged in the modern sky map. The hare's ancient role "
        "as cosmic prey — forever beneath the Hunter and just ahead of the Dogs — makes it one "
        "of astronomy's most enduring mythological scenes."
    ),
    "M41": (
        "M41 is an open star cluster in Canis Major, about four degrees south of Sirius. Aristotle "
        "mentioned a cloudy spot in this location around 325 BC — making M41 one of the oldest "
        "recorded deep-sky objects in history. Charles Messier catalogued it in 1765. It contains "
        "roughly 100 stars, some of them red giants, spread across a region of sky about twice the "
        "apparent width of the full Moon. From a dark sky it is visible to the naked eye as a "
        "faint smudge near the brightest star in the sky."
    ),
    "Gamma Pictoris": (
        "Gamma Pictoris is in the constellation Pictor, the Painter's Easel — one of 14 southern "
        "constellations invented by French astronomer Nicolas Louis de Lacaille during his landmark "
        "survey of the southern sky from the Cape of Good Hope in 1751-52. Lacaille named his new "
        "constellations after Enlightenment-era scientific instruments and tools: the Telescope, "
        "the Microscope, the Air Pump, the Chemical Furnace, the Sculptor's Workshop, and the "
        "Painter's Easel among them — a sky full of the tools of reason."
    ),
    "Phad": (
        "Phad marks one of the four bowl stars of the Big Dipper, from Arabic for 'the thigh' of "
        "the Great Bear. Like Alioth, Merak, and Megrez, Phad is a genuine member of the Ursa "
        "Major Moving Group — a dispersed cluster of stars born from the same nebula about 300 "
        "million years ago and still drifting through space together. The Great Bear asterism they "
        "form has been the most important navigational star group in the Northern Hemisphere for "
        "the entirety of recorded human history."
    ),
}


def temp_to_star_color(temp_k):
    if temp_k >= 30_000: return "#9bb0ff"
    if temp_k >= 20_000: return "#aabfff"
    if temp_k >= 10_000: return "#cad7ff"
    if temp_k >= 7_500:  return "#f8f7ff"
    if temp_k >= 6_000:  return "#fff4ea"
    if temp_k >= 5_000:  return "#ffd2a1"
    if temp_k >= 3_500:  return "#ffb347"
    return "#ff6b35"


def metric_card(label, value, tooltip, sublabel=None, sublabel_color="#2ED573", value_color="white"):
    sub_html = ""
    if sublabel:
        sub_html = (
            "<div style='font-size:0.65rem; letter-spacing:0.1em; margin-top:0.25rem; color:"
            + sublabel_color + ";'>" + sublabel + "</div>"
        )
    return (
        "<div style='background:#0d0d1a; border:1px solid #111133; border-radius:4px; padding:1.25rem;'>"
        "<div style='display:flex; align-items:center; gap:5px; margin-bottom:0.25rem;'>"
        "<span style='color:#555577; font-size:11px; letter-spacing:0.15em; text-transform:uppercase;'>"
        + label +
        "</span><span class='tt-wrap'><span class='tt-icon'>?</span>"
        "<span class='tt-box'>" + tooltip + "</span></span>"
        "</div>"
        "<div style='color:" + value_color + "; font-size:2rem; font-weight:300;'>"
        + str(value) +
        "</div>"
        + sub_html
        + "</div>"
    )


def metrics_row(cards, cols=None):
    n = cols if cols is not None else len(cards)
    return (
        f"<div class='wyhl-metric-row wyhl-metric-row-{n}'>"
        + "".join(cards) + "</div>"
    )


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
            "horizon to horizon. Only the brightest stars cut through. On humid or hazy "
            "nights even Orion's Belt can be hard to spot. Airplane lights compete "
            "with the stars."
        )
    else:
        return (
            "Inner City", "Bortle 9+", "25–50",
            "The sky never truly darkens. A uniform orange-white glow fills the night from "
            "horizon to horizon — a permanent artificial dawn. Only the very brightest stars "
            "— Sirius, Arcturus, Vega — cut through the haze. Most constellation patterns "
            "are completely invisible."
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
                bh_labels.append("")
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
            lost_labels.append("")
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
            textfont=dict(size=10, color="#7799CC"),
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
            textfont=dict(size=9, color=lost_label_colors),
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
            textfont=dict(size=9, color=bh_colors_list),
            customdata=bh_names,
            hovertemplate='<b>%{customdata}</b><br><i>below horizon</i><extra></extra>',
            opacity=0.35,
            showlegend=False, name='below horizon'
        ))

    fig = go.Figure(data=traces)
    fig.update_layout(
        paper_bgcolor="#03030a",
        plot_bgcolor="#03030a",
        shapes=shapes,
        annotations=annotations,
        xaxis=dict(range=[-1.2, 1.2], visible=False, fixedrange=True,
                   scaleanchor="y", scaleratio=1),
        yaxis=dict(range=[-1.15, 1.15], visible=False, fixedrange=True),
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        dragmode=False,
        clickmode='event+select',
        height=650,
        modebar_remove=["zoom", "pan", "zoomIn", "zoomOut", "autoScale",
                        "resetScale", "select2d", "lasso2d"],
    )

    return fig, lost_on_chart, visible_count, rad_now


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

# Navigate to star info when an HTML link passes ?star=Name
_star_qp = st.query_params.get("star", None)
if _star_qp and any(s[0] == _star_qp for s in STARS):
    st.session_state["star_search_input"] = _star_qp
    st.session_state.page = "stars"
    del st.query_params["star"]

# ── Nav bar (fixed, full-width) ───────────────────────────────────────────────
_p = st.session_state.page
st.html(f"""
<div class='wyhl-topnav'>
  <a href='?page=landing' target='_self' class='wyhl-brand'>✦ &nbsp;WHAT HAVE YOU LOST</a>
  <div class='wyhl-navlinks'>
    <a href='?page=landing' target='_self' class='wyhl-navlink {"active" if _p == "landing" else ""}'>HOME</a>
    <a href='?page=finder'  target='_self' class='wyhl-navlink {"active" if _p == "finder"  else ""}'>EXPLORE</a>
    <a href='?page=stars'   target='_self' class='wyhl-navlink {"active" if _p == "stars"   else ""}'>STARS</a>
  </div>
</div>
""")

# ── Landing page ──────────────────────────────────────────────────────────────
if st.session_state.page == "landing":
    st.html("""
<style>
html { background: #03030a !important; }
body, #root { background: transparent !important; }
.stApp, [data-testid="stAppViewContainer"], .main { background: transparent !important; background-image: none !important; }
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(28px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes glowPulse {
    0%, 100% { text-shadow: 0 0 20px rgba(255,68,68,0.25); }
    50%       { text-shadow: 0 0 55px rgba(255,68,68,0.6), 0 0 110px rgba(255,68,68,0.18); }
}
.wyhl-tl-entry {
    opacity: 0;
    transform: translateX(-18px);
    transition: opacity 0.65s ease, transform 0.65s ease;
}
.wyhl-tl-entry.visible {
    opacity: 1;
    transform: translateX(0);
}
</style>
""")
    inject_js("""
  var old = document.getElementById('wyhl-bg');
  if (old) old.remove();
  var cv = document.createElement('canvas');
  cv.id = 'wyhl-bg';
  cv.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:-1;pointer-events:none;';
  document.body.insertBefore(cv, document.body.firstChild);
  var ctx = cv.getContext('2d');
  var W, H, cx, cy;
  function resize() { W = cv.width = window.innerWidth; H = cv.height = window.innerHeight; cx = W/2; cy = H/2; }
  resize();
  window.addEventListener('resize', resize);

  var SPEED = 0.0007, FOV = 260;
  var COLS = [[200,215,255],[255,245,220],[255,210,170],[180,205,255]];
  function mkStar(z) {
    return { x:(Math.random()-0.5)*2, y:(Math.random()-0.5)*2, z:z!==undefined?z:(0.02+Math.random()*0.96),
             pz:null, col:COLS[Math.random()*COLS.length|0], tw:Math.random()*6.28, twr:0.006+Math.random()*0.014 };
  }
  var stars = [];
  for (var i=0; i<320; i++) stars.push(mkStar());

  var NEBS = [
    {fx:0.72,fy:0.28,r:0.32,rgb:'70,12,95',a:0.14},
    {fx:0.18,fy:0.62,r:0.26,rgb:'12,28,100',a:0.11},
    {fx:0.48,fy:0.82,r:0.22,rgb:'95,12,22',a:0.09},
  ];
  var nT=0, shooters=[], shootCd=220+Math.random()*280, frame=0;

  function drawShip(x,y,ang,s,a) {
    ctx.save(); ctx.translate(x,y); ctx.rotate(ang); ctx.globalAlpha=a;
    ctx.strokeStyle='#8899bb'; ctx.lineWidth=0.9; ctx.lineCap='round'; ctx.lineJoin='round';
    ctx.beginPath(); ctx.moveTo(0,-s*2); ctx.lineTo(s*0.5,s*0.5); ctx.lineTo(0,s*0.2); ctx.lineTo(-s*0.5,s*0.5); ctx.closePath(); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(s*0.4,s*0.1); ctx.lineTo(s*1.5,s*0.8); ctx.lineTo(s*0.5,s*0.5); ctx.closePath(); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(-s*0.4,s*0.1); ctx.lineTo(-s*1.5,s*0.8); ctx.lineTo(-s*0.5,s*0.5); ctx.closePath(); ctx.stroke();
    ctx.beginPath(); ctx.ellipse(0,-s*0.8,s*0.18,s*0.28,0,0,6.28); ctx.strokeStyle='rgba(100,160,220,'+(a*4)+')'; ctx.lineWidth=0.6; ctx.stroke();
    var gp=0.4+0.6*(0.5+0.5*Math.sin(frame*0.07));
    var eg=ctx.createRadialGradient(0,s*0.5,0,0,s*0.5,s*0.85);
    eg.addColorStop(0,'rgba(255,110,50,'+(gp*a*6)+')'); eg.addColorStop(0.5,'rgba(255,70,30,'+(gp*a*1.5)+')'); eg.addColorStop(1,'rgba(255,50,20,0)');
    ctx.fillStyle=eg; ctx.globalAlpha=a; ctx.fillRect(-s*2,0,s*4,s*2);
    ctx.restore();
  }

  var lastT=0, FRATE=1000/42;
  function draw(t) {
    requestAnimationFrame(draw);
    if (t-lastT < FRATE) return;
    lastT=t; frame++; nT+=0.00025;
    ctx.fillStyle='#03030a'; ctx.fillRect(0,0,W,H);

    for (var ni=0; ni<NEBS.length; ni++) {
      var n=NEBS[ni];
      var nx=(n.fx+Math.sin(nT+ni*1.8)*0.022)*W, ny=(n.fy+Math.cos(nT*0.75+ni*2.3)*0.018)*H, nr=n.r*Math.min(W,H);
      var g=ctx.createRadialGradient(nx,ny,0,nx,ny,nr);
      g.addColorStop(0,'rgba('+n.rgb+','+n.a+')'); g.addColorStop(0.45,'rgba('+n.rgb+','+(n.a*0.4)+')'); g.addColorStop(1,'rgba('+n.rgb+',0)');
      ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
    }

    for (var si=0; si<stars.length; si++) {
      var s=stars[si]; s.pz=s.z; s.z-=SPEED;
      if (s.z<=0.004) { stars[si]=mkStar(0.97+Math.random()*0.03); continue; }
      var sx=cx+s.x*FOV/s.z, sy=cy+s.y*FOV/s.z;
      if (sx<-25||sx>W+25||sy<-25||sy>H+25) { stars[si]=mkStar(0.97+Math.random()*0.03); continue; }
      s.tw+=s.twr;
      var depth=1-s.z, a=Math.min(1,(0.2+depth*0.8)*(0.65+0.35*Math.sin(s.tw))), r=Math.max(0.25,depth*2.0);
      if (s.pz>0.01) {
        var px=cx+s.x*FOV/s.pz, py=cy+s.y*FOV/s.pz;
        if (Math.hypot(sx-px,sy-py)>0.4) {
          var tg=ctx.createLinearGradient(px,py,sx,sy);
          tg.addColorStop(0,'rgba('+s.col+',0)'); tg.addColorStop(1,'rgba('+s.col+','+(a*0.45)+')');
          ctx.beginPath(); ctx.moveTo(px,py); ctx.lineTo(sx,sy);
          ctx.strokeStyle=tg; ctx.lineWidth=Math.max(0.4,r*0.55); ctx.stroke();
        }
      }
      ctx.beginPath(); ctx.arc(sx,sy,r,0,6.28); ctx.fillStyle='rgba('+s.col+','+a+')'; ctx.fill();
      if (depth>0.82) { ctx.beginPath(); ctx.arc(sx,sy,r*2.8,0,6.28); ctx.fillStyle='rgba('+s.col+','+(a*0.1)+')'; ctx.fill(); }
    }

    var SHIP_IN=220, shipT=Math.min(1,frame/SHIP_IN), shipE=shipT<1?1-Math.pow(1-shipT,3):1;
    var shipX=shipT<1?W*(1.18-shipE*0.38):W*0.80+Math.sin(frame*0.006)*6;
    var shipY=shipT<1?H*(-0.12+shipE*0.34):H*0.22+Math.cos(frame*0.004)*4;
    var shipA=Math.min(0.28,shipE*0.36);
    drawShip(shipX, shipY, -0.2+Math.sin(frame*0.006)*0.08, 11, shipA);

    if (--shootCd<=0) {
      shooters.push({x:Math.random()*W*0.75,y:-5+Math.random()*H*0.45,vx:6+Math.random()*10,vy:2.5+Math.random()*5,life:1,mLen:65+Math.random()*75});
      shootCd=240+Math.random()*350;
    }
    shooters=shooters.filter(function(sh){return sh.life>0.01;});
    for (var shi=0; shi<shooters.length; shi++) {
      var sh=shooters[shi], spd=Math.hypot(sh.vx,sh.vy);
      var tx=sh.x-sh.vx/spd*sh.mLen, ty=sh.y-sh.vy/spd*sh.mLen;
      var sg=ctx.createLinearGradient(tx,ty,sh.x,sh.y);
      sg.addColorStop(0,'rgba(200,215,255,0)'); sg.addColorStop(1,'rgba(220,232,255,'+(sh.life*0.82)+')');
      ctx.beginPath(); ctx.moveTo(tx,ty); ctx.lineTo(sh.x,sh.y);
      ctx.strokeStyle=sg; ctx.lineWidth=1.6; ctx.stroke();
      sh.x+=sh.vx; sh.y+=sh.vy; sh.life-=0.028;
      if (sh.x>W+100||sh.y>H+100) sh.life=0;
    }
  }
  requestAnimationFrame(draw);
""")
    st.html("""
<style>
html {
    background-color: #03030a !important;
    background-image:
        radial-gradient(ellipse 60% 45% at 72% 28%, rgba(100,18,160,0.58), transparent 62%),
        radial-gradient(ellipse 55% 40% at 18% 65%, rgba(18,45,185,0.50), transparent 58%),
        radial-gradient(ellipse 50% 36% at 52% 90%, rgba(160,18,35,0.44), transparent 55%),
        radial-gradient(circle 2px at 8.3% 12.7%, rgba(210,225,255,0.88), transparent),
        radial-gradient(circle 3px at 23.1% 5.4%, rgba(255,252,230,0.92), transparent),
        radial-gradient(circle 2px at 41.6% 18.2%, rgba(255,255,255,0.80), transparent),
        radial-gradient(circle 2px at 58.9% 7.3%, rgba(210,225,255,0.85), transparent),
        radial-gradient(circle 3px at 74.2% 22.8%, rgba(255,252,230,0.94), transparent),
        radial-gradient(circle 2px at 87.5% 11.4%, rgba(255,220,185,0.82), transparent),
        radial-gradient(circle 2px at 3.8% 35.1%, rgba(210,225,255,0.75), transparent),
        radial-gradient(circle 2px at 16.4% 48.6%, rgba(255,255,255,0.70), transparent),
        radial-gradient(circle 2px at 31.7% 42.3%, rgba(255,252,230,0.78), transparent),
        radial-gradient(circle 3px at 48.3% 38.9%, rgba(210,225,255,0.90), transparent),
        radial-gradient(circle 2px at 65.8% 44.1%, rgba(255,220,185,0.80), transparent),
        radial-gradient(circle 2px at 81.2% 33.7%, rgba(255,252,230,0.72), transparent),
        radial-gradient(circle 2px at 92.6% 56.4%, rgba(210,225,255,0.78), transparent),
        radial-gradient(circle 2px at 12.9% 62.8%, rgba(255,255,255,0.68), transparent),
        radial-gradient(circle 3px at 29.4% 71.5%, rgba(210,225,255,0.86), transparent),
        radial-gradient(circle 2px at 54.7% 58.3%, rgba(255,252,230,0.80), transparent),
        radial-gradient(circle 2px at 68.1% 67.9%, rgba(255,220,185,0.74), transparent),
        radial-gradient(circle 2px at 83.4% 74.2%, rgba(210,225,255,0.70), transparent),
        radial-gradient(circle 2px at 6.5% 82.6%, rgba(255,255,255,0.76), transparent),
        radial-gradient(circle 3px at 22.8% 88.4%, rgba(255,252,230,0.84), transparent),
        radial-gradient(circle 2px at 45.3% 79.1%, rgba(210,225,255,0.82), transparent),
        radial-gradient(circle 2px at 71.6% 85.8%, rgba(255,220,185,0.76), transparent),
        radial-gradient(circle 2px at 95.2% 92.3%, rgba(210,225,255,0.72), transparent) !important;
    background-attachment: fixed !important;
    background-size: 100% 100% !important;
    animation: wyhlLandingBg 32s ease-in-out infinite alternate;
}
body, #root, .stApp, [data-testid="stAppViewContainer"], .main {
    background: transparent !important;
}
@keyframes wyhlLandingBg {
    0%   { background-size: 100% 100%; }
    100% { background-size: 105% 105%; }
}
</style>
""")

    st.html("<br><br><br><br>")
    st.html("<h1 style='text-align:center; font-size:clamp(1.8rem,7vw,3.5rem); letter-spacing:clamp(0.08em,1.5vw,0.25em); color:#FF4444; opacity:0; animation: fadeInUp 1.2s ease 0.1s forwards, glowPulse 4s ease 2s infinite;'>WHAT HAVE YOU LOST</h1>")
    st.html("<p style='text-align:center; font-size:clamp(0.6rem,2vw,0.8rem); letter-spacing:clamp(0.12em,1vw,0.3em); color:#6666AA; opacity:0; animation: fadeInUp 1s ease 0.55s forwards;'>A LIGHT POLLUTION OBSERVATORY</p>")

    st.html("""
<p style='text-align:center; max-width:600px; margin:0 auto; font-size:1.05rem; line-height:2.2; color:#8899BB; letter-spacing:0.02em; opacity:0; animation: fadeInUp 1s ease 0.95s forwards;'>
Every year, artificial light drowns out more of the night sky. Stars that your grandparents could name from memory have silently vanished — not from the universe, but from your view.
</p>
""")

    st.html("<br>")

    st.html("""
<p style='text-align:center; max-width:600px; margin:0 auto; font-size:0.9rem; line-height:2.1; color:#667799; letter-spacing:0.01em; opacity:0; animation: fadeInUp 1s ease 1.25s forwards;'>
Light pollution is the only form of pollution that erases something from human experience entirely. A child growing up in New York City today has never seen the Milky Way. Most have never seen more than a handful of stars at all. What was once an unbroken human inheritance — a canopy of thousands of points of light overhead on any clear night — has been quietly switched off over the course of a single lifetime.
</p>
""")

    st.html("<br><br>")

    st.html("""
<div class='wyhl-grid-3' style='gap:2px; max-width:680px; margin:0 auto;'>
  <div style='background:rgba(10,10,24,0.7); border:1px solid #111133; padding:2rem 1rem; text-align:center; backdrop-filter:blur(4px); opacity:0; animation: fadeInUp 0.8s ease 1.55s forwards;'>
    <div style='font-size:2.2rem; font-weight:300; color:white; font-family:"Space Grotesk",sans-serif;'>10+</div>
    <div style='font-size:0.65rem; letter-spacing:0.15em; color:#444466; margin-top:0.5rem;'>YEARS OF DATA</div>
  </div>
  <div style='background:rgba(10,10,24,0.7); border:1px solid #111133; padding:2rem 1rem; text-align:center; backdrop-filter:blur(4px); opacity:0; animation: fadeInUp 0.8s ease 1.75s forwards;'>
    <div style='font-size:2.2rem; font-weight:300; color:white; font-family:"Space Grotesk",sans-serif;'>~30K</div>
    <div style='font-size:0.65rem; letter-spacing:0.15em; color:#444466; margin-top:0.5rem;'>US ZIP CODES</div>
  </div>
  <div style='background:rgba(10,10,24,0.7); border:1px solid #111133; padding:2rem 1rem; text-align:center; backdrop-filter:blur(4px); opacity:0; animation: fadeInUp 0.8s ease 1.95s forwards;'>
    <div style='font-size:2.2rem; font-weight:300; color:#FF4444; font-family:"Space Grotesk",sans-serif;'>↑ 15%</div>
    <div style='font-size:0.65rem; letter-spacing:0.15em; color:#444466; margin-top:0.5rem;'>AVG SKY GLOW SINCE 2012</div>
  </div>
</div>
""")

    st.html("<br><br><br>")

    st.html("""
<p style='text-align:center; max-width:580px; margin:0 auto; font-size:0.9rem; line-height:2.1; color:#556688; opacity:0; animation: fadeInUp 1s ease 0.25s forwards;'>
This tool uses NASA Black Marble satellite data to translate raw light radiance into something human — the actual named stars you can no longer see from your backyard, mapped year by year since 2012. Enter your zip code and watch stars wink out as the years advance. Tap any star to learn its story.
</p>
""")

    st.html("<br><br>")

    st.html("""
<p style='text-align:center; font-size:0.58rem; letter-spacing:0.22em; color:#334455; margin:0 0 1.5rem 0; opacity:0; animation: fadeInUp 0.8s ease 0.1s forwards;'>A BRIEF HISTORY OF ARTIFICIAL NIGHT</p>
<div style='max-width:680px; margin:0 auto; position:relative;'>
  <div style='position:absolute; left:80px; top:0; bottom:0; width:1px; background:#111133;'></div>
  <div style='display:flex; flex-direction:column; gap:0;'>

    <div class='wyhl-tl-entry' style='display:flex; gap:0; align-items:flex-start; padding:0.6rem 0;'>
      <div style='min-width:80px; font-size:0.65rem; letter-spacing:0.1em; color:#334455; padding-top:0.1rem; text-align:right; padding-right:1.2rem;'>1879</div>
      <div style='width:7px; height:7px; border-radius:50%; background:#222244; border:1px solid #334466; flex-shrink:0; margin-top:0.22rem; margin-right:1.2rem;'></div>
      <div style='font-size:0.8rem; line-height:1.8; color:#556688;'>Thomas Edison demonstrates the first practical incandescent bulb. Electric street lighting begins spreading from city centres outward.</div>
    </div>

    <div class='wyhl-tl-entry' style='display:flex; gap:0; align-items:flex-start; padding:0.6rem 0;'>
      <div style='min-width:80px; font-size:0.65rem; letter-spacing:0.1em; color:#334455; padding-top:0.1rem; text-align:right; padding-right:1.2rem;'>1930s</div>
      <div style='width:7px; height:7px; border-radius:50%; background:#222244; border:1px solid #334466; flex-shrink:0; margin-top:0.22rem; margin-right:1.2rem;'></div>
      <div style='font-size:0.8rem; line-height:1.8; color:#556688;'>The Milky Way disappears from the skies above every major American and European city. Observatories begin relocating away from urban centres.</div>
    </div>

    <div class='wyhl-tl-entry' style='display:flex; gap:0; align-items:flex-start; padding:0.6rem 0;'>
      <div style='min-width:80px; font-size:0.65rem; letter-spacing:0.1em; color:#334455; padding-top:0.1rem; text-align:right; padding-right:1.2rem;'>1950s–70s</div>
      <div style='width:7px; height:7px; border-radius:50%; background:#222244; border:1px solid #334466; flex-shrink:0; margin-top:0.22rem; margin-right:1.2rem;'></div>
      <div style='font-size:0.8rem; line-height:1.8; color:#556688;'>Post-war suburban expansion and the interstate highway system blanket the continental US in roadway lighting. The dark sky retreats hundreds of miles from major cities.</div>
    </div>

    <div class='wyhl-tl-entry' style='display:flex; gap:0; align-items:flex-start; padding:0.6rem 0;'>
      <div style='min-width:80px; font-size:0.65rem; letter-spacing:0.1em; color:#334455; padding-top:0.1rem; text-align:right; padding-right:1.2rem;'>1994</div>
      <div style='width:7px; height:7px; border-radius:50%; background:#333355; border:1px solid #445577; flex-shrink:0; margin-top:0.22rem; margin-right:1.2rem;'></div>
      <div style='font-size:0.8rem; line-height:1.8; color:#556688;'>After the Northridge earthquake cuts power to Los Angeles, thousands of residents call 911 to report a strange silvery cloud overhead. They had seen the Milky Way for the first time in their lives.</div>
    </div>

    <div class='wyhl-tl-entry' style='display:flex; gap:0; align-items:flex-start; padding:0.6rem 0;'>
      <div style='min-width:80px; font-size:0.65rem; letter-spacing:0.1em; color:#334455; padding-top:0.1rem; text-align:right; padding-right:1.2rem;'>2001</div>
      <div style='width:7px; height:7px; border-radius:50%; background:#222244; border:1px solid #334466; flex-shrink:0; margin-top:0.22rem; margin-right:1.2rem;'></div>
      <div style='font-size:0.8rem; line-height:1.8; color:#556688;'>Scientists estimate one-third of humanity can no longer see the Milky Way at all. The figure is already higher in the United States and Europe.</div>
    </div>

    <div class='wyhl-tl-entry' style='display:flex; gap:0; align-items:flex-start; padding:0.6rem 0;'>
      <div style='min-width:80px; font-size:0.65rem; letter-spacing:0.1em; color:#334455; padding-top:0.1rem; text-align:right; padding-right:1.2rem;'>2016</div>
      <div style='width:7px; height:7px; border-radius:50%; background:#222244; border:1px solid #334466; flex-shrink:0; margin-top:0.22rem; margin-right:1.2rem;'></div>
      <div style='font-size:0.8rem; line-height:1.8; color:#556688;'>The <em>World Atlas of Artificial Night Sky Brightness</em> reveals 99% of Americans and Europeans live under light-polluted skies. 83% of the global population — and one-third of humanity — has never seen a truly dark night sky.</div>
    </div>

    <div class='wyhl-tl-entry' style='display:flex; gap:0; align-items:flex-start; padding:0.6rem 0;'>
      <div style='min-width:80px; font-size:0.65rem; letter-spacing:0.1em; color:#334455; padding-top:0.1rem; text-align:right; padding-right:1.2rem;'>2012–23</div>
      <div style='width:7px; height:7px; border-radius:50%; background:#333355; border:1px solid #445577; flex-shrink:0; margin-top:0.22rem; margin-right:1.2rem;'></div>
      <div style='font-size:0.8rem; line-height:1.8; color:#556688;'>LED adoption accelerates globally. Although individual LEDs are more efficient, the rebound effect means far more lights are installed. Total light pollution rises more than 10% per year across the US.</div>
    </div>

    <div class='wyhl-tl-entry' style='display:flex; gap:0; align-items:flex-start; padding:0.6rem 0;'>
      <div style='min-width:80px; font-size:0.65rem; letter-spacing:0.1em; color:#FF444455; padding-top:0.1rem; text-align:right; padding-right:1.2rem;'>2023</div>
      <div style='width:7px; height:7px; border-radius:50%; background:#442233; border:1px solid #FF4444; flex-shrink:0; margin-top:0.22rem; margin-right:1.2rem;'></div>
      <div style='font-size:0.8rem; line-height:1.8; color:#667788;'>A study in <em>Science</em> finds that the number of stars visible to the naked eye is decreasing by 9.6% per year — fast enough to halve the visible sky within a human generation.</div>
    </div>

  </div>
</div>
""")
    inject_js("""
  var obs = new IntersectionObserver(function(entries) {
    entries.forEach(function(e) {
      if (e.isIntersecting) {
        e.target.classList.add('visible');
        obs.unobserve(e.target);
      }
    });
  }, {threshold: 0.15});
  document.querySelectorAll('.wyhl-tl-entry').forEach(function(el) { obs.observe(el); });
""")

    st.html("<br><br>")

    st.html("""
<div class='wyhl-grid-2' style='max-width:680px;'>
  <div style='background:rgba(8,8,20,0.7); border:1px solid #0e0e2a; border-left:2px solid #2a3a6a; padding:1.2rem 1.5rem; backdrop-filter:blur(4px);'>
    <p style='font-size:0.58rem; letter-spacing:0.18em; color:#334455; margin:0 0 0.4rem 0;'>THE SCIENCE</p>
    <p style='font-size:0.82rem; line-height:1.9; color:#667799; margin:0;'>Satellite sensors aboard the Suomi-NPP spacecraft measure upward radiance at night. We convert that radiance into a limiting magnitude — the faintest star your eye can detect — and then cross-reference a catalog of 69 named objects to show you exactly what has been lost.</p>
  </div>
  <div style='background:rgba(8,8,20,0.7); border:1px solid #0e0e2a; border-left:2px solid #2a3a6a; padding:1.2rem 1.5rem; backdrop-filter:blur(4px);'>
    <p style='font-size:0.58rem; letter-spacing:0.18em; color:#334455; margin:0 0 0.4rem 0;'>WHY IT MATTERS</p>
    <p style='font-size:0.82rem; line-height:1.9; color:#667799; margin:0;'>99% of Americans live under light-polluted skies. Beyond the human cost, artificial light disrupts nocturnal ecosystems, confuses bird migration, and suppresses melatonin in ways that affect human health. The night sky is not a luxury — it is a commons, and it is being privatized by default.</p>
  </div>
</div>
""")

    st.html("<br><br><br>")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("EXPLORE YOUR SKY  →", use_container_width=True):
            st.session_state.page = "finder"
            st.query_params["page"] = "finder"
            st.rerun()

    st.html("<br>")
    st.html("<p style='text-align:center; font-size:0.65rem; letter-spacing:0.1em; color:#333355;'>ENTER YOUR ZIP CODE TO BEGIN</p>")
    st.html("<br><br><br>")
    st.html("<hr>")
    st.html("<br>")
    st.html("<p style='text-align:center; letter-spacing:0.15em; font-size:0.65rem; color:#444466;'>WHY DOES THE DATA STOP AT 2023?</p>")
    st.html("<br>")
    st.html("""
<p style='text-align:center; max-width:560px; margin:0 auto; font-size:0.8rem; line-height:2; color:#445566;'>
This tool is built on NASA's Black Marble VNP46A4 dataset — annual composites of nighttime light radiance captured by the VIIRS sensor aboard the Suomi-NPP satellite. 2023 is the most recent complete annual composite currently released by NASA. As new years are published, the data here can be updated to match.
</p>
""")
    st.html("<br><br>")
    st.html("<p style='text-align:center; font-size:0.65rem; letter-spacing:0.1em; color:#334455;'>NASA BLACK MARBLE VNP46A4  ·  BACKGROUND: NASA/GALEX M31</p>")
    st.html("<br><br>")
    st.stop()

# ── Zip code finder ───────────────────────────────────────────────────────────
if st.session_state.page == "finder":
    st.html("""<style>
html{background:#03030a!important;}
body,#root,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMainBlockContainer"],.main,.block-container,section.main{background:transparent!important;background-image:none!important;}
</style>""")
    canvas_bg("""
  var skyS = [];
  for (var i=0;i<110;i++) skyS.push({x:Math.random(),y:Math.random()*0.5,r:0.3+Math.random()*0.8,a:0.05+Math.random()*0.17,tw:Math.random()*6.28,twr:0.004+Math.random()*0.01});
  var cityL = [];
  for (var i=0;i<38;i++) {
    var led=Math.random()<0.25;
    cityL.push({x:Math.random(),y:0.52+Math.random()*0.48,r:0.018+Math.random()*0.055,ph:Math.random()*6.28,rate:0.002+Math.random()*0.005,
      rgb:led?'200,215,235':(Math.random()<0.5?'255,200,90':'248,172,58')});
  }
  var sat={t:-0.2,spd:0.00038}, shooters=[], shootCd=350+Math.random()*450, frame=0, lastT=0, FRATE=1000/42;

  function draw(t) {
    requestAnimationFrame(draw);
    if (t-lastT<FRATE) return;
    lastT=t; frame++;
    ctx.fillStyle='#03030a'; ctx.fillRect(0,0,W,H);

    var sky=ctx.createLinearGradient(0,0,0,H);
    sky.addColorStop(0,'rgba(3,3,10,1)'); sky.addColorStop(0.4,'rgba(5,4,12,1)');
    sky.addColorStop(0.62,'rgba(10,7,5,1)'); sky.addColorStop(0.8,'rgba(18,11,4,1)');
    sky.addColorStop(1,'rgba(28,15,5,1)');
    ctx.fillStyle=sky; ctx.fillRect(0,0,W,H);

    var pulse=0.5+0.5*Math.sin(frame*0.006);
    var dome=ctx.createRadialGradient(W*0.5,H*1.15,0,W*0.5,H*1.15,H*0.95);
    dome.addColorStop(0,'rgba(210,115,30,'+(0.20+pulse*0.05)+')');
    dome.addColorStop(0.4,'rgba(175,85,18,'+(0.09+pulse*0.02)+')');
    dome.addColorStop(0.75,'rgba(140,60,10,0.03)');
    dome.addColorStop(1,'rgba(140,60,10,0)');
    ctx.fillStyle=dome; ctx.fillRect(0,0,W,H);

    [[W*0.2,H*1.05,H*0.55,'255,200,60',0.07+pulse*0.015],[W*0.75,H*1.0,H*0.45,'230,150,40',0.06+pulse*0.01]].forEach(function(d){
      var g=ctx.createRadialGradient(d[0],d[1],0,d[0],d[1],d[2]);
      g.addColorStop(0,'rgba('+d[3]+','+d[4]+')'); g.addColorStop(1,'rgba('+d[3]+',0)');
      ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
    });

    for (var i=0;i<skyS.length;i++) {
      var s=skyS[i]; s.tw+=s.twr;
      var a=s.a*(0.5+0.5*Math.sin(s.tw))*Math.max(0,1-s.y*1.8);
      if(a<0.01) continue;
      ctx.beginPath(); ctx.arc(s.x*W,s.y*H,s.r,0,6.28);
      ctx.fillStyle='rgba(210,220,255,'+a+')'; ctx.fill();
    }

    for (var j=0;j<cityL.length;j++) {
      var l=cityL[j]; l.ph+=l.rate;
      var la=0.05+0.025*Math.sin(l.ph), lr=l.r*Math.min(W,H), lx=l.x*W, ly=l.y*H;
      var halo=ctx.createRadialGradient(lx,ly,0,lx,ly,lr);
      halo.addColorStop(0,'rgba('+l.rgb+','+(la*4)+')');
      halo.addColorStop(0.3,'rgba('+l.rgb+','+(la*1.8)+')');
      halo.addColorStop(1,'rgba('+l.rgb+',0)');
      ctx.fillStyle=halo; ctx.fillRect(lx-lr,ly-lr,lr*2,lr*2);
      ctx.beginPath(); ctx.arc(lx,ly,1.0,0,6.28);
      ctx.fillStyle='rgba('+l.rgb+','+Math.min(1,la*8)+')'; ctx.fill();
    }

    sat.t+=sat.spd;
    if (sat.t>1.25) sat.t=-0.25;
    var sx=sat.t*W*1.4-W*0.1, sy=H*(0.1+0.09*Math.sin(sat.t*Math.PI));
    var sa=Math.min(1,Math.max(0,Math.min((sat.t+0.25)*4,(1.25-sat.t)*4)));
    if (sa>0.02) {
      ctx.save(); ctx.globalAlpha=sa*0.65;
      ctx.fillStyle='rgba(200,225,255,1)'; ctx.beginPath(); ctx.arc(sx,sy,1.5,0,6.28); ctx.fill();
      ctx.strokeStyle='rgba(180,210,255,1)'; ctx.lineWidth=0.7;
      ctx.beginPath(); ctx.moveTo(sx-5,sy); ctx.lineTo(sx+5,sy); ctx.stroke();
      ctx.restore();
    }

    if (--shootCd<=0) {
      shooters.push({x:Math.random()*W*0.7,y:-4+Math.random()*H*0.28,vx:5+Math.random()*8,vy:2+Math.random()*4,life:1,mLen:38+Math.random()*48});
      shootCd=380+Math.random()*520;
    }
    shooters=shooters.filter(function(sh){return sh.life>0.01;});
    for (var shi=0;shi<shooters.length;shi++) {
      var sh=shooters[shi], spd=Math.hypot(sh.vx,sh.vy);
      var tx=sh.x-sh.vx/spd*sh.mLen, ty=sh.y-sh.vy/spd*sh.mLen;
      var sg=ctx.createLinearGradient(tx,ty,sh.x,sh.y);
      sg.addColorStop(0,'rgba(200,215,255,0)'); sg.addColorStop(1,'rgba(220,232,255,'+(sh.life*0.5)+')');
      ctx.beginPath(); ctx.moveTo(tx,ty); ctx.lineTo(sh.x,sh.y);
      ctx.strokeStyle=sg; ctx.lineWidth=1.1; ctx.stroke();
      sh.x+=sh.vx; sh.y+=sh.vy; sh.life-=0.032;
      if (sh.x>W+100||sh.y>H+100) sh.life=0;
    }
  }
  requestAnimationFrame(draw);
""")

if st.session_state.page != "stars":
    st.html("<br><br>")
    st.html("<h1 style='text-align:center; font-size:clamp(1.6rem,6vw,3rem); letter-spacing:clamp(0.06em,1.2vw,0.2em); color:#FF4444;'>WHAT HAVE YOU LOST</h1>")
    st.html("<p style='text-align:center; font-size:clamp(0.8rem,2.5vw,1rem); letter-spacing:0.05em; color:#555577;'>enter your zip code to see which stars have disappeared from your sky since 2012</p>")
    st.html("<br><br>")

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
                st.html("<p style='text-align:center; color:#442222;'>zip code not found</p>")

    st.html("<br>")

if st.session_state.searched and st.session_state.page != "stars":
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

    st.html(f"<p style='text-align:center; letter-spacing:0.15em; font-size:0.75rem; color:#444466;'>ZIP CODE {zipcode}</p>")
    st.html(f"<p style='text-align:center; font-size:0.85rem; color:#7788AA; margin-top:-8px;'>{st.session_state.place_name}</p>")
    st.html("<br>")

    poll_tip = ("Percentage change in upward light radiance measured by NASA Black Marble satellite "
                "between 2012 and 2023. Positive = more light pollution; negative = improvement.")
    vis_tip = ("Named stars and deep-sky objects from our 69-object catalog bright enough to be seen "
               "with the naked eye from your location under 2023 sky conditions.")
    if pct_change >= 0:
        star_label = "stars lost since 2012"
        star_value = str(len(all_lost))
        star_tip = ("Named stars from our 69-object catalog that were visible to the naked eye in 2012 "
                    "but can no longer be seen due to increased light pollution.")
    else:
        gained = [(n, m) for n, m in star_mags if lm_2012 < m <= lm_2023]
        star_label = "stars gained since 2012"
        star_value = str(len(gained))
        star_tip = ("Named stars from our 69-object catalog that were not visible in 2012 but have "
                    "become visible due to reduced light pollution.")
    st.html(metrics_row([
        metric_card("light pollution since 2012", f"{pct_change:+.1f}%", poll_tip),
        metric_card(star_label, star_value, star_tip),
        metric_card("visible in our atlas", str(len(still_visible)), vis_tip),
    ], 3))

    # Sky quality + change explanation cards
    sky_label_now, sky_bortle_now, sky_stars_now, sky_exp_now = get_sky_description(lm_2023)
    change_headline, change_text = get_change_reason(pct_change)
    sky_color_map = {
        "Inner City": "#FF4444", "City Sky": "#FF9943",
        "Urban Fringe": "#FECA57", "Suburban": "#48DBFB", "Bright Suburban": "#2ED573",
    }
    sky_color_now = sky_color_map.get(sky_label_now, "#8899BB")

    st.html("<br>")
    st.html(f"""
<div class='wyhl-grid-2'>
  <div style='background:#080818; border:1px solid #111133; border-left:2px solid {sky_color_now}; padding:1.4rem 1.5rem;'>
    <p style='font-size:0.58rem; letter-spacing:0.18em; color:#334455; margin:0 0 0.45rem 0;'>WHAT YOUR SKY LOOKS LIKE</p>
    <p style='font-size:1.05rem; color:{sky_color_now}; font-family:"Space Grotesk",sans-serif; font-weight:300; margin:0 0 0.2rem 0;'>{sky_label_now}</p>
    <p style='font-size:0.62rem; letter-spacing:0.08em; color:#334466; margin:0 0 0.9rem 0;'>{sky_bortle_now} &nbsp;·&nbsp; ~{sky_stars_now} total naked-eye stars across full sky</p>
    <p style='font-size:0.8rem; line-height:1.9; color:#7788AA; margin:0;'>{sky_exp_now}</p>
  </div>
  <div style='background:#080818; border:1px solid #111133; border-left:2px solid #2a3a6a; padding:1.4rem 1.5rem;'>
    <p style='font-size:0.58rem; letter-spacing:0.18em; color:#334455; margin:0 0 0.45rem 0;'>WHY YOUR VISIBILITY CHANGED</p>
    <p style='font-size:1.05rem; color:#8899BB; font-family:"Space Grotesk",sans-serif; font-weight:300; margin:0 0 0.9rem 0;'>{change_headline}</p>
    <p style='font-size:0.8rem; line-height:1.9; color:#7788AA; margin:0;'>{change_text}</p>
  </div>
</div>
""")

    st.html("<br><br>")
    st.html("<p style='text-align:center; letter-spacing:0.1em; font-size:0.7rem; color:#334466;'>DRAG TO TRAVEL THROUGH TIME</p>")

    year = st.slider("", min_value=2012, max_value=2023, value=2012,
                      label_visibility="collapsed")

    fig, lost_on_chart, visible_count, rad_now_chart = make_sky_chart(
        STARS, year, radiance_by_year, color_map, lat, lon, CONSTELLATION_LINES)

    st.html(f"<p style='text-align:center; font-size:2rem; font-family:\"Space Grotesk\",sans-serif; "
                f"font-weight:300; color:white; letter-spacing:0.15em; margin:0 0 0.2rem 0;'>{year}</p>")

    _chart_key = f"star_chart_{st.session_state.get('_star_chart_ver', 0)}"
    event_data = st.plotly_chart(fig, on_select="rerun", key=_chart_key)
    if event_data.selection.points:
        pt = event_data.selection.points[0]
        raw = pt.get("customdata")
        if raw is not None:
            while isinstance(raw, (list, tuple)) and len(raw) == 1:
                raw = raw[0]
            star_name = str(raw) if not isinstance(raw, str) else raw
            if star_name and any(s[0] == star_name for s in STARS):
                st.session_state["star_search_input"] = star_name
                st.session_state.page = "stars"
                st.session_state["_star_chart_ver"] = st.session_state.get("_star_chart_ver", 0) + 1
                st.query_params["page"] = "stars"
                st.rerun()

    st.html(
        f"<p style='text-align:center; font-size:0.68rem; color:#334455; margin:0.3rem 0 0;'>"
        f"● <span style='color:#8899BB;'>visible</span> &nbsp;&nbsp; "
        f"★ <span style='color:#CC6666;'>lost since 2012</span> &nbsp;&nbsp;&nbsp; "
        f"<span style='color:#334455;'>{rad_now_chart:.1f} nW/cm²/sr · {visible_count} visible</span>"
        f"</p>"
    )

    st.html("<p style='text-align:center; font-size:0.7rem; color:#334455; margin-top:0.5rem;'>face south · center is straight up · stars near the edge sit low on the horizon</p>")

    lm_year = radiance_to_limiting_magnitude(radiance_by_year[year])
    sky_label_yr, sky_bortle_yr, sky_stars_yr, sky_exp_yr = get_sky_description(lm_year)
    sky_color_yr = sky_color_map.get(sky_label_yr, "#8899BB")
    st.html(f"""
<div style='text-align:center; margin:1.2rem auto 0.2rem; padding:1rem 1.5rem;
     background:#080818; border:1px solid #0e0e2a; max-width:600px; border-radius:2px;'>
  <p style='font-size:0.58rem; letter-spacing:0.18em; color:#334455; margin:0 0 0.3rem 0;'>IN {year} YOUR SKY WAS</p>
  <p style='font-size:0.9rem; color:{sky_color_yr}; font-family:"Space Grotesk",sans-serif; font-weight:300; margin:0 0 0.2rem 0;'>{sky_label_yr}</p>
  <p style='font-size:0.62rem; color:#334466; margin:0 0 0.6rem 0;'>{sky_bortle_yr} · ~{sky_stars_yr} total naked-eye stars across full sky</p>
  <p style='font-size:0.78rem; line-height:1.85; color:#556677; margin:0; text-align:left;'>{sky_exp_yr}</p>
</div>
""")
    all_lost_for_year = sorted(
        [(n, m) for n, m in star_mags if lm_year < m <= lm_2012],
        key=lambda x: x[1]
    )
    on_chart_names = {name for name, _ in lost_on_chart}

    if all_lost_for_year:
        st.html("<br>")
        st.html(f"<p style='letter-spacing:0.15em; font-size:0.7rem; color:#333355;'>LOST FROM YOUR SKY BY {year} — tap a name to learn more</p>")
        st.html("<br>")
        html = "<div class='wyhl-grid-3'>"
        for name, mag in all_lost_for_year:
            color = color_map.get((name, mag), "#FF4444")
            encoded = name.replace(" ", "%20")
            if name in on_chart_names:
                html += (f"<div><a href='?page=stars&star={encoded}' target='_self' "
                         f"style='color:{color}; font-size:0.85rem; text-decoration:none;'>★ {name}</a></div>")
            else:
                html += (f"<div style='opacity:0.45;'><a href='?page=stars&star={encoded}' target='_self' "
                         f"style='color:{color}; font-size:0.85rem; text-decoration:none;'>★ {name} "
                         f"<span style='font-size:0.65rem; letter-spacing:0.05em;'>below horizon</span></a></div>")
        html += "</div>"
        st.html(html)

    st.html("<br>")

    travel_hint = {
        "Inner City":       "typically 50+ miles",
        "City Sky":         "typically 35–50 miles",
        "Urban Fringe":     "typically 20–35 miles",
        "Suburban":         "typically 15–25 miles",
        "Bright Suburban":  "typically 10–20 miles",
    }
    hint = travel_hint.get(sky_label_now, "typically 20–50 miles")
    _pn = st.session_state.place_name
    city_short = _pn.split(",")[0] if _pn else "your location"
    map_url = f"https://www.lightpollutionmap.info/#zoom=9&lat={lat:.4f}&lng={lon:.4f}"
    ida_url = "https://www.darksky.org/our-work/conservation/idsp/finder/"

    st.html(f"""
<div style='max-width:680px; margin:1.5rem auto 0; border-top:1px solid #111133; padding-top:2rem;'>
  <p style='font-size:0.58rem; letter-spacing:0.22em; color:#334455; margin:0 0 0.8rem 0;'>FIND DARK SKIES NEAR YOU</p>
  <p style='font-size:0.82rem; line-height:1.9; color:#667799; margin:0 0 1.2rem 0;'>
    The stars haven't gone anywhere — they're just drowned out from {city_short}.
    From here, you'll need to travel {hint} to reach skies dark enough for the Milky Way to reappear.
    Use the tools below to find the nearest dark patches and plan a night out.
  </p>
  <div class='wyhl-grid-2' style='max-width:100%;'>
    <a href='{map_url}' target='_blank' style='display:block; background:rgba(8,8,20,0.7);
       border:1px solid #0e0e2a; border-left:2px solid #2a3a6a; padding:1rem 1.25rem;
       text-decoration:none; backdrop-filter:blur(4px);'>
      <p style='font-size:0.58rem; letter-spacing:0.18em; color:#334455; margin:0 0 0.3rem 0;'>LIGHT POLLUTION MAP</p>
      <p style='font-size:0.82rem; color:#667799; margin:0;'>Interactive satellite radiance map centered on {city_short} — darker patches nearby are your targets. →</p>
    </a>
    <a href='{ida_url}' target='_blank' style='display:block; background:rgba(8,8,20,0.7);
       border:1px solid #0e0e2a; border-left:2px solid #2a3a6a; padding:1rem 1.25rem;
       text-decoration:none; backdrop-filter:blur(4px);'>
      <p style='font-size:0.58rem; letter-spacing:0.18em; color:#334455; margin:0 0 0.3rem 0;'>IDA DARK SKY PLACES</p>
      <p style='font-size:0.82rem; color:#667799; margin:0;'>Official International Dark-Sky Association registry of parks, reserves, and sanctuaries near you. →</p>
    </a>
  </div>
</div>
""")

    st.html("<br><br>")
    st.html("<p style='text-align:center; font-size:0.65rem; letter-spacing:0.1em; color:#445566;'>NASA BLACK MARBLE VNP46A4</p>")

# ── Stars page ────────────────────────────────────────────────────────────────
if st.session_state.page == "stars":
    st.html("""<style>
html{background:#03030a!important;}
body,#root,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMainBlockContainer"],.main,.block-container,section.main{background:transparent!important;background-image:none!important;}
</style>""")
    _sd = []; _si = {}; _li = []
    for _i, (_n, _m, _ra, _dec) in enumerate(STARS):
        _info = STAR_INFO.get(_n, {})
        _col = temp_to_star_color(_info.get('temp_k', 6000)).lstrip('#')
        _r, _g, _b = int(_col[0:2], 16), int(_col[2:4], 16), int(_col[4:6], 16)
        _sd.append(f"[{_ra:.4f},{_dec:.4f},{_m:.2f},'{_r},{_g},{_b}']")
        _si[_n] = _i
    for _n1, _n2 in CONSTELLATION_LINES:
        if _n1 in _si and _n2 in _si:
            _li.append(f"[{_si[_n1]},{_si[_n2]}]")
    canvas_bg(f"""
  var SD=[{','.join(_sd)}];
  var LD=[{','.join(_li)}];
  var tw = SD.map(function() {{ return {{ ph:Math.random()*6.28, rate:0.005+Math.random()*0.012 }}; }});
  var bgS = [];
  for (var i=0;i<180;i++) bgS.push({{ra:Math.random()*24,dec:-40+Math.random()*130,r:0.2+Math.random()*0.5,a:0.03+Math.random()*0.1,tw:Math.random()*6.28,twr:0.003+Math.random()*0.007}});
  var raOff=0, RA_DRIFT=0.00014, nebT=0, shooters=[], shootCd=280+Math.random()*420, frame=0, lastT=0, FRATE=1000/42;

  function proj(ra, dec) {{
    var x=((ra+raOff)%24+24)%24/24*W;
    var y=H*0.5-dec/90*H*0.44;
    return [x, y];
  }}

  function draw(t) {{
    requestAnimationFrame(draw);
    if (t-lastT<FRATE) return;
    lastT=t; frame++; raOff+=RA_DRIFT; nebT+=0.0003;
    ctx.fillStyle='#03030a'; ctx.fillRect(0,0,W,H);

    var mwShimmer=0.09+0.025*Math.sin(nebT*2.1)+0.015*Math.sin(nebT*5.7);
    ctx.save();
    ctx.translate(W*0.5,H*0.5); ctx.rotate(-0.32);
    var mw=ctx.createLinearGradient(0,-H*0.18,0,H*0.18);
    mw.addColorStop(0,'rgba(65,78,120,0)');
    mw.addColorStop(0.35,'rgba(72,86,135,'+mwShimmer*0.65+')');
    mw.addColorStop(0.5,'rgba(82,98,155,'+mwShimmer+')');
    mw.addColorStop(0.65,'rgba(72,86,135,'+mwShimmer*0.65+')');
    mw.addColorStop(1,'rgba(65,78,120,0)');
    ctx.fillStyle=mw; ctx.fillRect(-W,-H,W*2,H*2);
    ctx.restore();

    var nb1a=0.06+0.025*Math.sin(nebT*1.4), nb2a=0.05+0.02*Math.sin(nebT*1.9+1.2);
    var nb1=ctx.createRadialGradient(W*0.72,H*0.32,0,W*0.72,H*0.32,W*0.28);
    nb1.addColorStop(0,'rgba(95,18,130,'+nb1a+')'); nb1.addColorStop(1,'rgba(95,18,130,0)');
    ctx.fillStyle=nb1; ctx.fillRect(0,0,W,H);
    var nb2=ctx.createRadialGradient(W*0.22,H*0.62,0,W*0.22,H*0.62,W*0.24);
    nb2.addColorStop(0,'rgba(18,38,160,'+nb2a+')'); nb2.addColorStop(1,'rgba(18,38,160,0)');
    ctx.fillStyle=nb2; ctx.fillRect(0,0,W,H);

    for (var bi=0;bi<bgS.length;bi++) {{
      var b=bgS[bi]; b.tw+=b.twr;
      var bp=proj(b.ra,b.dec);
      if(bp[0]<-2||bp[0]>W+2||bp[1]<-2||bp[1]>H+2) continue;
      ctx.beginPath(); ctx.arc(bp[0],bp[1],b.r,0,6.28);
      ctx.fillStyle='rgba(180,195,220,'+(b.a*(0.6+0.4*Math.sin(b.tw)))+')';
      ctx.fill();
    }}

    for (var li=0;li<LD.length;li++) {{
      var s1=SD[LD[li][0]],s2=SD[LD[li][1]];
      var p1=proj(s1[0],s1[1]),p2=proj(s2[0],s2[1]);
      if(Math.abs(p1[0]-p2[0])>W*0.5) continue;
      var cg=ctx.createLinearGradient(p1[0],p1[1],p2[0],p2[1]);
      cg.addColorStop(0,'rgba(80,110,200,0.12)');
      cg.addColorStop(0.5,'rgba(105,135,225,0.24)');
      cg.addColorStop(1,'rgba(80,110,200,0.12)');
      ctx.strokeStyle=cg; ctx.lineWidth=0.65;
      ctx.beginPath(); ctx.moveTo(p1[0],p1[1]); ctx.lineTo(p2[0],p2[1]); ctx.stroke();
    }}

    for (var i=0;i<SD.length;i++) {{
      var s=SD[i], p=proj(s[0],s[1]);
      if(p[0]<-20||p[0]>W+20||p[1]<-10||p[1]>H+10) continue;
      tw[i].ph+=tw[i].rate;
      var mag=s[2], radius=Math.max(0.5,2.8-mag*0.52);
      var baseA=Math.max(0.12,0.95-mag*0.17);
      var alpha=baseA*(0.78+0.22*Math.sin(tw[i].ph));
      var rgb=s[3];
      if (mag<2.2) {{
        var gr=radius*(mag<1?5.5:3.8);
        var gg=ctx.createRadialGradient(p[0],p[1],0,p[0],p[1],gr);
        gg.addColorStop(0,'rgba('+rgb+','+(alpha*0.24)+')');
        gg.addColorStop(1,'rgba('+rgb+',0)');
        ctx.fillStyle=gg; ctx.fillRect(p[0]-gr,p[1]-gr,gr*2,gr*2);
      }}
      ctx.beginPath(); ctx.arc(p[0],p[1],radius,0,6.28);
      ctx.fillStyle='rgba('+rgb+','+alpha+')'; ctx.fill();
    }}

    if (--shootCd<=0) {{
      shooters.push({{x:Math.random()*W*0.8,y:-4+Math.random()*H*0.4,vx:4+Math.random()*9,vy:2+Math.random()*5,life:1,mLen:55+Math.random()*70}});
      shootCd=300+Math.random()*460;
    }}
    shooters=shooters.filter(function(sh){{return sh.life>0.01;}});
    for (var shi=0;shi<shooters.length;shi++) {{
      var sh=shooters[shi], spd=Math.hypot(sh.vx,sh.vy);
      var tx=sh.x-sh.vx/spd*sh.mLen, ty=sh.y-sh.vy/spd*sh.mLen;
      var sg=ctx.createLinearGradient(tx,ty,sh.x,sh.y);
      sg.addColorStop(0,'rgba(200,215,255,0)'); sg.addColorStop(1,'rgba(220,232,255,'+(sh.life*0.75)+')');
      ctx.beginPath(); ctx.moveTo(tx,ty); ctx.lineTo(sh.x,sh.y);
      ctx.strokeStyle=sg; ctx.lineWidth=1.4; ctx.stroke();
      sh.x+=sh.vx; sh.y+=sh.vy; sh.life-=0.025;
      if (sh.x>W+100||sh.y>H+100) sh.life=0;
    }}
  }}
  requestAnimationFrame(draw);
""")
    st.html("<br><br>")
    st.html("<h1 style='text-align:center; font-size:clamp(1.4rem,5vw,2.5rem); letter-spacing:clamp(0.06em,1vw,0.18em);'>STAR ATLAS</h1>")
    st.html("<p style='text-align:center; font-size:0.72rem; letter-spacing:0.2em; color:#444466;'>SEARCH THE CATALOG — 69 OBJECTS</p>")
    st.html("<br><br>")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        query = st.text_input("", placeholder="try  Sirius · Vega · Betelgeuse · Orion Nebula",
                              label_visibility="collapsed", key="star_search_input")
        searched = st.button("SEARCH", use_container_width=True, key="star_search_btn")

    star_names_lower = {s[0].lower(): s for s in STARS}

    if query:
        matches = [s for s in STARS if query.lower() in s[0].lower()]

        if not matches:
            st.html("<p style='text-align:center; color:#442222; margin-top:2rem;'>no match found — try a different name</p>")
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

            star_color = temp_to_star_color(info["temp_k"]) if info.get("temp_k") else "#ffffff"
            st.html("<br>")
            st.html(
                f"<div style='text-align:center;'>"
                f"<span style='display:inline-block; width:20px; height:20px; border-radius:50%; "
                f"background:{star_color}; box-shadow:0 0 18px 6px {star_color}55; "
                f"vertical-align:middle; margin-right:14px; margin-bottom:4px;'></span>"
                f"<span style='font-family:\"Space Grotesk\",sans-serif; font-size:clamp(1.6rem,5vw,2.8rem); "
                f"letter-spacing:clamp(0.04em,0.8vw,0.12em); color:white; font-weight:300;'>{name}</span>"
                f"</div>")
            if info.get("constellation"):
                st.html(f"<p style='text-align:center; font-size:0.65rem; letter-spacing:0.2em; color:#445566; margin-top:0.3rem;'>{info['constellation'].upper()}</p>")
            st.html("<br>")

            row1 = [
                metric_card("Apparent Magnitude", f"{mag:.2f}",
                            "How bright the object appears from Earth. Lower (or more negative) numbers "
                            "are brighter. Each step of 1 magnitude is ~2.5x in brightness; a difference "
                            "of 5 is exactly 100x."),
                metric_card("Right Ascension", f"{ra:.3f} h",
                            "The celestial equivalent of longitude — how far east the object sits on the "
                            "celestial sphere, measured in hours (0-24 h)."),
                metric_card("Declination", f"{dec:+.2f}°",
                            "The celestial equivalent of latitude — how far north (+) or south (-) the "
                            "object sits from the celestial equator, in degrees (-90° to +90°)."),
            ]
            if info.get("distance_ly"):
                d = info["distance_ly"]
                dist_str = f"{d:,.0f} ly" if d >= 1000 else f"{d} ly"
                row1.append(metric_card("Distance", dist_str,
                                        "Approximate distance from Earth in light-years. One light-year is "
                                        "the distance light travels in a year — about 9.46 trillion km."))
            st.html(metrics_row(row1))

            if info.get("type"):
                st.html("<br>")
                row2 = [
                    metric_card("Classification", info["type"],
                                "Physical category based on the object's size, luminosity, evolutionary "
                                "stage, and spectral properties."),
                ]
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
                    place_upper = st.session_state.place_name.upper() if st.session_state.place_name else ""
                    row2.append(metric_card("Visibility", vis_label,
                                            "Whether this object is visible to the naked eye from your "
                                            "searched location based on 2023 light pollution data.",
                                            sublabel=place_upper,
                                            sublabel_color=vis_color,
                                            value_color=vis_color))
                st.html(metrics_row(row2, cols=3))

            if info.get("spectral"):
                st.html("<br>")
                row3 = [
                    metric_card("Spectral Class", info["spectral"],
                                "A letter code describing the star's temperature and chemistry. "
                                "O B A F G K M runs hottest (blue) to coolest (red). A Roman numeral "
                                "suffix indicates luminosity class (I = supergiant, V = main sequence). "
                                "Our Sun is G2V."),
                    metric_card("Surface Temperature", f"{info['temp_k']:,} K",
                                "Effective temperature of the star's photosphere — the layer from which "
                                "its light escapes. Hotter stars appear blue-white; cooler stars appear "
                                "orange-red."),
                ]
                lum = info.get("luminosity_sun")
                if lum is not None:
                    if lum >= 1000:
                        lum_str = f"{lum:,.0f}× ☉"
                    elif lum >= 1:
                        lum_str = f"{lum:.2f}× ☉"
                    else:
                        lum_str = f"{lum:.3f}× ☉"
                    row3.append(metric_card("Luminosity", lum_str,
                                            "Total energy output compared to our Sun (☉ = 1 solar "
                                            "luminosity = 3.828 × 10²⁶ watts). A star 100× the "
                                            "Sun's luminosity radiates 100 times as much energy across all "
                                            "wavelengths."))
                rad = info.get("radius_sun")
                if rad is not None:
                    rad_str = f"{rad:.0f}× ☉" if rad >= 10 else f"{rad:.2f}× ☉"
                    row3.append(metric_card("Radius", rad_str,
                                            "Physical size compared to our Sun's radius (☉ = 696,000 km). "
                                            "A star with radius 10× ☉ is ten times wider than the Sun "
                                            "in diameter."))
                st.html(metrics_row(row3))

            if others:
                st.html(f"<p style='font-size:0.7rem; color:#334455; margin-top:1.5rem;'>other matches: "
                            + "  ·  ".join(f"<span style='color:#556688;'>{o}</span>" for o in others)
                            + "</p>")

            rb = st.session_state.radiance_by_year if st.session_state.searched else SD_RADIANCE
            lm12 = radiance_to_limiting_magnitude(rb.get(2012, SD_RADIANCE[2012]))
            lm23 = radiance_to_limiting_magnitude(rb.get(2023, SD_RADIANCE[2023]))
            fun = star_fun_fact(name, mag, info, lm12, lm23,
                                st.session_state.place_name, rb)
            if fun:
                st.html("<br>")
                st.html(f"""
<div style='max-width:680px; margin:0 auto; background:#0a0a18;
     border-left:2px solid #FF4444; padding:1rem 1.5rem; border-radius:0 4px 4px 0;'>
  <p style='font-size:0.65rem; letter-spacing:0.18em; color:#FF4444; margin:0 0 0.4rem 0;'>FUN FACT</p>
  <p style='font-size:0.88rem; line-height:1.9; color:#8899BB; margin:0;'>{fun}</p>
</div>""")

            history = STAR_HISTORY.get(name, "")
            if history:
                st.html("<br>")
                st.html(
                    "<div style='max-width:680px; margin:0 auto; background:#0a0a18;"
                    " border-left:2px solid #2a4a8a; padding:1rem 1.5rem; border-radius:0 4px 4px 0;'>"
                    "<p style='font-size:0.65rem; letter-spacing:0.18em; color:#4466AA; margin:0 0 0.4rem 0;'>HISTORY &amp; MYTHOLOGY</p>"
                    "<p style='font-size:0.88rem; line-height:1.9; color:#7799BB; margin:0;'>"
                    + history +
                    "</p></div>"
                )

            siblings = sorted([
                s for s in STARS
                if s[0] != name
                and STAR_INFO.get(s[0], {}).get("constellation") == info.get("constellation")
            ], key=lambda s: s[1])
            if siblings:
                st.html("<br>")
                sib_links = "  ·  ".join(
                    "<a href='?page=stars&star=" + s[0].replace(" ", "%20") + "' target='_self' "
                    "style='color:#445577; text-decoration:none; font-size:0.8rem;'>" + s[0] + "</a>"
                    for s in siblings
                )
                st.html(
                    f"<p style='font-size:0.58rem; letter-spacing:0.18em; color:#334455; margin:0 0 0.4rem 0;'>"
                    f"ALSO IN {info.get('constellation','').upper()}</p>"
                    f"<p style='margin:0;'>{sib_links}</p>")

            if description:
                st.html("<br>")
                st.html("<hr>")
                st.html("<br>")
                st.html(f"<p style='max-width:680px; margin:0 auto; font-size:0.9rem; line-height:2.1; color:#7788AA;'>{description}</p>")
                st.html(f"<p style='max-width:680px; margin:0.5rem auto 0; font-size:0.6rem; letter-spacing:0.08em; color:#334455;'>SOURCE: WIKIPEDIA</p>")

    st.stop()

st.html("<br><br>")
st.html("<hr>")
st.html("<br>")
st.html("<p style='text-align:center; letter-spacing:0.15em; font-size:0.7rem; color:#6666AA;'>HOW IS THIS DIFFERENT</p>")
st.html("<br>")
st.html("<p style='text-align:center; max-width:600px; margin:0 auto; font-size:0.9rem; line-height:2; color:#7788AA;'>Tools like Light Pollution Map, NASA Worldview, and Globe at Night show raw radiance data built for researchers. This tool translates that data into something human — the actual named stars you have lost from your specific sky, since 2012.</p>")
st.html("<br><br>")
st.html("<br><br>")
