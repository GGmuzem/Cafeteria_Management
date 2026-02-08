
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from app import create_db, app
from database.users import User

print("Running create_db...")
try:
    create_db()
    print("create_db finished.")
except Exception as e:
    print(f"Error in create_db: {e}")
    import traceback
    traceback.print_exc()

with app.app_context():
    admin = User.query.filter_by(login="admin").first()
    if admin:
        print(f"Admin found: {admin.login}, Role: {admin.role}")
    else:
        print("Admin NOT found.")
