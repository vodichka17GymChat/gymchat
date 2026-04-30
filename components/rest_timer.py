"""
Rest timer component. Shows a live-updating counter from a given start
time and exposes a helper to read the current elapsed seconds when the
user logs their next set.

Why a Streamlit fragment? In plain Streamlit, `st.markdown` of an
elapsed-time string would only refresh on the next user interaction.
With `@st.fragment(run_every=1.0)` the timer rerenders itself every
second WITHOUT rerunning the whole page - so the user sees a real
clock without losing form state or scrolling position.

Color thresholds:
  0-60s   green    (typical isolation rest)
  60-180s amber    (typical compound rest)
  180s+   red      (if you're resting >3 min, you've probably wandered off)

These are visual cues only - we don't enforce or judge anything.
"""

from datetime import datetime

import streamlit as st


# Color thresholds (seconds). Tweakable in one place if we want to make
# them user-configurable later (e.g. powerlifters often want longer
# green bands).
_GREEN_UNTIL = 60
_AMBER_UNTIL = 180

_COLOR_GREEN = "#059669"
_COLOR_AMBER = "#D97706"
_COLOR_RED = "#DC2626"


@st.fragment(run_every=1.0)
def render_live(start_time_iso: str) -> None:
    """
    Render a live, auto-updating rest timer. Pass the ISO timestamp of
    when the previous set was logged - the timer counts up from there.

    Wrapped in @st.fragment so only this block rerenders every second;
    the rest of the page stays still.
    """
    elapsed = get_elapsed_seconds(start_time_iso)
    color = _color_for(elapsed)
    label = _format_mmss(elapsed)

    # We use raw HTML rather than st.metric because we want full control
    # over the color and the visual weight - a fitness app's rest timer
    # is a focal element, not a passive stat.
    st.markdown(
        f"""
        <div style="
            text-align: center;
            padding: 0.6rem 1rem;
            border: 1px solid {color}44;
            border-radius: 10px;
            background: {color}0D;
            margin: 0.25rem 0 0.75rem 0;
        ">
            <div style="font-size: 0.72rem; font-weight:600; letter-spacing:0.08em;
                        text-transform:uppercase; color:{color}; opacity:0.8;
                        font-family:'Inter',sans-serif;">
                ⏱ &nbsp; RESTING
            </div>
            <div style="
                font-size: 2rem;
                font-weight: 700;
                color: {color};
                font-variant-numeric: tabular-nums;
                font-family: 'JetBrains Mono','Fira Code','SF Mono',monospace;
                line-height: 1.1;
            ">
                {label}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_elapsed_seconds(start_time_iso: str | None) -> int:
    """
    Return seconds elapsed since start_time_iso, or 0 if the input is
    None or unparseable. The workout page calls this when logging a set
    to capture the measured rest time.
    """
    if not start_time_iso:
        return 0
    try:
        start = datetime.fromisoformat(start_time_iso)
    except ValueError:
        return 0
    return max(0, int((datetime.now() - start).total_seconds()))


# ============================================================
# Internal helpers
# ============================================================

def _color_for(elapsed_seconds: int) -> str:
    if elapsed_seconds < _GREEN_UNTIL:
        return _COLOR_GREEN
    if elapsed_seconds < _AMBER_UNTIL:
        return _COLOR_AMBER
    return _COLOR_RED


def _format_mmss(seconds: int) -> str:
    """Format as M:SS (with zero-padded seconds), or just SS for under a minute."""
    m, s = divmod(seconds, 60)
    return f"{m}:{s:02d}" if m > 0 else f"{s}s"
