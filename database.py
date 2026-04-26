import sqlite3
import datetime

DB_FILE = 'gymchat_data.db'

def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    return conn

def init_database():
    conn = get_connection()
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        age INTEGER,
        gender TEXT,
        height_cm REAL,
        weight_kg REAL,
        training_experience_months INTEGER,
        fitness_level TEXT,
        primary_goal TEXT
    )''')
    
    # Workout sessions
    c.execute('''CREATE TABLE IF NOT EXISTS workout_sessions (
        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        session_date DATE,
        start_time TIME,
        end_time TIME,
        workout_type TEXT,
        gym_location TEXT,
        session_notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )''')
    
    # Exercise master
    c.execute('''CREATE TABLE IF NOT EXISTS exercise_master (
        exercise_master_id INTEGER PRIMARY KEY AUTOINCREMENT,
        exercise_name TEXT NOT NULL,
        primary_muscle_group TEXT,
        equipment_category TEXT,
        exercise_type TEXT
    )''')
    
    # Exercise executions
    c.execute('''CREATE TABLE IF NOT EXISTS exercise_executions (
        execution_id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        exercise_master_id INTEGER,
        exercise_order INTEGER,
        equipment_brand TEXT,
        equipment_model TEXT,
        grip_type TEXT,
        execution_notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES workout_sessions(session_id),
        FOREIGN KEY (exercise_master_id) REFERENCES exercise_master(exercise_master_id)
    )''')
    
    # Sets table
    c.execute('''CREATE TABLE IF NOT EXISTS sets (
        set_id INTEGER PRIMARY KEY AUTOINCREMENT,
        execution_id INTEGER,
        set_number INTEGER,
        set_type TEXT DEFAULT 'working',
        weight_kg REAL,
        weight_unit TEXT DEFAULT 'kg',
        reps_completed INTEGER,
        rpe INTEGER,
        rir INTEGER,
        failure_reached BOOLEAN DEFAULT 0,
        set_notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (execution_id) REFERENCES exercise_executions(execution_id)
    )''')
    
    conn.commit()
    conn.close()

def populate_exercises():
    conn = get_connection()
    c = conn.cursor()
    
    exercises = [
        ('Barbell Bench Press', 'chest', 'barbell', 'compound'),
        ('Barbell Squat', 'quads', 'barbell', 'compound'),
        ('Barbell Deadlift', 'back', 'barbell', 'compound'),
        ('Barbell Row', 'back', 'barbell', 'compound'),
        ('Overhead Press', 'shoulders', 'barbell', 'compound'),
        ('Dumbbell Bench Press', 'chest', 'dumbbell', 'compound'),
        ('Incline Dumbbell Press', 'chest', 'dumbbell', 'compound'),
        ('Lat Pulldown', 'back', 'machine', 'compound'),
        ('Cable Row', 'back', 'cable', 'compound'),
        ('Leg Press', 'quads', 'machine', 'compound'),
        ('Leg Extension', 'quads', 'machine', 'isolation'),
        ('Leg Curl', 'hamstrings', 'machine', 'isolation'),
        ('Cable Fly', 'chest', 'cable', 'isolation'),
        ('Lateral Raise', 'shoulders', 'dumbbell', 'isolation'),
        ('Bicep Curl', 'biceps', 'dumbbell', 'isolation'),
        ('Tricep Pushdown', 'triceps', 'cable', 'isolation'),
        ('Face Pulls', 'back', 'cable', 'isolation'),
        ('Calf Raise', 'calves', 'machine', 'isolation'),
    ]
    
    for ex in exercises:
        try:
            c.execute('''INSERT INTO exercise_master 
                        (exercise_name, primary_muscle_group, equipment_category, exercise_type) 
                        VALUES (?, ?, ?, ?)''', ex)
        except:
            pass
    
    conn.commit()
    conn.close()

# User functions
def add_user(email, password, age, gender, height, weight, experience, fitness_level, goal):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO users 
                    (email, password_hash, age, gender, height_cm, weight_kg, 
                     training_experience_months, fitness_level, primary_goal) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (email, password, age, gender, height, weight, experience, fitness_level, goal))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return user_id
    except:
        conn.close()
        return None

def get_user(email, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email=? AND password_hash=?', (email, password))
    user = c.fetchone()
    conn.close()
    return user

def create_session(user_id, workout_type, gym_location):
    conn = get_connection()
    c = conn.cursor()
    now = datetime.datetime.now()
    c.execute('''INSERT INTO workout_sessions 
                (user_id, session_date, start_time, workout_type, gym_location)
                VALUES (?, ?, ?, ?, ?)''',
              (user_id, now.date(), now.time(), workout_type, gym_location))
    conn.commit()
    session_id = c.lastrowid
    conn.close()
    return session_id

def end_session(session_id, notes):
    conn = get_connection()
    c = conn.cursor()
    now = datetime.datetime.now()
    c.execute('UPDATE workout_sessions SET end_time=?, session_notes=? WHERE session_id=?',
              (now.time(), notes, session_id))
    conn.commit()
    conn.close()

def get_exercises():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM exercise_master ORDER BY primary_muscle_group, exercise_name')
    exercises = c.fetchall()
    conn.close()
    return exercises

def add_exercise_to_session(session_id, exercise_id, order, brand, model, notes):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO exercise_executions 
                (session_id, exercise_master_id, exercise_order, equipment_brand, equipment_model, execution_notes)
                VALUES (?, ?, ?, ?, ?, ?)''',
              (session_id, exercise_id, order, brand, model, notes))
    conn.commit()
    execution_id = c.lastrowid
    conn.close()
    return execution_id

def add_set(execution_id, set_num, weight, reps, rpe, rir):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO sets 
                (execution_id, set_number, weight_kg, reps_completed, rpe, rir)
                VALUES (?, ?, ?, ?, ?, ?)''',
              (execution_id, set_num, weight, reps, rpe, rir))
    conn.commit()
    conn.close()

def get_execution_sets(execution_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM sets WHERE execution_id=? ORDER BY set_number', (execution_id,))
    sets = c.fetchall()
    conn.close()
    return sets