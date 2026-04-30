"""
Body diagram component - a stylised front-view human body with every
seeded muscle group represented as a clickable region.

Click handling
--------------
The SVG itself is purely visual. The actual click targets are the row
of ``st.button`` widgets rendered beneath it. We don't make the SVG
paths clickable because:

- ``st.markdown(unsafe_allow_html=True)`` strips ``onclick`` from inline
  HTML, so any JS click handler we'd add gets removed.
- A bare ``<a href="?muscle=...">`` does a real browser navigation,
  which re-opens the WebSocket session and wipes ``st.session_state``
  (including ``user_id``). The user gets logged out on every click.
- A ``components.v1.html`` iframe with ``window.parent.postMessage``
  needs the Streamlit component bridge JS, which is only injected for
  components declared via ``declare_component`` - that needs a build
  step the project doesn't have.

The button fallback is reliable, accessible, and uses native Streamlit
state. The SVG mirrors the current selection by colouring the matching
region in the accent shade, so the body stays the focal point.

Component contract
------------------
``render(selected_muscle)`` takes the currently-selected muscle name
(used to highlight the corresponding region) and returns whichever
muscle the user clicked on this run, or ``None`` if no click happened.
The caller decides what to do with that click (typically: persist it
in ``st.query_params`` and rerun).

Front-view caveats
------------------
A strict front view doesn't actually show back, triceps, glutes, or
hamstrings. Rather than drop those four groups (and their exercises)
from the library, we place each as a labelled clickable region in the
most plausible front-visible position:

    back        - trapezius band sitting above the chest, between neck
                  and shoulders (traps do show from the front)
    triceps     - thin lateral strip on the outer edge of each upper arm
    glutes      - small bump on the lateral hip
    hamstrings  - thin lateral strip down the outer edge of each thigh

The button grid below the SVG is the canonical click surface, so even
if a user can't pinpoint the lateral hamstring strip on the body, the
"Hamstrings" button is right there.
"""

import streamlit as st


MUSCLE_GROUPS: tuple[str, ...] = (
    "chest", "back", "shoulders", "biceps", "triceps",
    "quads", "hamstrings", "glutes", "calves", "core",
)

# Layout for the picker buttons - five rows of two, ordered roughly
# top-to-bottom along the body so the grid mirrors the diagram.
_BUTTON_PAIRS: tuple[tuple[str, str], ...] = (
    ("shoulders", "back"),
    ("chest",     "biceps"),
    ("triceps",   "core"),
    ("glutes",    "quads"),
    ("hamstrings", "calves"),
)


_CSS = """
<style>
.gc-body-diagram {
    display: flex;
    justify-content: center;
    margin: 0.25rem 0 0.9rem;
}
.gc-body-diagram svg {
    width: 100%;
    max-width: 230px;
    height: auto;
    display: block;
}
.gc-body-silhouette {
    fill: rgba(255, 255, 255, 0.55);
    stroke: rgba(61, 169, 252, 0.4);
    stroke-width: 1.2;
    stroke-linejoin: round;
}
.gc-muscle {
    fill: rgba(61, 169, 252, 0.22);
    stroke: rgba(27, 110, 204, 0.55);
    stroke-width: 1;
    transition: fill 0.18s ease, stroke 0.18s ease;
}
.gc-muscle.selected {
    fill: #1B6ECC;
    stroke: #0F4F94;
}
</style>
"""


def _cls(muscle: str, selected: str | None) -> str:
    return "gc-muscle selected" if muscle == selected else "gc-muscle"


def _svg(selected: str | None) -> str:
    """Build the front-view SVG with `selected` highlighted."""
    s = lambda m: _cls(m, selected)  # noqa: E731 - tiny local alias

    return f"""
<svg viewBox="0 0 200 500" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Front body view">
  <!-- ── Silhouette ───────────────────────────────────────── -->
  <ellipse class="gc-body-silhouette" cx="100" cy="42" rx="22" ry="27"/>
  <path class="gc-body-silhouette" d="M 88 65 L 112 65 L 116 82 L 84 82 Z"/>
  <path class="gc-body-silhouette" d="M 70 82 L 130 82 L 154 100 L 152 230 L 128 250 L 72 250 L 48 230 L 46 100 Z"/>
  <path class="gc-body-silhouette" d="M 46 100 L 30 110 L 26 245 L 36 252 L 48 248 L 50 110 Z"/>
  <path class="gc-body-silhouette" d="M 154 100 L 170 110 L 174 245 L 164 252 L 152 248 L 150 110 Z"/>
  <path class="gc-body-silhouette" d="M 72 250 L 100 250 L 100 485 L 76 485 Z"/>
  <path class="gc-body-silhouette" d="M 100 250 L 128 250 L 124 485 L 100 485 Z"/>

  <!-- ── Back (trapezius region, visible from front) ──────── -->
  <path class="{s('back')}" d="M 80 84 L 120 84 L 132 100 L 68 100 Z"/>

  <!-- ── Shoulders (front delts) ──────────────────────────── -->
  <ellipse class="{s('shoulders')}" cx="58" cy="108" rx="13" ry="9"/>
  <ellipse class="{s('shoulders')}" cx="142" cy="108" rx="13" ry="9"/>

  <!-- ── Chest ────────────────────────────────────────────── -->
  <path class="{s('chest')}" d="M 76 102 Q 100 94 124 102 L 126 142 Q 100 154 74 142 Z"/>

  <!-- ── Triceps (lateral strip on upper arm) ─────────────── -->
  <ellipse class="{s('triceps')}" cx="32" cy="160" rx="5" ry="22"/>
  <ellipse class="{s('triceps')}" cx="168" cy="160" rx="5" ry="22"/>

  <!-- ── Biceps (medial upper arm) ────────────────────────── -->
  <ellipse class="{s('biceps')}" cx="46" cy="160" rx="9" ry="24"/>
  <ellipse class="{s('biceps')}" cx="154" cy="160" rx="9" ry="24"/>

  <!-- ── Core ─────────────────────────────────────────────── -->
  <path class="{s('core')}" d="M 84 152 Q 100 148 116 152 L 116 226 Q 100 236 84 226 Z"/>

  <!-- ── Glutes (lateral hip bumps) ───────────────────────── -->
  <ellipse class="{s('glutes')}" cx="62" cy="246" rx="7" ry="9"/>
  <ellipse class="{s('glutes')}" cx="138" cy="246" rx="7" ry="9"/>

  <!-- ── Hamstrings (lateral thigh strip) ─────────────────── -->
  <ellipse class="{s('hamstrings')}" cx="74" cy="330" rx="4" ry="48"/>
  <ellipse class="{s('hamstrings')}" cx="126" cy="330" rx="4" ry="48"/>

  <!-- ── Quads (front of thigh) ───────────────────────────── -->
  <ellipse class="{s('quads')}" cx="86" cy="330" rx="12" ry="58"/>
  <ellipse class="{s('quads')}" cx="114" cy="330" rx="12" ry="58"/>

  <!-- ── Calves (front of lower leg) ──────────────────────── -->
  <ellipse class="{s('calves')}" cx="86" cy="430" rx="11" ry="32"/>
  <ellipse class="{s('calves')}" cx="114" cy="430" rx="11" ry="32"/>
</svg>
""".strip()


def _diagram_html(selected: str | None) -> str:
    return _CSS + f'<div class="gc-body-diagram">{_svg(selected)}</div>'


def render(selected_muscle: str | None) -> str | None:
    """
    Render the body diagram and the muscle-picker button grid.

    Args:
        selected_muscle: The currently-selected muscle (used to highlight
            the matching region in the SVG and the matching button). Pass
            ``None`` if nothing is selected.

    Returns:
        The muscle the user clicked on this rerun (one of MUSCLE_GROUPS),
        or ``None`` if no button was clicked. The caller is responsible
        for persisting the new selection (e.g. via ``st.query_params``)
        and triggering a rerun.
    """
    st.markdown(_diagram_html(selected_muscle), unsafe_allow_html=True)

    clicked: str | None = None
    for left, right in _BUTTON_PAIRS:
        c1, c2 = st.columns(2)
        for col, muscle in ((c1, left), (c2, right)):
            with col:
                if st.button(
                    muscle.title(),
                    key=f"bd_{muscle}",
                    use_container_width=True,
                    type="primary" if muscle == selected_muscle else "secondary",
                ):
                    clicked = muscle
    return clicked
