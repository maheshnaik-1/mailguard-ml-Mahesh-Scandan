"""Rengoku flame theme: CSS, animated embers and small HTML components for Streamlit.

Drop this file in ``src/theme.py`` and call ``inject_theme()`` once per page.
All animation is CSS-only and respects ``prefers-reduced-motion``.
"""

from __future__ import annotations

import random

import streamlit as st

# Flame palette
FLAME_GOLD = "#FFB703"
FLAME_ORANGE = "#FF6B1A"
FLAME_AMBER = "#FF9A3D"
FLAME_RED = "#D62828"
FLAME_CRIMSON = "#8E1426"
EMBER_DARK = "#10070A"
EMBER_PANEL = "#1B0D12"

_EMBER_COUNT = 28


def _embers_html() -> str:
    """Deterministic pseudo-random ember particles rising from the bottom."""
    rng = random.Random(1)
    spans = []
    for _ in range(_EMBER_COUNT):
        left = rng.uniform(0, 100)
        size = rng.uniform(3, 9)
        dur = rng.uniform(7, 15)
        delay = rng.uniform(-15, 0)
        drift = rng.uniform(-60, 60)
        spans.append(
            f'<span style="left:{left:.1f}%;width:{size:.1f}px;height:{size:.1f}px;'
            f"animation-duration:{dur:.1f}s;animation-delay:{delay:.1f}s;--drift:{drift:.0f}px\"></span>"
        )
    return f'<div class="rg-embers" aria-hidden="true">{"".join(spans)}</div>'


_CSS = f"""
<style>
:root {{
  --rg-gold: {FLAME_GOLD};
  --rg-orange: {FLAME_ORANGE};
  --rg-amber: {FLAME_AMBER};
  --rg-red: {FLAME_RED};
  --rg-crimson: {FLAME_CRIMSON};
  --rg-bg: {EMBER_DARK};
  --rg-panel: {EMBER_PANEL};
}}

/* ---------- Base ---------- */
.stApp {{
  background:
    radial-gradient(900px 520px at 8% 105%, rgba(255,107,26,.16), transparent 68%),
    radial-gradient(760px 420px at 94% -8%, rgba(142,20,38,.22), transparent 68%),
    linear-gradient(150deg, #0b0609 0%, var(--rg-bg) 55%, #19090d 100%) !important;
  background-size: 120% 120%;
  animation: rg-background-drift 24s ease-in-out infinite alternate;
  color: #f8eee8;
}}
.block-container {{
  position: relative; z-index: 1;
  padding-top: clamp(4.5rem, 8vh, 5.5rem) !important;
  padding-bottom: 3rem;
}}
body {{ font-family: Inter, "Segoe UI", sans-serif; }}
h1, h2, h3, h4 {{ letter-spacing: .015em; }}
h2, h3 {{ color: var(--rg-gold) !important; }}
[data-testid="stCaptionContainer"] {{ color: #c9b8b2; }}
@keyframes rg-background-drift {{
  from {{ background-position: 0% 0%; }}
  to {{ background-position: 100% 100%; }}
}}

/* ---------- Floating embers ---------- */
.rg-embers {{ position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }}
.rg-embers span {{
  position: absolute; bottom: -20px; border-radius: 50%;
  background: radial-gradient(circle, #fff6d5 0%, var(--rg-gold) 35%, var(--rg-orange) 70%, transparent 100%);
  box-shadow: 0 0 12px 3px rgba(255,140,40,.7);
  opacity: 0;
  animation-name: rg-rise; animation-timing-function: ease-in; animation-iteration-count: infinite;
}}
@keyframes rg-rise {{
  0%   {{ transform: translate(0, 0) scale(1); opacity: 0; }}
  10%  {{ opacity: .95; }}
  70%  {{ opacity: .6; }}
  100% {{ transform: translate(var(--drift), -105vh) scale(.2); opacity: 0; }}
}}

/* ---------- Page heading ---------- */
.rg-page-header {{
  position: relative; box-sizing: border-box; min-height: 7.5rem;
  margin: 0 0 1.35rem; padding: .45rem 0 .8rem; overflow: visible;
  animation: rg-fade-up .65s ease both;
}}
.rg-page-header h1 {{
  margin: 0; padding: .08em 0 .12em; overflow: visible;
  font-size: clamp(2rem, 3.2vw, 2.65rem); font-weight: 800; line-height: 1.2;
  background: linear-gradient(90deg, var(--rg-gold), var(--rg-orange), var(--rg-red), var(--rg-orange), var(--rg-gold));
  background-size: 250% 100%;
  -webkit-background-clip: text; background-clip: text; color: transparent;
  animation: rg-flow 9s linear infinite, rg-flicker 5s ease-in-out infinite;
  filter: drop-shadow(0 0 8px rgba(255,107,26,.42));
}}
.rg-page-header p {{ margin: .48rem 0 0; color: #f5ded1; font-size: 1rem; line-height: 1.5; }}
.rg-page-header::after {{
  content: ""; display: block; width: min(8rem, 24%); height: 2px; margin-top: 1rem;
  background: linear-gradient(90deg, var(--rg-crimson), var(--rg-orange), var(--rg-gold), transparent);
  box-shadow: 0 0 10px rgba(255,107,26,.28);
}}
@keyframes rg-flow {{ to {{ background-position: 250% 0; }} }}
@keyframes rg-flicker {{
  0%, 100% {{ filter: drop-shadow(0 0 8px rgba(255,107,26,.5)); }}
  30% {{ filter: drop-shadow(0 0 13px rgba(255,160,40,.72)); }}
  55% {{ filter: drop-shadow(0 0 10px rgba(255,90,20,.6)); }}
  80% {{ filter: drop-shadow(0 0 14px rgba(255,183,3,.7)); }}
}}
@keyframes rg-fade-up {{ from {{ opacity: 0; transform: translateY(18px); }} to {{ opacity: 1; transform: none; }} }}

/* ---------- Buttons ---------- */
.stButton > button, .stDownloadButton > button {{
  border-radius: 12px; border: 1px solid rgba(255,140,40,.5);
  background: rgba(32,16,9,.85); color: #ffe3c7; transition: transform .2s, box-shadow .25s, border-color .25s;
}}
.stButton > button:hover {{ transform: translateY(-2px); border-color: var(--rg-gold); box-shadow: 0 6px 20px rgba(255,107,26,.35); color: #fff; }}
.stButton > button:active {{ transform: translateY(0) scale(.98); }}
.stButton > button[kind="primary"] {{
  border: none; color: #1a0905; font-weight: 700;
  background: linear-gradient(100deg, var(--rg-gold), var(--rg-orange), var(--rg-red), var(--rg-orange));
  background-size: 220% 100%; animation: rg-flow 8s linear infinite;
}}
.stButton > button[kind="primary"]:hover {{ box-shadow: 0 0 22px rgba(255,140,40,.62); color: #1a0905; }}
.stButton > button:focus-visible, .stDownloadButton > button:focus-visible {{
  outline: 2px solid var(--rg-gold); outline-offset: 3px;
}}

/* ---------- Inputs ---------- */
.stTextInput input, .stTextArea textarea, .stNumberInput input,
.stSelectbox [data-baseweb="select"] > div, .stMultiSelect [data-baseweb="select"] > div,
[data-testid="stFileUploaderDropzone"] {{
  background: rgba(27,13,18,.88) !important; color: #f8eee8 !important;
  border: 1px solid rgba(255,154,61,.3) !important; border-radius: 11px !important;
  transition: border-color .22s ease, box-shadow .22s ease, background .22s ease;
}}
.stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus,
.stSelectbox [data-baseweb="select"] > div:focus-within, .stMultiSelect [data-baseweb="select"] > div:focus-within {{
  border-color: var(--rg-gold) !important;
  box-shadow: 0 0 0 2px rgba(255,183,3,.2), 0 0 18px rgba(255,107,26,.2) !important;
}}
[data-testid="stFileUploaderDropzone"]:hover {{ border-color: var(--rg-gold) !important; box-shadow: 0 0 18px rgba(255,107,26,.23); }}
[role="listbox"], [role="option"] {{ background-color: #211117 !important; color: #f8eee8 !important; }}
[role="option"]:hover {{ background-color: rgba(255,107,26,.2) !important; }}
.stSlider [data-baseweb="slider"] > div > div {{ background: linear-gradient(90deg, var(--rg-gold), var(--rg-orange), var(--rg-red)) !important; }}
.stSlider [role="slider"] {{ background: var(--rg-gold) !important; box-shadow: 0 0 14px rgba(255,183,3,.9) !important; }}
.stProgress [data-testid="stProgressBar"] > div {{ background: linear-gradient(90deg, var(--rg-red), var(--rg-orange), var(--rg-gold)) !important; }}

[data-testid="stMain"] {{ position: relative; z-index: 1; }}
[data-testid="stSidebar"] {{ position: relative; z-index: 1; }}

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] {{ gap: .4rem; border-bottom: 1px solid rgba(255,140,40,.25); }}
.stTabs [data-baseweb="tab"] {{ border-radius: 10px 10px 0 0; transition: background .25s, color .25s; }}
.stTabs [data-baseweb="tab"]:hover {{ background: rgba(255,107,26,.14); color: var(--rg-gold); }}
.stTabs [aria-selected="true"] {{ color: var(--rg-gold) !important; }}
.stTabs [data-baseweb="tab-highlight"] {{
  background: linear-gradient(90deg, var(--rg-gold), var(--rg-orange), var(--rg-red)) !important; height: 3px;
  box-shadow: 0 0 12px var(--rg-orange);
}}
.stTabs [data-baseweb="tab-panel"] {{ animation: rg-fade-up .45s ease both; }}

/* ---------- Metrics ---------- */
[data-testid="stMetric"] {{
  background: linear-gradient(150deg, rgba(45,17,22,.88), rgba(24,12,17,.94));
  border: 1px solid rgba(255,154,61,.3); border-radius: 14px; padding: .9rem 1rem;
  transition: transform .25s, box-shadow .25s, border-color .25s; animation: rg-fade-up .6s ease both;
}}
[data-testid="stMetric"]:hover {{ transform: translateY(-3px); border-color: var(--rg-gold); box-shadow: 0 9px 24px rgba(255,107,26,.24); }}
[data-testid="stMetricValue"] {{ color: var(--rg-gold); text-shadow: 0 0 12px rgba(255,140,40,.55); }}
[data-testid="stHorizontalBlock"] > div:nth-child(2) [data-testid="stMetric"] {{ animation-delay: .08s; }}
[data-testid="stHorizontalBlock"] > div:nth-child(3) [data-testid="stMetric"] {{ animation-delay: .16s; }}
[data-testid="stHorizontalBlock"] > div:nth-child(4) [data-testid="stMetric"] {{ animation-delay: .24s; }}

/* ---------- Verdict banner ---------- */
.rg-verdict {{
  display: flex; align-items: center; gap: 1rem; margin: 1rem 0; padding: 1.1rem 1.4rem; border-radius: 16px;
  animation: rg-fade-up .6s ease both;
}}
.rg-verdict .rg-title {{ font-size: 1.5rem; font-weight: 800; letter-spacing: .08em; }}
.rg-verdict .rg-sub {{ opacity: .92; font-size: .95rem; }}
.rg-verdict .rg-seal {{
  flex: 0 0 auto; width: 56px; height: 56px; border-radius: 50%; display: grid; place-items: center;
  font-size: 1.7rem; font-weight: 900;
}}
.rg-spam {{
  background: linear-gradient(110deg, rgba(214,40,40,.55), rgba(120,10,10,.55));
  border: 1px solid #ff4d4d; color: #ffe0dc;
  animation: rg-fade-up .6s ease both, rg-alarm 1.6s ease-in-out .6s infinite;
}}
.rg-spam .rg-seal {{ background: #D62828; color: #fff; box-shadow: 0 0 20px #ff3b3b; animation: rg-shake .6s ease .3s 2; }}
.rg-ham {{
  background: linear-gradient(110deg, rgba(255,183,3,.30), rgba(255,107,26,.22));
  border: 1px solid var(--rg-gold); color: #fff1d6;
  animation: rg-fade-up .6s ease both, rg-glow-gold 2.6s ease-in-out .6s infinite;
}}
.rg-ham .rg-seal {{ background: linear-gradient(135deg, var(--rg-gold), var(--rg-orange)); color: #1a0905; box-shadow: 0 0 20px rgba(255,183,3,.9); }}
@keyframes rg-alarm {{ 0%, 100% {{ box-shadow: 0 0 10px rgba(214,40,40,.4); }} 50% {{ box-shadow: 0 0 34px rgba(255,60,60,.8); }} }}
@keyframes rg-glow-gold {{ 0%, 100% {{ box-shadow: 0 0 12px rgba(255,183,3,.35); }} 50% {{ box-shadow: 0 0 34px rgba(255,160,40,.75); }} }}
@keyframes rg-shake {{ 0%, 100% {{ transform: translateX(0); }} 25% {{ transform: translateX(-5px) rotate(-6deg); }} 75% {{ transform: translateX(5px) rotate(6deg); }} }}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {{
  background: linear-gradient(200deg, #261017 0%, #170a10 58%, #0d070a 100%) !important;
  border-right: 1px solid rgba(255,154,61,.3);
  box-shadow: 4px 0 26px rgba(116,20,35,.18);
}}
[data-testid="stSidebar"] h3 {{
  background: linear-gradient(90deg, var(--rg-gold), var(--rg-orange), var(--rg-red), var(--rg-gold));
  background-size: 250% 100%; -webkit-background-clip: text; background-clip: text; color: transparent !important;
  animation: rg-flow 6s linear infinite;
}}
[data-testid="stSidebarNavLink"] {{ border-radius: 10px; transition: background .25s, transform .25s, box-shadow .25s; }}
[data-testid="stSidebarNavLink"]:hover {{ background: rgba(255,107,26,.18); transform: translateX(4px); }}
[data-testid="stSidebarNavLink"][aria-current="page"] {{
  background: linear-gradient(90deg, rgba(255,183,3,.2), rgba(214,40,40,.24), rgba(142,20,38,.12));
  border-left: 3px solid var(--rg-gold); box-shadow: 0 0 14px rgba(255,107,26,.27);
}}
[data-testid="stSidebarNavLink"][aria-current="page"] p {{ color: #ffe3b2 !important; font-weight: 700; }}
[data-testid="stSidebar"] [data-testid="stAlert"] {{ animation: rg-fade-up .6s ease both; }}

/* ---------- Misc ---------- */
hr {{ border: none !important; height: 2px !important; background: linear-gradient(90deg, transparent, var(--rg-orange), transparent) !important; opacity: .8; }}
[data-testid="stAlert"] {{ border-radius: 13px; animation: rg-fade-up .5s ease both; }}
[data-testid="stExpander"] {{
  border: 1px solid rgba(255,154,61,.28) !important; border-radius: 12px !important;
  background: rgba(27,13,18,.55); transition: border-color .22s ease, box-shadow .22s ease;
}}
[data-testid="stExpander"]:hover {{ border-color: rgba(255,183,3,.55) !important; box-shadow: 0 5px 18px rgba(255,107,26,.12); }}
[data-testid="stDataFrame"], [data-testid="stTable"] {{
  border-radius: 13px; overflow: hidden; border: 1px solid rgba(255,154,61,.35);
  background: rgba(27,13,18,.55); box-shadow: 0 0 18px rgba(255,107,26,.12);
  transition: box-shadow .3s, border-color .3s; animation: rg-fade-up .5s ease both;
}}
[data-testid="stDataFrame"]:hover, [data-testid="stTable"]:hover {{ border-color: var(--rg-gold); box-shadow: 0 0 28px rgba(255,183,3,.30); }}
[data-testid="stPlotlyChart"] {{ border-radius: 12px; }}

@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{ animation: none !important; transition: none !important; }}
  .rg-embers {{ display: none; }}
}}
</style>
"""


def inject_theme() -> None:
    """Inject the Rengoku CSS and the ember particle layer. Call once near the top of a page."""
    st.markdown(_CSS + _embers_html(), unsafe_allow_html=True)


def hero(title: str, subtitle: str) -> None:
    """Render a standalone page heading and its description from trusted static strings."""
    st.markdown(
        f'<header class="rg-page-header"><h1>{title}</h1><p>{subtitle}</p></header>',
        unsafe_allow_html=True,
    )


def verdict_banner(is_spam: bool, probability: float, threshold: float) -> None:
    """Animated verdict banner. Only numeric values are interpolated, so no HTML injection is possible."""
    if is_spam:
        cls, seal, title = "rg-spam", "✖", "SPAM DETECTED"
        sub = f"Probability {probability:.3f} ≥ threshold {threshold:.2f}. This one gets cut down."
    else:
        cls, seal, title = "rg-ham", "✔", "LEGITIMATE (HAM)"
        sub = f"Probability {probability:.3f} &lt; threshold {threshold:.2f}. The flame burns clear: safe to read."
    st.markdown(
        f'<div class="rg-verdict {cls}"><div class="rg-seal">{seal}</div>'
        f'<div><div class="rg-title">{title}</div><div class="rg-sub">{sub}</div></div></div>',
        unsafe_allow_html=True,
    )
