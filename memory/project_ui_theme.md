---
name: GymChat UI theme system
description: Light blue futuristic theme added — where to find tokens, how to extend
type: project
---

GymChat received a full visual redesign targeting a light-blue/glassmorphism aesthetic.

**Why:** User requested a "sleek fitness-tech" look, away from default Streamlit dark theme.

**How to apply:** All CSS tokens and utility classes live in `components/theme.py`. Every page calls `inject_theme()` once, right after `st.set_page_config()`. Never call it from within components (they're rendered inside pages that already injected it).

Token names: `--bg`, `--surface`, `--accent` (#3DA9FC), `--accent-strong` (#1B6ECC), `--text`, `--text-muted`, `--border`, `--radius`, `--shadow`.

Glass card effect comes from `st.container(border=True)` — the CSS targets `[data-testid="stVerticalBlockBorderWrapper"]` automatically.

Utility HTML classes defined in theme.py (use in `st.markdown(..., unsafe_allow_html=True)`):
- `.gc-hero` / `.gc-hero-icon` / `.gc-hero-title` / `.gc-hero-sub` — login page hero
- `.gc-section-label` — eyebrow text above sections
- `.gc-status-strip` / `.gc-status-dot` / `.gc-status-label` / `.gc-status-meta` — active workout status bar
- `.gc-chip` + `.gc-chip-blue/.green/.amber` — inline coloured badges
- `.gc-meta-strip` — quiet header strip (profile page account info)
- `.gc-mono` — monospace tabular numerals
