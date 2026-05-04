import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'flow_agent.db')
print(f"Connecting to {db_path}")
try:
    conn = sqlite3.connect(db_path)
    conn.execute("ALTER TABLE project ADD COLUMN orientation TEXT DEFAULT 'HORIZONTAL' CHECK(orientation IN ('VERTICAL','HORIZONTAL'));")
    conn.commit()
    conn.close()
    print("Success")
except Exception as e:
    print(f"Error: {e}")
