import sqlite3
import os

db_path = os.path.abspath("database/health.db")
print(f"Checking database at: {db_path}")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM predictions")
    count = cursor.fetchone()[0]
    print(f"Number of records in 'predictions' table: {count}")
    
    if count > 0:
        cursor.execute("SELECT * FROM predictions")
        for row in cursor.fetchall():
            print(f"Data found: {row}")
    else:
        print("Table is empty. Make sure you run the API POST request first!")
    conn.close()
else:
    print("Database file does not exist at this location.")