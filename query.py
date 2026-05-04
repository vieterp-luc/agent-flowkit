import sqlite3
import json
conn = sqlite3.connect('flow_agent.db')
with open('query_output.txt', 'w', encoding='utf-8') as f:
    f.write("ERRORS: " + str(conn.execute("SELECT type, status, error_message FROM request WHERE status='FAILED' LIMIT 20").fetchall()) + "\n")
