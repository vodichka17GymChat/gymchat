"""
Library page - explore exercises by muscle group.

The user clicks a muscle on the body diagram (or its label below it) and
the right-hand column refills with cards for the exercises that train
that muscle. Each card shows the name + type and expands inline to
reveal a short "how to do it" tip.

Selection is mirrored to the URL query param ``?muscle=...`` so the
page is deep-linkable and survives a refresh. The body_diagram
component returns just the click; the page owns the selection.
"""

import html

import streamlit as st

from components.body_diagram import MUSCLE_GROUPS, render as render_body_diagram
from components.theme import inject_theme
from db import exercises as exercises_db


inject_theme()


# ============================================================
# Auth gate
# ============================================================

if st.session_state.get("user_id") is None:
    st.warning("Please log in from the home page first.")
    st.stop()


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:
    st.write(f"Signed in as **{st.session_state.user_email}**")


# ============================================================
# Static content
# ============================================================
#
# A short blurb per muscle group + a "how to do it" tip per exercise.
# Kept inline because they're only consumed here. Keys in
# EXERCISE_INSTRUCTIONS must match exercise_name in the DB exactly.

MUSCLE_BLURBS: dict[str, str] = {
    "chest": (
        "The chest (pectoralis major and minor) drives all horizontal pushing - "
        "bench presses, pushups, flyes. Train with both heavy compounds and at "
        "least one isolation movement for full development."
    ),
    "back": (
        "Back covers a large group: lats, traps, rhomboids, erectors. Build it "
        "with vertical pulls (pulldowns, pull-ups), horizontal pulls (rows), "
        "and the deadlift for total-body posterior loading."
    ),
    "shoulders": (
        "The deltoid has three heads: front, side, and rear. The overhead press "
        "hits all three; lateral raises target the side head; rear-delt work "
        "catches the part rows often miss."
    ),
    "biceps": (
        "Biceps flex the elbow and supinate the forearm. They get worked on "
        "every back day, but direct curls in different grips (supinated, "
        "neutral, narrow) are how you actually put size on them."
    ),
    "triceps": (
        "Triceps make up roughly two-thirds of upper-arm size. Press-style "
        "movements (close-grip bench, dips) load the long head heavy, while "
        "pushdowns and overhead extensions isolate the muscle."
    ),
    "quads": (
        "The quadriceps are the four front-of-thigh muscles that extend the "
        "knee. Squat patterns are king; leg presses, split squats, and "
        "extensions all add useful volume."
    ),
    "hamstrings": (
        "Hamstrings flex the knee and extend the hip. Train both functions - "
        "hinges (RDLs, good mornings) for hip extension and curls (leg curl, "
        "Nordic) for knee flexion."
    ),
    "glutes": (
        "The glutes are the most powerful hip extensors in your body. Hip "
        "thrusts and bridges are the highest-tension direct lift; squats and "
        "deadlifts cover them as a side-effect of heavy loading."
    ),
    "calves": (
        "The calf has two muscles: the gastrocnemius (knee straight) and the "
        "soleus (knee bent). Train with both standing AND seated raises for "
        "full coverage. Slow tempo - calves are tendon-heavy."
    ),
    "core": (
        "Core means more than just abs - it's the entire trunk that stabilises "
        "the spine. Mix anti-extension (planks, leg raises), anti-rotation "
        "(Pallof presses), and crunching patterns."
    ),
}


EXERCISE_INSTRUCTIONS: dict[str, str] = {
    # Chest
    "Barbell Bench Press": (
        "Lie flat on a bench with feet planted, retract your shoulder blades, "
        "and lower the bar under control to mid-chest. Press straight up while "
        "keeping your wrists stacked over your elbows."
    ),
    "Dumbbell Bench Press": (
        "Same motion as the barbell press but with independent dumbbells, "
        "allowing a deeper stretch at the bottom and a more shoulder-friendly "
        "press path."
    ),
    "Incline Barbell Bench Press": (
        "Bench at about 30 degrees. Lower the bar to your upper chest with "
        "elbows tucked at ~70 degrees from the torso. Targets the upper pec."
    ),
    "Incline Dumbbell Press": (
        "Dumbbell version of the incline press - friendlier on the shoulders "
        "and lets each arm work independently. Don't crash the dumbbells "
        "together at the top."
    ),
    "Decline Bench Press": (
        "Bench tilted head-down 15-30 degrees. Lower to the lower chest, pause "
        "briefly, and press up. Emphasises the lower pec."
    ),
    "Chest Fly Machine": (
        "Sit upright, grip the handles, and bring them together in front of "
        "your chest with arms only slightly bent. Squeeze and pause at peak "
        "contraction."
    ),
    "Cable Chest Fly": (
        "Stand between two cable stacks at chest height. Step forward, draw "
        "the handles together in front of your body, control the eccentric "
        "to keep tension on the chest the whole time."
    ),
    "Dumbbell Fly": (
        "Lie flat with dumbbells over your chest. Lower in a wide arc with a "
        "soft elbow bend until you feel a stretch, then bring back together "
        "by squeezing the chest."
    ),
    "Push-ups": (
        "Body in a rigid plank, hands just outside shoulder width. Lower until "
        "your chest nearly touches the floor, then press back up. Keep glutes "
        "and core tight throughout."
    ),

    # Back
    "Barbell Row": (
        "Hinge forward to about 45 degrees with a neutral spine. Pull the bar "
        "to your lower ribs and drive your elbows back. Don't let the lower "
        "back round."
    ),
    "Dumbbell Row": (
        "One knee and one hand on a bench, torso parallel to the floor. Pull "
        "the dumbbell from a hanging position toward your hip, squeeze the "
        "lat, and lower with control."
    ),
    "Lat Pulldown": (
        "Sit tall with a slight backward lean. Pull the bar to your upper "
        "chest by driving the elbows down and back. Don't shrug as you pull."
    ),
    "Pull-ups": (
        "Hang from the bar with palms facing away. Pull until your chin clears "
        "the bar by leading with your chest and squeezing the shoulder blades."
    ),
    "Chin-ups": (
        "Same motion as pull-ups but with palms facing you (supinated grip). "
        "Heavier biceps involvement and usually a touch easier than pull-ups."
    ),
    "Seated Cable Row": (
        "Sit upright at the row station. Pull the handle to your sternum or "
        "lower ribs and control the return without rounding the back."
    ),
    "T-Bar Row": (
        "Straddle the bar, hinge forward with chest tall, and pull toward your "
        "lower chest. Allows heavier loads than the dumbbell row."
    ),
    "Deadlift": (
        "Bar over mid-foot. Brace hard, hinge to grip, pull the slack out of "
        "the bar, then drive through the floor and lock out by squeezing the "
        "glutes - not by hyperextending the back."
    ),
    "Face Pulls": (
        "Cable rope set at face height. Pull the rope apart toward your face "
        "with elbows kept high. Excellent for rear delts, traps, and overall "
        "shoulder health."
    ),

    # Shoulders
    "Overhead Press": (
        "Standing or seated, press the bar from the front rack to fully "
        "overhead. Brace the core and squeeze the glutes; avoid leaning back "
        "excessively."
    ),
    "Dumbbell Shoulder Press": (
        "Press dumbbells from shoulder height to overhead. Allows a more "
        "natural press path than the barbell and works each side "
        "independently."
    ),
    "Lateral Raises": (
        "Hold dumbbells at your sides, raise out to the side with a slight "
        "elbow bend until your arms are parallel to the floor. Lead with the "
        "elbows, don't shrug."
    ),
    "Front Raises": (
        "Raise the dumbbells in front of you to shoulder height, then lower "
        "under control. Targets the anterior delt."
    ),
    "Rear Delt Fly": (
        "Bent over with a flat back, raise dumbbells out to the side leading "
        "with the elbows. Or use a reverse pec-deck. Targets the often-"
        "neglected rear delts."
    ),
    "Arnold Press": (
        "Start with palms facing you at chest height. Rotate the dumbbells "
        "out as you press up. Hits all three deltoid heads in one rep."
    ),
    "Cable Lateral Raise": (
        "Single-arm cable lateral with the cable from a low pulley behind "
        "you. Provides constant tension throughout the range, especially in "
        "the bottom half where dumbbells go light."
    ),

    # Biceps
    "Barbell Curl": (
        "Stand tall with the bar at thigh-level. Curl up by flexing the "
        "elbows while keeping them pinned at your sides; control the lowering."
    ),
    "Dumbbell Curl": (
        "Same motion with independent dumbbells. Rotate (supinate) the wrist "
        "as you curl for full biceps activation."
    ),
    "Hammer Curl": (
        "Curl with a neutral grip (thumbs up). Targets the brachialis and "
        "brachioradialis as well as the biceps - great for thickening the arm."
    ),
    "Preacher Curl": (
        "Forearms supported on the preacher pad, curl from full extension. "
        "Removes momentum and isolates the biceps, especially the lower "
        "portion."
    ),
    "Cable Curl": (
        "Curl from a low-pulley cable with a bar or rope. Constant tension "
        "throughout the range, especially at the top."
    ),
    "Concentration Curl": (
        "Seated, elbow braced against the inner thigh. Curl one dumbbell at "
        "a time. Maximum biceps isolation - squeeze hard at the top."
    ),

    # Triceps
    "Tricep Pushdown": (
        "Cable bar or rope at chest height. Lock elbows at your sides and "
        "push down by extending only the elbows."
    ),
    "Overhead Tricep Extension": (
        "Hold a dumbbell or rope behind your head, extend up by straightening "
        "the elbows. The overhead position stretches the long head."
    ),
    "Skull Crushers": (
        "Lying on a bench with an EZ-bar held over your chest. Lower toward "
        "your forehead by bending only the elbows, then extend back up."
    ),
    "Close Grip Bench Press": (
        "Bench press with hands about shoulder-width apart and elbows tucked "
        "close to the body. Heavier triceps involvement than the regular "
        "bench press."
    ),
    "Dips": (
        "Suspend on parallel bars. Lower until your shoulders are slightly "
        "below the elbows, then press back up. Stay vertical for triceps; "
        "lean forward for chest emphasis."
    ),

    # Quads
    "Barbell Squat": (
        "Bar on the upper back. Brace, descend by sitting back and down until "
        "thighs are parallel or below, then drive up through mid-foot."
    ),
    "Front Squat": (
        "Bar racked across the front delts. More upright torso than back "
        "squat - heavier quad emphasis. Demands wrist mobility and a strong "
        "upper back."
    ),
    "Leg Press": (
        "Sit in the machine with feet shoulder-width on the platform. Lower "
        "with control until knees hit ~90 degrees, press back up without "
        "locking out hard."
    ),
    "Leg Extension": (
        "Seated machine, ankles behind the pad. Extend the knees fully "
        "against the resistance. Pure quad isolation."
    ),
    "Bulgarian Split Squat": (
        "Rear foot elevated on a bench. Lunge down on the front leg until "
        "the back knee nearly touches the floor, then drive up through the "
        "front foot."
    ),
    "Hack Squat": (
        "Machine squat with the back supported on a sliding pad. Allows heavy "
        "loading with less spine demand than a barbell squat."
    ),

    # Hamstrings
    "Romanian Deadlift": (
        "Stand with the bar at thigh-level. Hip-hinge by pushing your hips "
        "back while keeping a slight knee bend. Stop when you feel a deep "
        "hamstring stretch, then drive your hips forward."
    ),
    "Leg Curl": (
        "Seated or lying machine. Curl your heels toward your glutes against "
        "the pad. Pause and squeeze at the top of each rep."
    ),
    "Good Mornings": (
        "Bar on the upper back. Hip-hinge forward keeping a slight knee bend, "
        "then return by driving the hips forward. Use light loads - form is "
        "everything here."
    ),
    "Nordic Curls": (
        "Kneel with feet anchored. Slowly lower your torso forward by "
        "extending the knees, then pull back up using the hamstrings. Brutal "
        "eccentric - use a band or push-off assistance to start."
    ),

    # Glutes
    "Hip Thrust": (
        "Upper back on a bench, bar across the hips (use a pad). Drive the "
        "hips up to a flat-line lockout and squeeze the glutes hard at the "
        "top."
    ),
    "Glute Bridge": (
        "Floor version of the hip thrust. Lie on your back with knees bent, "
        "drive hips up by squeezing glutes. Good warm-up or activation drill."
    ),
    "Cable Kickbacks": (
        "Cable strap around one ankle, support yourself on a frame. Kick the "
        "leg straight back, leading with the heel. Squeeze the glute at "
        "end-range."
    ),

    # Calves
    "Standing Calf Raise": (
        "Stand under the machine pad or hold dumbbells. Rise onto the balls "
        "of your feet, pause at the top, lower under full control. Knee "
        "straight = gastrocnemius emphasis."
    ),
    "Seated Calf Raise": (
        "Seated machine, knees under the pad. The bent knee biases the soleus "
        "over the gastrocnemius. Use slow tempo and a full stretch at the "
        "bottom."
    ),

    # Core
    "Plank": (
        "Forearms on the floor, body in a rigid line from head to heels. "
        "Brace abs and squeeze glutes; don't let the hips sag or pike up."
    ),
    "Crunches": (
        "Lying on your back, knees bent. Lift only your shoulder blades off "
        "the floor by contracting the abs. Don't pull on your neck."
    ),
    "Russian Twists": (
        "Seated with knees bent and feet up. Rotate the torso side to side "
        "holding a weight. Move from the obliques, not from flailing arms."
    ),
    "Leg Raises": (
        "Lying on your back or hanging from a bar. Raise straight legs to "
        "around 90 degrees while keeping the lower back pressed down or the "
        "spine stable. Lower under control."
    ),
    "Cable Crunches": (
        "Kneel facing a cable stack with the rope behind your head. Crunch "
        "down by flexing the spine. The heaviest direct ab loading you can "
        "do."
    ),
}


# ============================================================
# Page-local CSS - chip strip + exercise card grid
# ============================================================

_PAGE_CSS = """
<style>
.gc-selection-strip {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    margin: 0.3rem 0 1rem;
    flex-wrap: wrap;
}
.gc-selection-label {
    font-size: 0.78rem;
    color: var(--text-muted);
    font-weight: 500;
}
.gc-chip-empty {
    background: rgba(107, 122, 144, 0.10);
    color: var(--text-muted);
    border: 1px solid rgba(107, 122, 144, 0.20);
    display: inline-block;
    padding: 0.18rem 0.6rem;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
}

.gc-muscle-blurb {
    font-size: 0.86rem;
    color: var(--text);
    line-height: 1.55;
    margin: 0 0 0.85rem;
}

.gc-exercise-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
    gap: 0.65rem;
}
.gc-exercise-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    box-shadow: 0 1px 6px var(--shadow);
    overflow: hidden;
    transition: box-shadow 0.18s ease, border-color 0.18s ease;
}
.gc-exercise-card:hover {
    box-shadow: 0 2px 14px var(--shadow);
}
.gc-exercise-card[open] {
    border-color: var(--accent);
}
.gc-exercise-card summary {
    cursor: pointer;
    list-style: none;
    padding: 0.7rem 0.85rem;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
}
.gc-exercise-card summary::-webkit-details-marker { display: none; }
.gc-exercise-card summary::marker { content: ""; }
.gc-exercise-card[open] summary {
    border-bottom: 1px solid var(--border);
}
.gc-exercise-name {
    font-weight: 600;
    font-size: 0.92rem;
    color: var(--text);
    line-height: 1.3;
    font-family: 'Inter', sans-serif;
}
.gc-exercise-desc {
    margin: 0;
    padding: 0.7rem 0.85rem;
    color: var(--text);
    font-size: 0.85rem;
    line-height: 1.55;
    font-family: 'Inter', sans-serif;
}
</style>
"""

st.markdown(_PAGE_CSS, unsafe_allow_html=True)


# ============================================================
# Selection state - URL is the source of truth so the page is
# deep-linkable and survives a refresh.
# ============================================================

raw = st.query_params.get("muscle")
selected_muscle: str | None = raw if raw in MUSCLE_GROUPS else None


# ============================================================
# Header + selection chip
# ============================================================

st.title("Exercise Library")
st.caption("Click a muscle on the body to explore the exercises that train it.")

if selected_muscle is None:
    chip_html = '<span class="gc-chip-empty">No muscle selected</span>'
else:
    chip_html = f'<span class="gc-chip gc-chip-blue">{selected_muscle.title()}</span>'

st.markdown(
    f'<div class="gc-selection-strip">'
    f'<span class="gc-selection-label">Selected:</span>{chip_html}'
    f'</div>',
    unsafe_allow_html=True,
)


# ============================================================
# Two-column layout: body diagram | exercise grid
# ============================================================

col_body, col_cards = st.columns([2, 3], gap="medium")

with col_body:
    clicked = render_body_diagram(selected_muscle)
    if clicked is not None:
        # Click the same muscle again to clear the selection.
        if clicked == selected_muscle:
            del st.query_params["muscle"]
        else:
            st.query_params["muscle"] = clicked
        st.rerun()

with col_cards:
    if selected_muscle is None:
        st.info("Select a muscle group to see its exercises.")
    else:
        blurb = MUSCLE_BLURBS.get(selected_muscle)
        if blurb:
            st.markdown(
                f'<p class="gc-muscle-blurb">{html.escape(blurb)}</p>',
                unsafe_allow_html=True,
            )

        rows = exercises_db.search_exercises(muscle_group=selected_muscle)
        if not rows:
            st.info("No exercises catalogued for this muscle yet.")
        else:
            cards = []
            for ex in rows:
                name = html.escape(ex["exercise_name"])
                ex_type = ex["exercise_type"]
                chip_class = (
                    "gc-chip-blue" if ex_type == "compound" else "gc-chip-green"
                )
                tip = EXERCISE_INSTRUCTIONS.get(
                    ex["exercise_name"], "No description yet."
                )
                cards.append(
                    f'<details class="gc-exercise-card">'
                    f'<summary>'
                    f'<span class="gc-exercise-name">{name}</span>'
                    f'<span class="gc-chip {chip_class}">{ex_type.title()}</span>'
                    f'</summary>'
                    f'<p class="gc-exercise-desc">{html.escape(tip)}</p>'
                    f'</details>'
                )
            st.markdown(
                f'<div class="gc-exercise-grid">{"".join(cards)}</div>',
                unsafe_allow_html=True,
            )
