import sqlite3
import json
conn = sqlite3.connect('flow_agent.db')
conn.execute("UPDATE request SET status='PENDING' WHERE type='GENERATE_IMAGE' AND status='FAILED' AND error_message LIKE '%waiting for reference images%'")
conn.commit()
conn.execute("UPDATE scene SET horizontal_image_status='PENDING' WHERE horizontal_image_status='FAILED'")
conn.execute("UPDATE scene SET vertical_image_status='PENDING' WHERE vertical_image_status='FAILED'")
conn.commit()
