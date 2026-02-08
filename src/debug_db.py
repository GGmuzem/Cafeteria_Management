from app import app, db
# Ensure all models are imported so they are registered with SQLAlchemy
from database.users import User
from database.wallets import Wallet
from database.history import History
from database.menu import Menu
from database.store import Storage
from database.reviews import Reviews
from database.requests import Requests

with app.app_context():
    print("Tables in SQLAlchemy metadata:")
    for table_name in db.metadata.tables:
        print(f"- {table_name}")
    
    print("\nAttempting to create all tables...")
    db.create_all()
    
    print("\nTables in database after create_all (via introspection):")
    # We need to reflect to see what is practically in the DB, 
    # but create_all uses metadata. 
    # Let's inspect the engine directly.
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    for table_name in inspector.get_table_names():
        print(f"- {table_name}")
