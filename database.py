import sqlite3
from datetime import datetime
import hashlib

class Database:
    def __init__(self, db_name='gymchat_data.db'):
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_db(self):
        conn = self.get_connection()
        c = conn.cursor()
        
        # Users table
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            height_cm REAL,
            weight_kg REAL,
            training_experience_months INTEGER,
            fitness_level TEXT,
            primary_goal TEXT,
            created_at TEXT
        )''')
        
        # Exercises table
        c.execute('''CREATE TABLE IF NOT EXISTS exercises (
            exercise_id INTEGER PRIMARY KEY AUTOINCREMENT,
            exercise_name TEXT UNIQUE NOT NULL,
            muscle_group TEXT,
            exercise_type TEXT
        )''')
        
        # Workout sessions table
        c.execute('''CREATE TABLE IF NOT EXISTS workout_sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            workout_type TEXT,
            gym_location TEXT,
            start_time TEXT,
            end_time TEXT,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )''')
        
        # Exercise executions table
        c.execute('''CREATE TABLE IF NOT EXISTS exercise_executions (
            execution_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            exercise_id INTEGER,
            equipment_brand TEXT,
            equipment_model TEXT,
            FOREIGN KEY (session_id) REFERENCES workout_sessions(session_id),
            FOREIGN KEY (exercise_id) REFERENCES exercises(exercise_id)
        )''')
        
        # Sets table
        c.execute('''CREATE TABLE IF NOT EXISTS sets (
            set_id INTEGER PRIMARY KEY AUTOINCREMENT,
            execution_id INTEGER,
            set_number INTEGER,
            timestamp TEXT,
            weight_kg REAL,
            reps INTEGER,
            rpe INTEGER,
            rir INTEGER,
            FOREIGN KEY (execution_id) REFERENCES exercise_executions(execution_id)
        )''')
        
        conn.commit()
        
        # Populate exercises if empty
        c.execute('SELECT COUNT(*) FROM exercises')
        if c.fetchone()[0] == 0:
            self.populate_exercises()
        
        conn.close()
    
    def populate_exercises(self):
        exercises = [
            # Chest
            ('Barbell Bench Press', 'chest', 'compound'),
            ('Dumbbell Bench Press', 'chest', 'compound'),
            ('Incline Barbell Bench Press', 'chest', 'compound'),
            ('Incline Dumbbell Press', 'chest', 'compound'),
            ('Decline Bench Press', 'chest', 'compound'),
            ('Chest Fly Machine', 'chest', 'isolation'),
            ('Cable Chest Fly', 'chest', 'isolation'),
            ('Dumbbell Fly', 'chest', 'isolation'),
            ('Push-ups', 'chest', 'compound'),
            
            # Back
            ('Barbell Row', 'back', 'compound'),
            ('Dumbbell Row', 'back', 'compound'),
            ('Lat Pulldown', 'back', 'compound'),
            ('Pull-ups', 'back', 'compound'),
            ('Chin-ups', 'back', 'compound'),
            ('Seated Cable Row', 'back', 'compound'),
            ('T-Bar Row', 'back', 'compound'),
            ('Deadlift', 'back', 'compound'),
            ('Face Pulls', 'back', 'isolation'),
            
            # Shoulders
            ('Overhead Press', 'shoulders', 'compound'),
            ('Dumbbell Shoulder Press', 'shoulders', 'compound'),
            ('Lateral Raises', 'shoulders', 'isolation'),
            ('Front Raises', 'shoulders', 'isolation'),
            ('Rear Delt Fly', 'shoulders', 'isolation'),
            ('Arnold Press', 'shoulders', 'compound'),
            ('Cable Lateral Raise', 'shoulders', 'isolation'),
            
            # Arms - Biceps
            ('Barbell Curl', 'biceps', 'isolation'),
            ('Dumbbell Curl', 'biceps', 'isolation'),
            ('Hammer Curl', 'biceps', 'isolation'),
            ('Preacher Curl', 'biceps', 'isolation'),
            ('Cable Curl', 'biceps', 'isolation'),
            ('Concentration Curl', 'biceps', 'isolation'),
            
            # Arms - Triceps
            ('Tricep Pushdown', 'triceps', 'isolation'),
            ('Overhead Tricep Extension', 'triceps', 'isolation'),
            ('Skull Crushers', 'triceps', 'isolation'),
            ('Close Grip Bench Press', 'triceps', 'compound'),
            ('Dips', 'triceps', 'compound'),
            
            # Legs - Quads
            ('Barbell Squat', 'quads', 'compound'),
            ('Front Squat', 'quads', 'compound'),
            ('Leg Press', 'quads', 'compound'),
            ('Leg Extension', 'quads', 'isolation'),
            ('Bulgarian Split Squat', 'quads', 'compound'),
            ('Hack Squat', 'quads', 'compound'),
            
            # Legs - Hamstrings
            ('Romanian Deadlift', 'hamstrings', 'compound'),
            ('Leg Curl', 'hamstrings', 'isolation'),
            ('Good Mornings', 'hamstrings', 'compound'),
            ('Nordic Curls', 'hamstrings', 'isolation'),
            
            # Legs - Glutes
            ('Hip Thrust', 'glutes', 'isolation'),
            ('Glute Bridge', 'glutes', 'isolation'),
            ('Cable Kickbacks', 'glutes', 'isolation'),
            
            # Legs - Calves
            ('Standing Calf Raise', 'calves', 'isolation'),
            ('Seated Calf Raise', 'calves', 'isolation'),
            
            # Core
            ('Plank', 'core', 'isolation'),
            ('Crunches', 'core', 'isolation'),
            ('Russian Twists', 'core', 'isolation'),
            ('Leg Raises', 'core', 'isolation'),
            ('Cable Crunches', 'core', 'isolation'),
        ]
        
        conn = self.get_connection()
        c = conn.cursor()
        c.executemany('INSERT INTO exercises (exercise_name, muscle_group, exercise_type) VALUES (?, ?, ?)', exercises)
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, email, password, age, gender, height_cm, weight_kg, 
                    training_experience_months, fitness_level, primary_goal):
        conn = self.get_connection()
        c = conn.cursor()
        
        password_hash = self.hash_password(password)
        
        c.execute('''INSERT INTO users 
                     (email, password_hash, age, gender, height_cm, weight_kg, 
                      training_experience_months, fitness_level, primary_goal, created_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (email, password_hash, age, gender, height_cm, weight_kg, 
                   training_experience_months, fitness_level, primary_goal, 
                   datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def verify_user(self, email, password):
        conn = self.get_connection()
        c = conn.cursor()
        
        password_hash = self.hash_password(password)
        
        c.execute('SELECT user_id FROM users WHERE email = ? AND password_hash = ?',
                  (email, password_hash))
        
        user = c.fetchone()
        conn.close()
        return user
    
    def create_session(self, user_id, workout_type, gym_location=None):
        conn = self.get_connection()
        c = conn.cursor()
        
        # Handle empty string as None
        if gym_location == "":
            gym_location = None
        
        c.execute('''INSERT INTO workout_sessions 
                     (user_id, workout_type, gym_location, start_time)
                     VALUES (?, ?, ?, ?)''',
                  (user_id, workout_type, gym_location, datetime.now().isoformat()))
        
        session_id = c.lastrowid
        conn.commit()
        conn.close()
        return session_id
    
    def end_session(self, session_id, notes=None):
        conn = self.get_connection()
        c = conn.cursor()
        
        # Handle empty string as None
        if notes == "":
            notes = None
        
        c.execute('''UPDATE workout_sessions 
                     SET end_time = ?, notes = ?
                     WHERE session_id = ?''',
                  (datetime.now().isoformat(), notes, session_id))
        
        conn.commit()
        conn.close()
    
    def get_exercises(self):
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute('SELECT exercise_id, exercise_name, muscle_group, exercise_type FROM exercises ORDER BY exercise_name')
        
        exercises = c.fetchall()
        conn.close()
        return exercises
    
    def add_exercise_execution(self, session_id, exercise_id, equipment_brand=None, equipment_model=None):
        conn = self.get_connection()
        c = conn.cursor()
        
        # Handle empty strings as None
        if equipment_brand == "":
            equipment_brand = None
        if equipment_model == "":
            equipment_model = None
        
        c.execute('''INSERT INTO exercise_executions 
                     (session_id, exercise_id, equipment_brand, equipment_model)
                     VALUES (?, ?, ?, ?)''',
                  (session_id, exercise_id, equipment_brand, equipment_model))
        
        execution_id = c.lastrowid
        conn.commit()
        conn.close()
        return execution_id
    
    def add_set(self, execution_id, set_number, weight_kg, reps, rpe=None, rir=None):
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute('''INSERT INTO sets 
                     (execution_id, set_number, timestamp, weight_kg, reps, rpe, rir)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (execution_id, set_number, datetime.now().isoformat(), 
                   weight_kg, reps, rpe, rir))
        
        conn.commit()
        conn.close()
    
    def get_sets(self, execution_id):
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute('''SELECT set_number, timestamp, weight_kg, reps, rpe, rir 
                     FROM sets 
                     WHERE execution_id = ? 
                     ORDER BY set_number''',
                  (execution_id,))
        
        sets = c.fetchall()
        conn.close()
        return sets
    
    def get_execution_info(self, execution_id):
        conn = self.get_connection()
        c = conn.cursor()
        
        c.execute('''SELECT e.exercise_name, e.muscle_group, e.exercise_type,
                            ex.equipment_brand, ex.equipment_model
                     FROM exercise_executions ex
                     JOIN exercises e ON ex.exercise_id = e.exercise_id
                     WHERE ex.execution_id = ?''',
                  (execution_id,))
        
        result = c.fetchone()
        conn.close()
        
        if result:
            return {
                'exercise_name': result[0],
                'muscle_group': result[1],
                'exercise_type': result[2],
                'equipment_brand': result[3],
                'equipment_model': result[4]
            }
        return None