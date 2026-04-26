import streamlit as st
import pandas as pd
from database import Database
from datetime import datetime

# Initialize database
db = Database()

# Page config
st.set_page_config(page_title="GymChat", page_icon="💪", layout="wide")

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'active_session' not in st.session_state:
    st.session_state.active_session = None
if 'current_execution' not in st.session_state:
    st.session_state.current_execution = None

# Title
st.title("💪 GymChat - Workout Tracker")

# Login/Register System
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login"):
            user = db.verify_user(email, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.success("✅ Logged in successfully!")
                st.rerun()
            else:
                st.error("❌ Invalid email or password")
    
    with tab2:
        st.subheader("Register New User")
        
        col1, col2 = st.columns(2)
        
        with col1:
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            age = st.number_input("Age", min_value=13, max_value=100, value=25, step=1)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            
        with col2:
            height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170, step=1)
            weight = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0, value=70.0, step=0.5, format="%.1f")
            experience = st.number_input("Training Experience (months)", min_value=0, max_value=600, value=0, step=1)
            fitness_level = st.selectbox("Fitness Level", 
                                        ["Beginner", "Intermediate", "Advanced", "Elite"])
        
        goal = st.selectbox("Primary Goal", 
                           ["Muscle Growth (Hypertrophy)", 
                            "Strength", 
                            "Endurance", 
                            "Weight Loss", 
                            "General Fitness"])
        
        if st.button("Register"):
            if reg_email and reg_password:
                try:
                    db.create_user(reg_email, reg_password, age, gender, 
                                 height, weight, experience, fitness_level, goal)
                    st.success("✅ Registration successful! Please login.")
                except Exception as e:
                    st.error(f"❌ Registration failed: {str(e)}")
            else:
                st.error("❌ Please fill in email and password")

# Main App (after login)
else:
    # Sidebar
    with st.sidebar:
        st.write(f"👤 User ID: {st.session_state.user_id}")
        
        if st.session_state.active_session:
            st.write(f"🏋️ Active Session: {st.session_state.active_session}")
            if st.button("❌ End Workout"):
                st.session_state.show_end_workout = True
        
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.active_session = None
            st.session_state.current_execution = None
            st.rerun()
    
    # End workout dialog
    if st.session_state.get('show_end_workout', False):
        st.subheader("End Workout")
        notes = st.text_area("Workout Notes (optional)")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✔️ Confirm End Workout"):
                db.end_session(st.session_state.active_session, notes)
                st.session_state.active_session = None
                st.session_state.current_execution = None
                st.session_state.show_end_workout = False
                st.success("✅ Workout ended!")
                st.rerun()
        with col2:
            if st.button("Cancel"):
                st.session_state.show_end_workout = False
                st.rerun()
    
    # No active session - Start workout
    elif not st.session_state.active_session:
        st.subheader("Start New Workout")
        
        col1, col2 = st.columns(2)
        with col1:
            workout_type = st.selectbox("Workout Type", 
                                       ["Push", "Pull", "Legs", "Upper", "Lower", "Full Body", "Other"])
        with col2:
            gym_location = st.text_input("Gym Location (optional)")
        
        if st.button("▶️ Begin Workout"):
            session_id = db.create_session(st.session_state.user_id, workout_type, gym_location)
            st.session_state.active_session = session_id
            st.success(f"✅ Workout started! Session ID: {session_id}")
            st.rerun()
    
    # Active session - no current exercise
    elif not st.session_state.current_execution:
        st.subheader("Add Exercise")
        
        # Exercise selection
        exercises = db.get_exercises()
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            muscle_filter = st.selectbox("Filter by Muscle Group", 
                                        ["All"] + sorted(list(set([e[2] for e in exercises]))))
        with col2:
            type_filter = st.selectbox("Filter by Type", 
                                      ["All", "compound", "isolation"])
        
        # Apply filters
        filtered_exercises = exercises
        if muscle_filter != "All":
            filtered_exercises = [e for e in filtered_exercises if e[2] == muscle_filter]
        if type_filter != "All":
            filtered_exercises = [e for e in filtered_exercises if e[3] == type_filter]
        
        # Create display names
        exercise_options = [f"{e[1]} ({e[2]} - {e[3]})" for e in filtered_exercises]
        
        selected_exercise = st.selectbox("Select Exercise", exercise_options)
        
        # Get exercise_id from selection
        selected_idx = exercise_options.index(selected_exercise)
        exercise_id = filtered_exercises[selected_idx][0]
        
        # Optional fields
        col1, col2 = st.columns(2)
        with col1:
            brand = st.text_input("Equipment Brand (optional)")
        with col2:
            model = st.text_input("Equipment Model (optional)")
        
        if st.button("➕ Add This Exercise"):
            execution_id = db.add_exercise_execution(
                st.session_state.active_session, 
                exercise_id, 
                brand if brand else None, 
                model if model else None
            )
            st.session_state.current_execution = execution_id
            st.success(f"✅ Exercise added! Execution ID: {execution_id}")
            st.rerun()
    
    # Active exercise - Log sets
    else:
        # Get current exercise info
        execution_info = db.get_execution_info(st.session_state.current_execution)
        st.subheader(f"🏋️ {execution_info['exercise_name']}")
        st.caption(f"{execution_info['muscle_group']} - {execution_info['exercise_type']}")
        
        # Show previous sets
        sets = db.get_sets(st.session_state.current_execution)
        if sets:
            st.write("### Previous Sets")
            sets_df = pd.DataFrame(sets, columns=['Set', 'Time', 'Weight (kg)', 'Reps', 'RPE', 'RIR'])
            st.dataframe(sets_df, use_container_width=True)
        
        # Log new set
        st.write("### Log New Set")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            weight = st.number_input("Weight (kg)", min_value=0.0, max_value=500.0, value=20.0, step=2.5, format="%.1f")
        with col2:
            reps = st.number_input("Reps", min_value=1, max_value=100, value=10, step=1)
        with col3:
            rpe = st.number_input("RPE (1-10)", min_value=1, max_value=10, value=7, step=1)
        with col4:
            rir = st.number_input("RIR (0-10)", min_value=0, max_value=10, value=3, step=1)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Complete Set"):
                set_number = len(sets) + 1
                db.add_set(st.session_state.current_execution, set_number, weight, reps, rpe, rir)
                st.success(f"✅ Set {set_number} logged!")
                st.rerun()
        
        with col2:
            if st.button("✔️ Finish Exercise"):
                st.session_state.current_execution = None
                st.success("✅ Exercise completed!")
                st.rerun()