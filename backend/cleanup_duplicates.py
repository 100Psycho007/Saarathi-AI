"""
Utility script to find and remove duplicate schemes from the database.
Run this anytime you suspect duplicate schemes have been added.

Usage:
    python cleanup_duplicates.py
"""
from db import SessionLocal
from models import Scheme
from collections import defaultdict

def cleanup_duplicates():
    """Find and remove duplicate schemes, keeping the first occurrence."""
    db = SessionLocal()
    
    try:
        # Get all schemes ordered by ID
        schemes = db.query(Scheme).order_by(Scheme.id).all()
        
        # Group by name
        schemes_by_name = defaultdict(list)
        for scheme in schemes:
            schemes_by_name[scheme.name].append(scheme)
        
        # Find and remove duplicates
        duplicates_removed = 0
        
        for name, scheme_list in schemes_by_name.items():
            if len(scheme_list) > 1:
                print(f"\n❌ Found {len(scheme_list)} copies of '{name}'")
                print(f"   Keeping: ID={scheme_list[0].id}")
                
                # Delete all but the first one
                for scheme in scheme_list[1:]:
                    print(f"   Deleting: ID={scheme.id}")
                    db.delete(scheme)
                    duplicates_removed += 1
        
        if duplicates_removed > 0:
            db.commit()
            print(f"\n✅ Removed {duplicates_removed} duplicate schemes")
        else:
            print("\n✅ No duplicates found")
        
        # Show final count
        remaining = db.query(Scheme).count()
        print(f"\nTotal schemes in database: {remaining}")
        
    finally:
        db.close()

if __name__ == "__main__":
    print("="*80)
    print("DUPLICATE SCHEME CLEANUP UTILITY")
    print("="*80)
    cleanup_duplicates()
