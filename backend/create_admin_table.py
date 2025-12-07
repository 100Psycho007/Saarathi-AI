"""
Create admin_users table in database
Run this once to set up the admin authentication system
"""
from db import engine, Base
from models import AdminUser

def create_admin_table():
    """Create the admin_users table"""
    print("Creating admin_users table...")
    Base.metadata.create_all(bind=engine, tables=[AdminUser.__table__])
    print("✓ Admin users table created successfully!")
    print("\nYou can now register admin users via the /api/auth/register endpoint")
    print("Make sure to set ADMIN_REGISTRATION_KEY in your .env file")

if __name__ == "__main__":
    create_admin_table()
