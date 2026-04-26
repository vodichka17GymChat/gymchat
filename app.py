import streamlit as st
import database as db
from datetime import datetime

# Page config
st.set_page_config(
    page_title="GymChat",
    page_icon="💪",
    layout="wide"
)

# Initialize database
db.init_database()
db.populate_exercises()

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'current_session' not in st.session_state:
    st.session_state.current_session = None
if 'current_execution' not in st.session_state:
    st.session_state.current_execution = None
if 'current_exercise_name' not in st.session_state:
    st.session_state.current_exercise_name = None
if 'set_counter' not in st.session_state:
    st.session_state.set_counter = 1
if 'exercise_order' not in st.session_state:
    st.session_state.exercise_order = 1

# App Header
st.title("💪 GymChat")
st.markdown("### Track Your Training Data")

# LOGIN/REGISTER SCREEN
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        st.subheader("Login to GymChat")
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                user = db.get_user(email, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user[0]
                    st.session_state.user_email = user[1]
                    st.success("✅ Logged in successfully!")
                    st.rerun()
                else:
                    st.error("❌ Invalid email or password")
    
    with tab2:
        st.subheader("Register for Study")
        st.info("📊 Join our gym training research study")
        
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                reg_email = st.text_input("Email*")
                reg_password = st.text_input("Password*", type="password")
                age = st.number_input("Age*", min_value=13, max_value=100, value=25)
                gender = st.selectbox("Gender*", ["Male", "Female", "Other", "Prefer not to say"])
            
            with col2:
                height = st.number_input("Height (cm)*", min_value=100.0, max_value=250.0, value=170.0)
                weight = st.number_input("Weight (kg)*", min_value=30.0, max_value=200.0, value=70.0)
                experience = st.number_input("Training Experience (months)*", min_value=0, max_value=600, value=12)
                fitness_level = st.selectbox("Fitness Level*", ["Beginner", "Intermediate", "Advanced"])
            
            goal = st.selectbox("Primary Goal*", 
                ["Strength", "Muscle Growth (Hypertrophy)", "General Fitness", "Powerlifting", "Weight Loss"])
            
            submit_reg = st.form_submit_button("Register")
            
            if submit_reg:
                if not reg_email or not reg_password:
                    st.error("❌ Email and password are required")
                else:
                    user_id = db.add_user(reg_email, reg_password, age, gender, height, weight, 
                                         experience, fitness_level, goal)
                    if user_id:
                        st.success("✅ Registration successful! Please login.")
                    else:
                        st.error("❌ Email already exists")

# MAIN APP - LOGGED IN
else:
    # Sidebar
    with st.sidebar:
        st.success(f"✅ Logged in as: {st.session_state.user_email}")
        st.write(f"**User ID:** {st.session_state.user_id}")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.user_email = None
            st.session_state.current_session = None
            st.session_state.current_execution = None
            st.session_state.set_counter = 1
            st.session_state.exercise_order = 1
            st.rerun()
        
        st.divider()
        
        if st.session_state.current_session:
            st.info(f"📝 **Active Workout**\nSession ID: {st.session_state.current_session}")
            if st.button("❌ End Workout", use_container_width=True):
                notes = st.text_area("Workout Notes (optional):", key="end_notes")
                if st.button("Confirm End Workout"):
                    db.end_session(st.session_state.current_session, notes)
                    st.session_state.current_session = None
                    st.session_state.current_execution = None
                    st.session_state.exercise_order = 1
                    st.success("✅ Workout ended!")
                    st.rerun()
    
    # MAIN CONTENT
    if st.session_state.current_session is None:
        # START NEW WORKOUT
        st.header("🏋️ Start New Workout")
        
        col1, col2 = st.columns(2)
        
        with col1:
            workout_type = st.selectbox("Workout Type*", 
                ["Push", "Pull", "Legs", "Upper Body", "Lower Body", "Full Body", 
                 "Chest", "Back", "Shoulders", "Arms", "Custom"])
            
        with col2:
            gym_location = st.text_input("Gym Location", placeholder="e.g., Gold's Gym Downtown")
        
        if st.button("▶️ Begin Workout", type="primary", use_container_width=True):
            session_id = db.create_session(st.session_state.user_id, workout_type, gym_location)
            st.session_state.current_session = session_id
            st.session_state.exercise_order = 1
            st.success(f"✅ Workout started! Session ID: {session_id}")
            st.rerun()
    
    else:
        # WORKOUT IN PROGRESS
        st.header(f"📝 Workout Session #{st.session_state.current_session}")
        
        if st.session_state.current_execution is None:
            # SELECT EXERCISE
            st.subheader("Add Exercise to Workout")
            
            exercises = db.get_exercises()
            
            # Group exercises by muscle group
            muscle_groups = {}
            for ex in exercises:
                muscle = ex[2]  # primary_muscle_group
                if muscle not in muscle_groups:
                    muscle_groups[muscle] = []
                muscle_groups[muscle].append(ex)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Filter by muscle group
                selected_muscle = st.selectbox("Filter by Muscle Group", 
                    ["All"] + sorted(list(muscle_groups.keys())))
                
                if selected_muscle == "All":
                    available_exercises = exercises
                else:
                    available_exercises = muscle_groups[selected_muscle]
                
                exercise_options = {f"{ex[1]} ({ex[2]} - {ex[3]})": ex[0] for ex in available_exercises}
                selected_exercise_name = st.selectbox("Select Exercise*", list(exercise_options.keys()))
                selected_exercise_id = exercise_options[selected_exercise_name]
            
            with col2:
                st.write("**Equipment Details** (optional)")
                brand = st.text_input("Brand", placeholder="e.g., Hammer Strength")
                model = st.text_input("Model", placeholder="e.g., ISO-Lateral Row")
            
            notes = st.text_area("Exercise Notes", placeholder="Any specific setup, grip, or execution details...")
            
            if st.button("➕ Add This Exercise", type="primary", use_container_width=True):
                execution_id = db.add_exercise_to_session(
                    st.session_state.current_session,
                    selected_exercise_id,
                    st.session_state.exercise_order,
                    brand,
                    model,
                    notes
                )
                st.session_state.current_execution = execution_id
                st.session_state.current_exercise_name = selected_exercise_name
                st.session_state.set_counter = 1
                st.success(f"✅ Added: {selected_exercise_name}")
                st.rerun()
        
        else:
            # LOG SETS
            st.subheader(f"🎯 {st.session_state.current_exercise_name}")
            st.caption(f"Execution ID: {st.session_state.current_execution}")
            
            # Show previous sets
            previous_sets = db.get_execution_sets(st.session_state.current_execution)
            
            if previous_sets:
                st.write("**Sets Completed:**")
                for s in previous_sets:
                    set_num = s[2]
                    weight = s[4]
                    reps = s[6]
                    rpe = s[7] if s[7] else "-"
                    rir = s[8] if s[8] else "-"
                    st.write(f"Set {set_num}: **{weight} kg × {reps} reps** | RPE: {rpe} | RIR: {rir}")
                st.divider()
            
            # Log new set
            st.write(f"**Log Set #{st.session_state.set_counter}**")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                weight = st.number_input("Weight (kg)*", min_value=0.0, max_value=500.0, value=20.0, step=2.5, key=f"weight_{st.session_state.set_counter}")
            
            with col2:
                reps = st.number_input("Reps*", min_value=1, max_value=100, value=10, key=f"reps_{st.session_state.set_counter}")
            
            with col3:
                rpe = st.number_input("RPE (1-10)", min_value=1, max_value=10, value=7, key=f"rpe_{st.session_state.set_counter}")
                st.caption("Rate of Perceived Exertion")
            
            with col4:
                rir = st.number_input("RIR (0-10)", min_value=0, max_value=10, value=3, key=f"rir_{st.session_state.set_counter}")
                st.caption("Reps in Reserve")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("✅ Complete Set", type="primary", use_container_width=True):
                    db.add_set(
                        st.session_state.current_execution,
                        st.session_state.set_counter,
                        weight,
                        reps,
                        rpe,
                        rir
                    )
                    st.session_state.set_counter += 1
                    st.success(f"✅ Set logged!")
                    st.rerun()
            
            with col_b:
                if st.button("✔️ Finish Exercise", use_container_width=True):
                    st.session_state.current_execution = None
                    st.session_state.current_exercise_name = None
                    st.session_state.set_counter = 1
                    st.session_state.exercise_order += 1
                    st.success("✅ Exercise completed!")
                    st.rerun()