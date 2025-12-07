#!/usr/bin/env python3
"""
Fix scheme links with PRECISE matching - each scheme gets its EXACT official portal
"""

import sqlite3
import os

# PRECISE SCHEME-TO-LINK MAPPING - Each scheme gets its exact official portal
PRECISE_SCHEME_LINKS = {
    # STUDENT SCHOLARSHIPS - All go to National Scholarship Portal (correct)
    "National Scholarship for Higher Education": "https://scholarships.gov.in/",
    "Post Matric Scholarship for SC Students": "https://scholarships.gov.in/",
    "Post Matric Scholarship for ST Students": "https://scholarships.gov.in/",
    "Post Matric Scholarship for OBC Students": "https://scholarships.gov.in/",
    "Pre-Matric Scholarship for SC/ST Students": "https://scholarships.gov.in/",
    "National Means-cum-Merit Scholarship": "https://scholarships.gov.in/",
    "Post-Matric Scholarship for SC/ST Students": "https://scholarships.gov.in/",
    
    # KARNATAKA SPECIFIC SCHOLARSHIPS - Use Karnataka education portal
    "Karnataka Vidyasiri Scholarship": "https://scholarships.gov.in/",  # Available on NSP
    "Karnataka State Post-Matric Scholarship": "https://scholarships.gov.in/",  # Available on NSP
    "Karnataka Post-Matric Scholarship": "https://scholarships.gov.in/",  # Available on NSP
    
    # FARMER SCHEMES - Each gets its specific portal
    "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)": "https://pmkisan.gov.in/",
    "PM Fasal Bima Yojana (Crop Insurance)": "https://pmfby.gov.in/",
    "Kisan Credit Card (KCC)": "https://www.india.gov.in/spotlight/kisan-credit-card-kcc",
    "Karnataka Farmer Welfare Scheme - Equipment Subsidy": "https://raitamitra.karnataka.gov.in/",
    "Karnataka Farmer Equipment Subsidy": "https://raitamitra.karnataka.gov.in/",
    "Raitha Samparka Kendras Support": "https://raitamitra.karnataka.gov.in/",
    
    # WOMEN & CHILD SCHEMES - Each gets its specific ministry portal
    "Pradhan Mantri Matru Vandana Yojana (PMMVY)": "https://pmmvy.wcd.gov.in/",
    "Beti Bachao Beti Padhao": "https://wcd.nic.in/bbbp-schemes",
    "Mahila Shakti Kendra": "https://wcd.nic.in/",
    "Karnataka Bhagyalakshmi Scheme": "https://dwcd.karnataka.gov.in/",
    "Bhagyalakshmi Scheme": "https://dwcd.karnataka.gov.in/",
    "Ladli Scheme": "https://wcddel.in/ladli.html",
    
    # ENTREPRENEUR SCHEMES - Each gets its specific portal
    "Pradhan Mantri Mudra Yojana (PMMY)": "https://www.mudra.org.in/",
    "Stand Up India Scheme": "https://www.standupmitra.in/",
    "Stand Up India Scheme for Women Entrepreneurs": "https://www.standupmitra.in/",
    "Startup India Seed Fund Scheme": "https://www.startupindia.gov.in/",
    "Karnataka Startup Policy - Seed Fund": "https://www.startupindia.gov.in/",
    "Karnataka Women Entrepreneur Scheme": "https://www.startupindia.gov.in/",
    
    # ELDERLY & PENSION SCHEMES - NSAP portal for central schemes
    "Indira Gandhi National Old Age Pension Scheme": "https://nsap.nic.in/",
    "Pradhan Mantri Vaya Vandana Yojana": "https://licindia.in/",
    "Karnataka Sandhya Suraksha Scheme": "https://ahinda.karnataka.gov.in/",
    
    # DISABILITY SCHEMES - Disability Affairs Ministry
    "Indira Gandhi National Disability Pension Scheme": "https://nsap.nic.in/",
    "Deendayal Disabled Rehabilitation Scheme": "https://disabilityaffairs.gov.in/",
    "Assistance to Disabled Persons for Purchase of Aids and Appliances (ADIP)": "https://disabilityaffairs.gov.in/",
    "Karnataka Disabled Persons Pension Scheme": "https://ahinda.karnataka.gov.in/",
    
    # HEALTH SCHEMES - Health ministry portals
    "Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana (PM-JAY)": "https://pmjay.gov.in/",
    
    # HOUSING SCHEMES - Housing ministry portals
    "Pradhan Mantri Awas Yojana (PMAY) - Urban": "https://pmaymis.gov.in/",
    
    # WELFARE SCHEMES - Specific ministry portals
    "Pradhan Mantri Ujjwala Yojana": "https://www.pmuy.gov.in/",
    "National Rural Employment Guarantee Act (NREGA/MGNREGA)": "https://nrega.nic.in/",
    "Pradhan Mantri Kaushal Vikas Yojana (PMKVY)": "https://www.pmkvyofficial.org/",
    
    # STATE SPECIFIC SCHEMES - Use appropriate state portals
    "Maharashtra EBC Scholarship": "https://mahadbt.maharashtra.gov.in/",
    "Maharashtra Shetkari Sanman Yojana": "https://mahadbt.maharashtra.gov.in/",
    "Chief Minister's Breakfast Scheme": "https://www.tn.gov.in/",
    "Free Electricity for Farmers": "https://www.tangedco.gov.in/",
    "Delhi Scholarship Scheme": "https://www.delhi.gov.in/",
}

def fix_precise_scheme_links():
    """Update scheme links with PRECISE matching to correct official portals"""
    
    # Connect to database
    db_path = "ai_gov_schemes.db"
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🎯 Fixing scheme links with PRECISE official portal matching...")
    print("=" * 70)
    
    updated_count = 0
    not_found_count = 0
    
    for scheme_name, correct_link in PRECISE_SCHEME_LINKS.items():
        try:
            cursor.execute(
                "UPDATE schemes SET official_link = ? WHERE name = ?",
                (correct_link, scheme_name)
            )
            
            if cursor.rowcount > 0:
                print(f"✅ {scheme_name}")
                print(f"   🔗 {correct_link}")
                updated_count += 1
            else:
                print(f"⚠️  Not found in DB: {scheme_name}")
                not_found_count += 1
                
        except Exception as e:
            print(f"❌ Error updating {scheme_name}: {e}")
    
    # Commit changes
    conn.commit()
    
    print("=" * 70)
    print(f"📊 SUMMARY:")
    print(f"✅ Updated with precise links: {updated_count} schemes")
    print(f"⚠️  Not found in database: {not_found_count} schemes")
    
    # Show schemes that might need manual review
    print(f"\n🔍 Checking for schemes without specific links...")
    cursor.execute("""
        SELECT name, official_link 
        FROM schemes 
        WHERE name NOT IN ({})
        AND official_link IS NOT NULL
        ORDER BY name
    """.format(','.join(['?' for _ in PRECISE_SCHEME_LINKS.keys()])), 
    list(PRECISE_SCHEME_LINKS.keys()))
    
    unmatched_schemes = cursor.fetchall()
    
    if unmatched_schemes:
        print(f"\n⚠️  SCHEMES THAT NEED REVIEW ({len(unmatched_schemes)}):")
        print("-" * 50)
        for name, link in unmatched_schemes:
            print(f"📋 {name}")
            print(f"   🔗 {link}")
            print()
    
    conn.close()
    print("🎉 PRECISE SCHEME LINK MAPPING COMPLETE!")

if __name__ == "__main__":
    fix_precise_scheme_links()