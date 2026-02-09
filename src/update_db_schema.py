from config import app, db
from sqlalchemy import text

def update_schema():
    with app.app_context():
        try:
            # Check if column exists (this is a bit hacky for SQLite but works)
            # Or just try to add it and catch error
            with db.engine.connect() as conn:
                try:
                    conn.execute(text("ALTER TABLE requests ADD COLUMN price_per_unit INTEGER"))
                    print("Column 'price_per_unit' added to 'requests' successfully.")
                except Exception as e:
                    print(f"Requests update error (likely exists): {e}")

                try:
                    conn.execute(text("ALTER TABLE storage ADD COLUMN price_per_unit INTEGER NOT NULL DEFAULT 0"))
                    print("Column 'price_per_unit' added to 'storage' successfully.")
                except Exception as e:
                    print(f"Storage update error (likely exists): {e}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    update_schema()
