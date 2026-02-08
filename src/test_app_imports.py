from app import app, db
# Do NOT import models here manually. 
# We want to verify that app.py imports them.

with app.app_context():
    print("Tables in metadata (from app imports):")
    existing_tables = set(db.metadata.tables.keys())
    expected_tables = {'user', 'wallet', 'history', 'menu', 'storage', 'reviews', 'requests'}
    
    for table_name in existing_tables:
        print(f"- {table_name}")
        
    missing = expected_tables - existing_tables
    if missing:
        print(f"\nMISSING TABLES: {missing}")
        exit(1)
    else:
        print("\nAll expected tables are present in metadata.")
