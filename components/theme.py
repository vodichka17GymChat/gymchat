"""
Shared GymChat visual theme.

Call inject_theme() once per page, right after st.set_page_config().
All design tokens are CSS custom properties — change a value here and
it propagates to every element that references the variable.

Token reference:
  --bg             Page background (light blue-white gradient base)
  --surface        Glass-card surface (white at ~78% opacity)
  --accent         Primary sky/cyan (#3DA9FC)
  --accent-strong  Deeper navy for emphasis (#1B6ECC)
  --text           Slate dark body text (#1B2A41)
  --text-muted     Secondary / caption text (#6B7A90)
  --radius         Standard border-radius (14px)
  --shadow         Standard drop-shadow colour
"""

import streamlit as st

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Design tokens ───────────────────────────────────────────────────────── */
:root {
  --bg:            #F4F8FC;
  --surface:       rgba(255, 255, 255, 0.78);
  --accent:        #3DA9FC;
  --accent-strong: #1B6ECC;
  --accent-glow:   rgba(61, 169, 252, 0.18);
  --accent-bg:     rgba(61, 169, 252, 0.07);
  --text:          #1B2A41;
  --text-muted:    #6B7A90;
  --border:        rgba(61, 169, 252, 0.17);
  --radius:        14px;
  --radius-sm:     8px;
  --shadow:        rgba(31, 78, 140, 0.09);
}

/* ── App shell ───────────────────────────────────────────────────────────── */
.stApp {
  background: linear-gradient(150deg, #EDF5FF 0%, #F4F8FC 55%, #EAF3FF 100%) !important;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
  color: var(--text) !important;
}
.main .block-container {
  padding-top: 2rem !important;
  padding-bottom: 3rem !important;
}

/* ── Typography ──────────────────────────────────────────────────────────── */
h1, h2, h3, h4 {
  font-family: 'Inter', sans-serif !important;
  letter-spacing: -0.02em !important;
  color: var(--text) !important;
}
h1 { font-size: 1.8rem !important; font-weight: 700 !important; }
h2 { font-size: 1.35rem !important; font-weight: 600 !important; }
h3 { font-size: 1.1rem !important; font-weight: 600 !important; }

/* ── Bordered containers → glassmorphism cards ───────────────────────────── */
[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--surface) !important;
  backdrop-filter: blur(16px) !important;
  -webkit-backdrop-filter: blur(16px) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  box-shadow: 0 2px 20px var(--shadow), 0 0 0 0.5px rgba(61,169,252,0.06) !important;
}

/* ── Buttons ─────────────────────────────────────────────────────────────── */
.stButton > button {
  font-family: 'Inter', sans-serif !important;
  font-weight: 500 !important;
  font-size: 0.9rem !important;
  border-radius: var(--radius-sm) !important;
  transition: box-shadow 0.18s ease, transform 0.18s ease, background 0.18s ease !important;
}
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, var(--accent), var(--accent-strong)) !important;
  border: none !important;
  color: #fff !important;
  box-shadow: 0 2px 14px var(--accent-glow) !important;
}
.stButton > button[kind="primary"]:hover {
  box-shadow: 0 4px 22px rgba(61,169,252,0.4) !important;
  transform: translateY(-1px) !important;
}
.stButton > button:not([kind="primary"]) {
  background: rgba(255,255,255,0.9) !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
}
.stButton > button:not([kind="primary"]):hover {
  background: var(--accent-bg) !important;
  border-color: var(--accent) !important;
}

/* ── Form submit buttons ─────────────────────────────────────────────────── */
[data-testid="stFormSubmitButton"] > button {
  background: linear-gradient(135deg, var(--accent), var(--accent-strong)) !important;
  border: none !important;
  color: #fff !important;
  font-weight: 600 !important;
  font-size: 0.95rem !important;
  border-radius: var(--radius-sm) !important;
  box-shadow: 0 2px 18px var(--accent-glow) !important;
  transition: box-shadow 0.18s ease, transform 0.18s ease !important;
}
[data-testid="stFormSubmitButton"] > button:hover {
  box-shadow: 0 4px 26px rgba(61,169,252,0.42) !important;
  transform: translateY(-1px) !important;
}

/* ── Text inputs ─────────────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
  font-family: 'Inter', sans-serif !important;
  border-radius: var(--radius-sm) !important;
  border: 1px solid var(--border) !important;
  background: rgba(255,255,255,0.9) !important;
  color: var(--text) !important;
  transition: border-color 0.15s, box-shadow 0.15s !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--accent-glow) !important;
  outline: none !important;
}

/* ── Selectbox ───────────────────────────────────────────────────────────── */
.stSelectbox > div > div {
  border-radius: var(--radius-sm) !important;
  border: 1px solid var(--border) !important;
  background: rgba(255,255,255,0.9) !important;
  color: var(--text) !important;
}
.stSelectbox > div > div:focus-within {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--accent-glow) !important;
}

/* ── Expanders ───────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
  background: var(--surface) !important;
  backdrop-filter: blur(12px) !important;
  -webkit-backdrop-filter: blur(12px) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  box-shadow: 0 2px 12px var(--shadow) !important;
  overflow: hidden !important;
}
[data-testid="stExpander"] summary {
  font-family: 'Inter', sans-serif !important;
  font-weight: 500 !important;
  color: var(--text) !important;
  padding: 0.75rem 1rem !important;
}
[data-testid="stExpander"] summary:hover {
  background: var(--accent-bg) !important;
}
[data-testid="stExpander"] summary svg {
  color: var(--accent) !important;
}

/* ── Tabs → pill toggles ─────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  background: rgba(234, 242, 251, 0.85) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  padding: 4px !important;
  gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 7px !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 500 !important;
  font-size: 0.88rem !important;
  color: var(--text-muted) !important;
  background: transparent !important;
  border: none !important;
  padding: 0.45rem 1.3rem !important;
  transition: all 0.15s ease !important;
}
.stTabs [aria-selected="true"] {
  background: #fff !important;
  color: var(--accent-strong) !important;
  box-shadow: 0 1px 8px var(--shadow) !important;
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ── Metrics → glass stat cards ──────────────────────────────────────────── */
[data-testid="stMetric"] {
  background: var(--surface) !important;
  backdrop-filter: blur(12px) !important;
  -webkit-backdrop-filter: blur(12px) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  box-shadow: 0 2px 12px var(--shadow) !important;
  padding: 1rem 1.1rem !important;
}
[data-testid="stMetricValue"] {
  font-size: 1.9rem !important;
  font-weight: 700 !important;
  color: var(--text) !important;
  font-variant-numeric: tabular-nums !important;
}
[data-testid="stMetricLabel"] {
  font-size: 0.66rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.09em !important;
  text-transform: uppercase !important;
  color: var(--text-muted) !important;
}

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: rgba(234, 242, 251, 0.97) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .stMarkdown p {
  font-size: 0.85rem !important;
  color: var(--text-muted) !important;
}

/* ── Alerts ──────────────────────────────────────────────────────────────── */
[data-testid="stAlert"] {
  border-radius: var(--radius-sm) !important;
}

/* ── Dataframes ──────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
  border-radius: var(--radius-sm) !important;
  overflow: hidden !important;
  font-variant-numeric: tabular-nums !important;
}

/* ── Captions ────────────────────────────────────────────────────────────── */
.stCaption p {
  color: var(--text-muted) !important;
  font-size: 0.8rem !important;
}

/* ── Dividers ────────────────────────────────────────────────────────────── */
hr {
  border: none !important;
  border-top: 1px solid var(--border) !important;
  margin: 1.25rem 0 !important;
}

/* ── Sliders ─────────────────────────────────────────────────────────────── */
[data-testid="stSlider"] [role="slider"] {
  background: var(--accent) !important;
  border-color: var(--accent) !important;
}

/* ── Checkboxes ──────────────────────────────────────────────────────────── */
[data-baseweb="checkbox"] input:checked ~ span {
  background: var(--accent) !important;
  border-color: var(--accent) !important;
}

/* ── Page links ──────────────────────────────────────────────────────────── */
[data-testid="stPageLink"] a {
  font-family: 'Inter', sans-serif !important;
  font-weight: 500 !important;
  font-size: 0.88rem !important;
  color: var(--accent-strong) !important;
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  padding: 0.5rem 0.75rem !important;
  display: block !important;
  text-align: center !important;
  text-decoration: none !important;
  transition: box-shadow 0.15s ease, transform 0.15s ease !important;
}
[data-testid="stPageLink"] a:hover {
  background: var(--accent-bg) !important;
  border-color: var(--accent) !important;
  box-shadow: 0 2px 12px var(--accent-glow) !important;
  transform: translateY(-1px) !important;
}

/* ══════════════════════════════════════════════════════════════════════════
   Utility classes — used in st.markdown(..., unsafe_allow_html=True) blocks.
   These only apply to pure HTML; Streamlit widgets inside them are rendered
   outside the DOM tree so layout tricks only work on static HTML.
   ══════════════════════════════════════════════════════════════════════════ */

/* Login / hero block */
.gc-hero {
  text-align: center;
  padding: 1.5rem 0 1.25rem;
}
.gc-hero-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 68px; height: 68px;
  background: linear-gradient(135deg, #3DA9FC, #1B6ECC);
  border-radius: 20px;
  font-size: 2rem;
  box-shadow: 0 6px 24px rgba(61,169,252,0.38);
  margin-bottom: 1rem;
}
.gc-hero-title {
  font-size: 1.7rem; font-weight: 700;
  letter-spacing: -0.02em; color: #1B2A41;
  margin: 0; font-family: 'Inter', sans-serif;
}
.gc-hero-sub {
  font-size: 0.88rem; color: #6B7A90;
  margin: 0.3rem 0 0; font-family: 'Inter', sans-serif;
}

/* Section label (eyebrow text above a section) */
.gc-section-label {
  font-size: 0.68rem; font-weight: 600;
  letter-spacing: 0.1em; text-transform: uppercase;
  color: #6B7A90; margin: 1.25rem 0 0.4rem;
  font-family: 'Inter', sans-serif;
}

/* Live-session status strip */
.gc-status-strip {
  background: linear-gradient(135deg, rgba(61,169,252,0.08), rgba(27,110,204,0.05));
  border: 1px solid rgba(61,169,252,0.2);
  border-radius: 12px;
  padding: 0.75rem 1.2rem;
  display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;
}
.gc-status-dot {
  width: 9px; height: 9px; border-radius: 50%;
  background: #10B981;
  box-shadow: 0 0 8px rgba(16,185,129,0.55);
  flex-shrink: 0;
}
.gc-status-label {
  font-weight: 600; font-size: 0.92rem; color: #1B2A41;
  font-family: 'Inter', sans-serif;
}
.gc-status-meta {
  font-size: 0.78rem; color: #6B7A90;
  font-family: 'Inter', sans-serif; margin-left: auto;
}

/* Coloured chip / badge */
.gc-chip {
  display: inline-block;
  padding: 0.18rem 0.6rem; border-radius: 20px;
  font-size: 0.72rem; font-weight: 600;
  font-family: 'Inter', sans-serif;
  vertical-align: middle;
}
.gc-chip-blue  { background: rgba(61,169,252,0.12); color:#1B6ECC; border:1px solid rgba(61,169,252,0.22); }
.gc-chip-green { background: rgba(16,185,129,0.1);  color:#059669; border:1px solid rgba(16,185,129,0.2); }
.gc-chip-amber { background: rgba(245,158,11,0.1);  color:#B45309; border:1px solid rgba(245,158,11,0.2); }

/* Account metadata strip (profile page) */
.gc-meta-strip {
  background: rgba(61,169,252,0.06);
  border: 1px solid rgba(61,169,252,0.15);
  border-radius: 10px;
  padding: 0.65rem 1rem;
  margin-bottom: 1rem;
  font-size: 0.82rem; color: #6B7A90;
  font-family: 'Inter', sans-serif;
  display: flex; gap: 1.75rem; flex-wrap: wrap; align-items: center;
}
.gc-meta-strip strong { color: #1B2A41; font-weight: 600; }

/* Monospace numerals (set tables, elapsed time) */
.gc-mono {
  font-variant-numeric: tabular-nums;
  font-feature-settings: "tnum";
  font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', 'Roboto Mono', monospace;
}
</style>
"""


def inject_theme() -> None:
    """Inject the shared GymChat CSS into the current Streamlit page."""
    st.markdown(_CSS, unsafe_allow_html=True)
