#!/usr/bin/env python3
"""
Test script for the ingestion system.
Run this to verify the ingestion layer works correctly.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from ingestion.myscheme_ingestor import load_mock_myscheme_data
from ingestion.merge import upsert_schemes_from_source
from db import SessionLocal
from models import Scheme


def test_load_mock_data():
    """Test loading mock data from JSON files"""
    print("Testing mock data loading...")
    
    states = ["Karnataka", "Maharashtra", "Central"]
    for state in states:
        data = load_mock_myscheme_data(state)
        print(f"  {state}: {len(data)} schemes loaded")
        if data:
            print(f"    Sample: {data[0]['name']}")
    print()


def test_upsert():
    """Test upserting schemes into database"""
    print("Testing upsert functionality...")
    
    db = SessionLocal()
    try:
        # Load Karnataka data
        data = load_mock_myscheme_data("Karnataka")
        print(f"  Loaded {len(data)} Karnataka schemes")
        
        # First upsert (should insert)
        result1 = upsert_schemes_from_source(db, data, source="myscheme")
        print(f"  First sync: inserted={result1['inserted']}, updated={result1['updated']}")
        
        # Second upsert (should update)
        result2 = upsert_schemes_from_source(db, data, source="myscheme")
        print(f"  Second sync: inserted={result2['inserted']}, updated={result2['updated']}")
        
        # Verify in database
        count = db.query(Scheme).filter(Scheme.source == "myscheme").count()
        print(f"  Total myscheme schemes in DB: {count}")
        
        # Show sample scheme
        sample = db.query(Scheme).filter(Scheme.source == "myscheme").first()
        if sample:
            print(f"  Sample scheme: {sample.name} (ID: {sample.source_scheme_id})")
            print(f"    Last synced: {sample.last_synced_at}")
        
    finally:
        db.close()
    print()


def test_all_states():
    """Sync all available states"""
    print("Syncing all states...")
    
    db = SessionLocal()
    try:
        states = ["Karnataka", "Maharashtra", "Central"]
        total_inserted = 0
        total_updated = 0
        
        for state in states:
            data = load_mock_myscheme_data(state)
            if data:
                result = upsert_schemes_from_source(db, data, source="myscheme")
                print(f"  {state}: inserted={result['inserted']}, updated={result['updated']}")
                total_inserted += result['inserted']
                total_updated += result['updated']
        
        print(f"\nTotal: inserted={total_inserted}, updated={total_updated}")
        
        # Final count
        total_schemes = db.query(Scheme).count()
        myscheme_count = db.query(Scheme).filter(Scheme.source == "myscheme").count()
        print(f"Database totals: {total_schemes} schemes ({myscheme_count} from myscheme)")
        
    finally:
        db.close()
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("Ingestion System Test")
    print("=" * 60)
    print()
    
    try:
        test_load_mock_data()
        test_upsert()
        test_all_states()
        
        print("=" * 60)
        print("All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
