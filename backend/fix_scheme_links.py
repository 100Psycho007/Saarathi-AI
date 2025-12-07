#!/usr/bin/env python3
"""
Fix official links for government schemes to ensure they work correctly
"""

import sqlite3
import os

# Updated working links for schemes
LINK_UPDATES = {
    # Karnataka Vidyasiri - the myscheme.gov.in link might be broken
    "Karnataka Vidyasiri Scholarship": "https://kea.kar.nic.in/",
    
    # Karnataka Bhagyalakshmi - update to working link
    "Karnataka Bhagyalakshmi Scheme": "https://dwcd.karnataka.gov.in/",
    
    # PM Ujjwala - update to official government link
    "Pradhan Mantri Ujjwala Yojana": "https://www.pmuy.gov.in/",
    
    # Karnataka Startup Policy - ensure correct link
    "Karnataka Startup Policy - Seed Fund": "https://www.karnataka.gov.in/startup",
    
    # Beti Bachao Beti Padhao - update to working link
    "Beti Bachao Beti Padhao": "https://www.india.gov.in/spotlight/beti-bachao-beti-padhao",
    
    # Mahila Shakti Kendra - more specific link
    "Mahila Shakti Kendra": "https://www.india.gov.in/spotlight/mahila-shakti-kendra",
    
    # Karnataka Sandhya Suraksha - update to working link
    "Karnataka Sandhya Suraksha Scheme": "https://www.karnataka.gov.in/socialwelfare",
    
    # Karnataka Disabled Persons Pension - update to working link
    "Karnataka Disabled Persons Pension Scheme": "https://www.karnataka.gov.in/socialwelfare",
}

def fix_scheme_links():
    """Update problematic scheme links in the database"""
    
    # Connect to database
    db_path = "ai_gov_schemes.db"
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Fixing scheme official links...")
    
    for scheme_name, new_link in LINK_UPDATES.items():
        try:
            cursor.execute(
                "UPDATE schemes SET official_link = ? WHERE name = ?",
                (new_link, scheme_name)
            )
            
            if cursor.rowcount > 0:
                print(f"✅ Updated: {scheme_name}")
            else:
                print(f"⚠️  Not found: {scheme_name}")
                
        except Exception as e:
            print(f"❌ Error updating {scheme_name}: {e}")
    
    # Commit changes
    conn.commit()
    
    # Verify updates
    print("\nVerifying updates...")
    for scheme_name in LINK_UPDATES.keys():
        cursor.execute(
            "SELECT official_link FROM schemes WHERE name = ?",
            (scheme_name,)
        )
        result = cursor.fetchone()
        if result:
            print(f"✅ {scheme_name}: {result[0]}")
    
    conn.close()
    print("\n🎉 Scheme links updated successfully!")

if __name__ == "__main__":
    fix_scheme_links()