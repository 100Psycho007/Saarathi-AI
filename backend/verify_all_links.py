#!/usr/bin/env python3
"""
Verify all scheme official links to ensure they're working
"""

import sqlite3
import requests
import time
from urllib.parse import urlparse

def verify_scheme_links():
    """Check all scheme links in the database"""
    
    # Connect to database
    conn = sqlite3.connect("ai_gov_schemes.db")
    cursor = conn.cursor()
    
    # Get all schemes with their links
    cursor.execute("SELECT name, official_link FROM schemes WHERE official_link IS NOT NULL")
    schemes = cursor.fetchall()
    
    print(f"Checking {len(schemes)} scheme links...\n")
    
    working_links = []
    broken_links = []
    
    for name, link in schemes:
        try:
            # Add a small delay to be respectful to servers
            time.sleep(0.5)
            
            # Make request with timeout
            response = requests.head(link, timeout=10, allow_redirects=True)
            
            if response.status_code < 400:
                print(f"✅ {name}: {link}")
                working_links.append((name, link))
            else:
                print(f"❌ {name}: {link} (Status: {response.status_code})")
                broken_links.append((name, link, response.status_code))
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️  {name}: {link} (Error: {str(e)[:50]}...)")
            broken_links.append((name, link, str(e)))
    
    conn.close()
    
    # Summary
    print(f"\n📊 SUMMARY:")
    print(f"✅ Working links: {len(working_links)}")
    print(f"❌ Broken links: {len(broken_links)}")
    
    if broken_links:
        print(f"\n🔧 BROKEN LINKS TO FIX:")
        for name, link, error in broken_links:
            print(f"- {name}: {link}")
    
    return working_links, broken_links

if __name__ == "__main__":
    verify_scheme_links()