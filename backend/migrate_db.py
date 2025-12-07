"""
Database migration script to add new columns to existing tables.
Run this after updating models to add new fields.
"""

from sqlalchemy import text
from db import engine, SessionLocal


def migrate_database():
    """Add new columns to schemes and user_profiles tables if they don't exist."""
    
    db = SessionLocal()
    
    try:
        print("Starting database migration...")
        
        # Add columns to schemes table
        schemes_columns = [
            ("gender", "VARCHAR", "Any"),
            ("caste", "VARCHAR", "Any"),
            ("disability", "VARCHAR", "Any"),
            ("source", "VARCHAR", None),
            ("source_scheme_id", "VARCHAR", None),
            ("last_synced_at", "DATETIME", None),
        ]
        
        for col_name, col_type, default_value in schemes_columns:
            try:
                if default_value:
                    db.execute(text(f"""
                        ALTER TABLE schemes 
                        ADD COLUMN {col_name} {col_type} DEFAULT '{default_value}'
                    """))
                else:
                    db.execute(text(f"""
                        ALTER TABLE schemes 
                        ADD COLUMN {col_name} {col_type}
                    """))
                print(f"✓ Added column '{col_name}' to schemes table")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                    print(f"  Column '{col_name}' already exists in schemes table")
                else:
                    print(f"✗ Error adding column '{col_name}' to schemes: {e}")
        
        # Add index on source_scheme_id for faster lookups
        try:
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_schemes_source_scheme_id 
                ON schemes(source_scheme_id)
            """))
            print("✓ Created index on source_scheme_id")
        except Exception as e:
            print(f"  Index may already exist: {e}")
        
        # Add columns to user_profiles table
        user_columns = [
            ("caste", "VARCHAR", None),
            ("disability", "VARCHAR", None),
        ]
        
        for col_name, col_type, default_value in user_columns:
            try:
                if default_value:
                    db.execute(text(f"""
                        ALTER TABLE user_profiles 
                        ADD COLUMN {col_name} {col_type} DEFAULT '{default_value}'
                    """))
                else:
                    db.execute(text(f"""
                        ALTER TABLE user_profiles 
                        ADD COLUMN {col_name} {col_type}
                    """))
                print(f"✓ Added column '{col_name}' to user_profiles table")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                    print(f"  Column '{col_name}' already exists in user_profiles table")
                else:
                    print(f"✗ Error adding column '{col_name}' to user_profiles: {e}")
        
        db.commit()
        print("\n✓ Database migration completed successfully!")
        print("\nYou can now use the ingestion system:")
        print("  POST /admin/sync/myscheme?state=Karnataka")
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    migrate_database()
