import sqlite3
import os

DB_NAME = 'gymchat_data.db'

def migrate():
    if not os.path.exists(DB_NAME):
        print(f"❌ Database file '{DB_NAME}' not found.")
        print("   Make sure you run this script from your gymchat folder.")
        return

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    print("🔍 Checking current database schema...\n")

    # --- Check users table ---
    c.execute("SELECT COUNT(*) FROM users")
    user_count = c.fetchone()[0]
    print(f"✅ Found {user_count} user(s) — will preserve all accounts.\n")

    # --- Fix exercise_executions table ---
    c.execute("PRAGMA table_info(exercise_executions)")
    columns = [row[1] for row in c.fetchall()]
    print(f"   exercise_executions columns: {columns}")

    needs_rebuild = False

    if 'exercise_id' not in columns:
        print("   ⚠️  Missing column: exercise_id")
        needs_rebuild = True
    if 'equipment_brand' not in columns:
        print("   ⚠️  Missing column: equipment_brand")
        needs_rebuild = True
    if 'equipment_model' not in columns:
        print("   ⚠️  Missing column: equipment_model")
        needs_rebuild = True

    if needs_rebuild:
        print("\n🔧 Rebuilding exercise_executions table...")

        # Save existing data
        c.execute("SELECT * FROM exercise_executions")
        existing_rows = c.fetchall()
        c.execute("PRAGMA table_info(exercise_executions)")
        old_cols = [row[1] for row in c.fetchall()]
        print(f"   Backing up {len(existing_rows)} existing row(s)...")

        # Drop and recreate
        c.execute("DROP TABLE exercise_executions")
        c.execute('''CREATE TABLE exercise_executions (
            execution_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            exercise_id INTEGER,
            equipment_brand TEXT,
            equipment_model TEXT,
            FOREIGN KEY (session_id) REFERENCES workout_sessions(session_id),
            FOREIGN KEY (exercise_id) REFERENCES exercises(exercise_id)
        )''')

        # Restore rows that have compatible data
        restored = 0
        for row in existing_rows:
            row_dict = dict(zip(old_cols, row))
            try:
                c.execute('''INSERT INTO exercise_executions 
                             (execution_id, session_id, exercise_id, equipment_brand, equipment_model)
                             VALUES (?, ?, ?, ?, ?)''', (
                    row_dict.get('execution_id'),
                    row_dict.get('session_id'),
                    row_dict.get('exercise_id'),        # may be None if old schema lacked it
                    row_dict.get('equipment_brand'),
                    row_dict.get('equipment_model')
                ))
                restored += 1
            except Exception as e:
                print(f"   ⚠️  Could not restore row {row_dict.get('execution_id')}: {e}")

        print(f"   ✅ exercise_executions rebuilt. {restored}/{len(existing_rows)} row(s) restored.")
    else:
        print("   ✅ exercise_executions schema is already correct.")

    # --- Fix sets table ---
    c.execute("PRAGMA table_info(sets)")
    set_cols = [row[1] for row in c.fetchall()]
    print(f"\n   sets columns: {set_cols}")

    if 'timestamp' not in set_cols:
        print("   ⚠️  Missing column: timestamp — adding it...")
        c.execute("ALTER TABLE sets ADD COLUMN timestamp TEXT")
        print("   ✅ Added timestamp column to sets.")
    else:
        print("   ✅ sets schema is correct.")

    # --- Ensure exercises table is populated ---
    c.execute("SELECT COUNT(*) FROM exercises")
    ex_count = c.fetchone()[0]
    print(f"\n   exercises table: {ex_count} exercises loaded.")
    if ex_count == 0:
        print("   ⚠️  No exercises found — they will be added when app starts.")

    conn.commit()
    conn.close()

    print("\n✅ Migration complete! You can now run:  streamlit run app.py")

if __name__ == '__main__':
    migrate()
