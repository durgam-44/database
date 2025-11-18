import sqlite3

DB_PATH = "users.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE attendance ADD COLUMN paid INTEGER DEFAULT 0;")
    conn.commit()
    print("Column 'paid' added successfully!")
except Exception as e:
    print("Error:", e)

conn.close()