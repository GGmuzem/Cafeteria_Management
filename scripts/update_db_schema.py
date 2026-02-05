
import sqlite3
import os

# Path to database
db_path = os.path.join('src', 'database', 'cafeteria.db')
print(f"Checking database at {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get table info
    cursor.execute("PRAGMA table_info(user)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Existing columns: {columns}")

    # Check and add columns
    if 'email' not in columns:
        print("Adding email column...")
        cursor.execute("ALTER TABLE user ADD COLUMN email VARCHAR(120)")
    
    if 'allergen' not in columns:
        print("Adding allergen column...")
        cursor.execute("ALTER TABLE user ADD COLUMN allergen VARCHAR(255)")
        
    if 'preferences' not in columns:
        print("Adding preferences column...")
        cursor.execute("ALTER TABLE user ADD COLUMN preferences VARCHAR(255)")

    conn.commit()
    conn.close()
    print("Database updated successfully.")

except Exception as e:
    print(f"Error: {e}")
