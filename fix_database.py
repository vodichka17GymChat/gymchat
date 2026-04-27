import sqlite3

conn = sqlite3.connect('gymchat_data.db')
c = conn.cursor()

# Check if the column exists
c.execute("PRAGMA table_info(exercise_executions)")
columns = [column[1] for column in c.fetchall()]

if 'exercise_id' not in columns:
    print("Fixing exercise_executions table...")
    
    # Create new table with correct schema
    c.execute('''CREATE TABLE IF NOT EXISTS exercise_executions_new (
        execution_id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        exercise_id INTEGER,
        equipment_brand TEXT,
        equipment_model TEXT,
        FOREIGN KEY (session_id) REFERENCES workout_sessions(session_id),
        FOREIGN KEY (exercise_id) REFERENCES exercises(exercise_id)
    )''')
    
    # Copy data if old table had any
    try:
        c.execute('''INSERT INTO exercise_executions_new 
                     SELECT * FROM exercise_executions''')
    except:
        pass
    
    # Drop old table and rename new one
    c.execute('DROP TABLE IF EXISTS exercise_executions')
    c.execute('ALTER TABLE exercise_executions_new RENAME TO exercise_executions')
    
    conn.commit()
    print("✅ Database fixed!")
else:
    print("✅ Database is already correct!")

conn.close()