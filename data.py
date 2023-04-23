import sqlite3
from datetime import datetime


conn = sqlite3.connect('Profile.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Cookie_Profile (
        id INTEGER PRIMARY KEY NOT NULL,
        created_at TEXT NOT NULL,
        cookie_values TEXT,
        last_launch TEXT,
        total_launches INTEGER
    );
''')


for i in range(15):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(f'''
        INSERT INTO Cookie_Profile (created_at, total_launches)
        VALUES ('{now}', 0);
    ''')


conn.commit()
conn.close()
