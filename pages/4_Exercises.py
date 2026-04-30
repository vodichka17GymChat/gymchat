"""
Exercise Library page - clickable muscle body diagram on the left,
exercise list on the right.

Clicking a muscle region in the SVG diagram navigates the parent frame
to the same page with a ?muscle=<name> query param, which Streamlit reads
on rerun to filter the exercise list.
"""

import streamlit as st
import streamlit.components.v1 as components

from db import exercises as exercises_db
from db.connection import get_connection


# ============================================================
# Auth gate
# ============================================================

if st.session_state.get("user_id") is None:
    st.warning("Please log in from the home page first.")
    st.stop()

USER_ID = st.session_state.user_id

with st.sidebar:
    st.write(f"Signed in as **{st.session_state.user_email}**")


# ============================================================
# Selected muscle — read from URL query params (Streamlit 1.29 API)
# ============================================================

VALID_MUSCLES = {
    "chest", "back", "shoulders", "biceps", "triceps",
    "quads", "hamstrings", "glutes", "calves", "core",
}

_params = st.experimental_get_query_params()
_raw = _params.get("muscle", [""])[0]
selected = _raw if _raw in VALID_MUSCLES else ""


# ============================================================
# Per-exercise usage stats for this user
# ============================================================

def _usage_counts(user_id: int) -> dict[int, int]:
    """exercise_id → sessions logged by this user."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT ex.exercise_id, COUNT(DISTINCT ex.session_id) AS n
            FROM exercise_executions ex
            JOIN workout_sessions ws ON ex.session_id = ws.session_id
            WHERE ws.user_id = ?
            GROUP BY ex.exercise_id
            """,
            (user_id,),
        ).fetchall()
        return {r["exercise_id"]: r["n"] for r in rows}
    finally:
        conn.close()


usage = _usage_counts(USER_ID)


# ============================================================
# SVG body diagram
# ============================================================

_ACCENT = "#FF4B4B"
_DIM    = "#3d5a80"
_BODY   = "#1e2530"
_STROKE = "#4a5568"


def _c(muscle: str) -> str:
    return _ACCENT if muscle == selected else _DIM


def _border(muscle: str) -> str:
    return f'stroke="{_ACCENT}" stroke-width="2.5"' if muscle == selected else 'stroke="none"'


def _body_svg() -> str:
    """Return a full HTML page containing the front+back body SVG."""
    c = {m: _c(m) for m in VALID_MUSCLES}
    b = {m: _border(m) for m in VALID_MUSCLES}

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: transparent; overflow: hidden; }}
  .m {{ cursor: pointer; transition: opacity .15s; }}
  .m:hover {{ opacity: .75; }}
  .vtit {{ font: bold 11px system-ui; fill: #718096; text-anchor: middle; }}
  .lbl  {{ font: 9px system-ui; fill: #e2e8f0; text-anchor: middle; pointer-events: none; }}
</style>
<script>
function pick(m) {{
  var base = window.parent.location.pathname;
  var next = (m === '{selected}') ? base : base + '?muscle=' + m;
  window.parent.location.href = next;
}}
</script>
</head>
<body>
<svg viewBox="0 0 300 490" width="100%" xmlns="http://www.w3.org/2000/svg">

<!-- ── titles ── -->
<text x="75"  y="14" class="vtit">FRONT</text>
<text x="225" y="14" class="vtit">BACK</text>

<!-- ═══════════════════════════════
     FRONT body base (non-clickable)
     ═══════════════════════════════ -->
<!-- head -->
<circle cx="75" cy="42" r="21" fill="{_BODY}" stroke="{_STROKE}" stroke-width="1.5"/>
<!-- neck -->
<rect x="68" y="62" width="14" height="13" fill="{_BODY}"/>
<!-- torso -->
<path d="M40,75 Q75,68 110,75 L106,195 Q75,200 44,195 Z"
      fill="{_BODY}" stroke="{_STROKE}" stroke-width="1"/>
<!-- hips -->
<rect x="40" y="193" width="70" height="22" rx="6"
      fill="{_BODY}" stroke="{_STROKE}" stroke-width="1"/>
<!-- L/R upper arm shells -->
<rect x="17"  y="74" width="20" height="72" rx="9" fill="{_BODY}" stroke="{_STROKE}" stroke-width="1"/>
<rect x="113" y="74" width="20" height="72" rx="9" fill="{_BODY}" stroke="{_STROKE}" stroke-width="1"/>
<!-- L/R forearms -->
<rect x="19"  y="148" width="16" height="52" rx="7" fill="{_BODY}" stroke="{_STROKE}" stroke-width="1"/>
<rect x="115" y="148" width="16" height="52" rx="7" fill="{_BODY}" stroke="{_STROKE}" stroke-width="1"/>
<!-- L/R thighs -->
<rect x="41" y="214" width="29" height="96" rx="12" fill="{_BODY}" stroke="{_STROKE}" stroke-width="1"/>
<rect x="80" y="214" width="29" height="96" rx="12" fill="{_BODY}" stroke="{_STROKE}" stroke-width="1"/>
<!-- L/R shins -->
<rect x="43" y="313" width="25" height="88" rx="10" fill="{_BODY}" stroke="{_STROKE}" stroke-width="1"/>
<rect x="82" y="313" width="25" height="88" rx="10" fill="{_BODY}" stroke="{_STROKE}" stroke-width="1"/>
<!-- feet -->
<ellipse cx="57" cy="404" rx="19" ry="8" fill="{_BODY}" stroke="{_STROKE}" stroke-width="1"/>
<ellipse cx="93" cy="404" rx="19" ry="8" fill="{_BODY}" stroke="{_STROKE}" stroke-width="1"/>

<!-- ── FRONT muscles ── -->

<g class="m" onclick="pick('shoulders')">
  <ellipse cx="27"  cy="88" rx="13" ry="17" fill="{c['shoulders']}" {b['shoulders']}/>
  <ellipse cx="123" cy="88" rx="13" ry="17" fill="{c['shoulders']}" {b['shoulders']}/>
  <text x="27"  y="93" class="lbl" font-size="7">delt</text>
  <text x="123" y="93" class="lbl" font-size="7">delt</text>
</g>

<g class="m" onclick="pick('chest')">
  <ellipse cx="63" cy="103" rx="18" ry="22" fill="{c['chest']}" {b['chest']}/>
  <ellipse cx="87" cy="103" rx="18" ry="22" fill="{c['chest']}" {b['chest']}/>
  <text x="75" y="107" class="lbl">chest</text>
</g>

<g class="m" onclick="pick('biceps')">
  <rect x="18"  y="76" width="18" height="68" rx="8" fill="{c['biceps']}" {b['biceps']}/>
  <rect x="114" y="76" width="18" height="68" rx="8" fill="{c['biceps']}" {b['biceps']}/>
  <text x="27"  y="114" class="lbl" font-size="7">bi</text>
  <text x="123" y="114" class="lbl" font-size="7">bi</text>
</g>

<g class="m" onclick="pick('core')">
  <rect x="52" y="126" width="46" height="64" rx="5" fill="{c['core']}" {b['core']}/>
  <text x="75" y="162" class="lbl">core</text>
</g>

<g class="m" onclick="pick('quads')">
  <rect x="42" y="215" width="27" height="91" rx="11" fill="{c['quads']}" {b['quads']}/>
  <rect x="81" y="215" width="27" height="91" rx="11" fill="{c['quads']}" {b['quads']}/>
  <text x="75" y="264" class="lbl">quads</text>
</g>

<g class="m" onclick="pick('calves')">
  <rect x="44" y="314" width="23" height="84" rx="9" fill="{c['calves']}" {b['calves']}/>
  <rect x="83" y="314" width="23" height="84" rx="9" fill="{c['calves']}" {b['calves']}/>
  <text x="75" y="358" class="lbl" font-size="8">calves</text>
</g>


<!-- ═══════════════════════════════
     BACK body base (x offset +150)
     ═══════════════════════════════ -->
<circle cx="225" cy="42" r="21" fill="{_BODY}" stroke="{_STROKE}" stroke-width="1.5"/>
<rect x="218" y="62" width="14" height="13" fill="{_BODY}"/>
<path d="M190,75 Q225,68 260,75 L256,195 Q225,200 194,195 Z"
      fill="{_BODY}" stroke="{_STROKE}" stroke-width="1"/>
<rect x="190" y="193" width="70" height="22" rx="6"
      fill="{_BODY}" stroke="{_STROKE}" stroke-width="1"/>
<rect x="167" y="74" width="20" height="72" rx="9" fill="{_BODY}" stroke="{_STROKE}" stroke-width="1"/>
<rect x="263" y="74" width="20" height="72" rx="9" fill="{_BODY}" stroke="{_STROKE}" stroke-width="1"/>
<rect x="169" y="148" width="16" height="52" rx="7" fill="{_BODY}" stroke="{_STROKE}" stroke-width="1"/>
<rect x="265" y="148" width="16" height="52" rx="7" fill="{_BODY}" stroke="{_STROKE}" stroke-width="1"/>
<rect x="191" y="214" width="29" height="96" rx="12" fill="{_BODY}" stroke="{_STROKE}" stroke-width="1"/>
<rect x="230" y="214" width="29" height="96" rx="12" fill="{_BODY}" stroke="{_STROKE}" stroke-width="1"/>
<rect x="193" y="313" width="25" height="88" rx="10" fill="{_BODY}" stroke="{_STROKE}" stroke-width="1"/>
<rect x="232" y="313" width="25" height="88" rx="10" fill="{_BODY}" stroke="{_STROKE}" stroke-width="1"/>
<ellipse cx="207" cy="404" rx="19" ry="8" fill="{_BODY}" stroke="{_STROKE}" stroke-width="1"/>
<ellipse cx="243" cy="404" rx="19" ry="8" fill="{_BODY}" stroke="{_STROKE}" stroke-width="1"/>

<!-- ── BACK muscles ── -->

<g class="m" onclick="pick('shoulders')">
  <ellipse cx="177" cy="88" rx="13" ry="17" fill="{c['shoulders']}" {b['shoulders']}/>
  <ellipse cx="273" cy="88" rx="13" ry="17" fill="{c['shoulders']}" {b['shoulders']}/>
  <text x="177" y="93" class="lbl" font-size="7">delt</text>
  <text x="273" y="93" class="lbl" font-size="7">delt</text>
</g>

<g class="m" onclick="pick('back')">
  <path d="M198,76 Q225,70 252,76 L250,193 Q225,198 200,193 Z"
        fill="{c['back']}" {b['back']}/>
  <text x="225" y="138" class="lbl">back</text>
</g>

<g class="m" onclick="pick('triceps')">
  <rect x="168" y="76" width="18" height="68" rx="8" fill="{c['triceps']}" {b['triceps']}/>
  <rect x="264" y="76" width="18" height="68" rx="8" fill="{c['triceps']}" {b['triceps']}/>
  <text x="177" y="114" class="lbl" font-size="7">tri</text>
  <text x="273" y="114" class="lbl" font-size="7">tri</text>
</g>

<g class="m" onclick="pick('glutes')">
  <ellipse cx="207" cy="206" rx="17" ry="15" fill="{c['glutes']}" {b['glutes']}/>
  <ellipse cx="243" cy="206" rx="17" ry="15" fill="{c['glutes']}" {b['glutes']}/>
  <text x="225" y="210" class="lbl">glutes</text>
</g>

<g class="m" onclick="pick('hamstrings')">
  <rect x="192" y="220" width="27" height="86" rx="11" fill="{c['hamstrings']}" {b['hamstrings']}/>
  <rect x="231" y="220" width="27" height="86" rx="11" fill="{c['hamstrings']}" {b['hamstrings']}/>
  <text x="225" y="266" class="lbl" font-size="8">hamstrings</text>
</g>

<g class="m" onclick="pick('calves')">
  <rect x="194" y="314" width="23" height="84" rx="9" fill="{c['calves']}" {b['calves']}/>
  <rect x="233" y="314" width="23" height="84" rx="9" fill="{c['calves']}" {b['calves']}/>
  <text x="225" y="358" class="lbl" font-size="8">calves</text>
</g>

</svg>
</body>
</html>"""


# ============================================================
# Page layout
# ============================================================

st.title("📚 Exercise Library")

col_body, col_list = st.columns([5, 6])

with col_body:
    components.html(_body_svg(), height=500, scrolling=False)

with col_list:
    if selected:
        exercises = exercises_db.search_exercises(muscle_group=selected)

        st.subheader(selected.title())
        st.caption(
            f"{len(exercises)} exercise{'s' if len(exercises) != 1 else ''}"
            " · click the same muscle region again to deselect"
        )
        st.write("")

        for ex in exercises:
            ex_id   = ex["exercise_id"]
            ex_type = ex["exercise_type"]
            sessions = usage.get(ex_id, 0)
            type_badge = "🔵 Compound" if ex_type == "compound" else "🟠 Isolation"

            with st.container(border=True):
                left, right = st.columns([4, 1])
                left.markdown(f"**{ex['exercise_name']}**")
                left.caption(type_badge)
                if sessions:
                    right.markdown(f"**{sessions}×**")
                    right.caption("logged")

    else:
        st.subheader("All muscle groups")
        st.caption("Click a region on the body diagram to see its exercises.")
        st.write("")

        all_exs = exercises_db.get_all_exercises()

        for group in exercises_db.get_muscle_groups():
            group_exs = [e for e in all_exs if e["muscle_group"] == group]
            logged    = sum(1 for e in group_exs if usage.get(e["exercise_id"], 0) > 0)
            total     = len(group_exs)

            left, right = st.columns([3, 2])
            left.markdown(f"**{group.title()}**")
            right.caption(
                f"{total} exercises" + (f"  ·  {logged} logged" if logged else "")
            )
