from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from db import get_db
from models import Scheme
from schemas import SchemeRead

router = APIRouter(tags=["schemes"])


@router.get("/schemes/", response_model=List[SchemeRead])
def get_all_schemes(db: Session = Depends(get_db)):
    """Get all schemes from the database."""
    schemes = db.query(Scheme).all()
    return schemes


@router.post("/schemes/update-links")
def update_scheme_links(db: Session = Depends(get_db)):
    """Update official links for existing schemes."""
    
    updates = {
        "Karnataka Vidyasiri Scholarship": "https://www.myscheme.gov.in/schemes/vidyasiri",
        "Karnataka State Post-Matric Scholarship": "https://www.myscheme.gov.in/schemes/kpms",
        "National Scholarship for Higher Education": "https://scholarships.gov.in/",
        "Karnataka Farmer Welfare Scheme - Equipment Subsidy": "https://raitamitra.karnataka.gov.in/",
        "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)": "https://pmkisan.gov.in/"
    }
    
    updated_count = 0
    for scheme_name, new_link in updates.items():
        scheme = db.query(Scheme).filter(Scheme.name == scheme_name).first()
        if scheme:
            scheme.official_link = new_link
            updated_count += 1
    
    db.commit()
    return {"updated": updated_count, "message": f"Updated {updated_count} scheme links"}


@router.post("/schemes/seed-demo-data")
def seed_demo_data(db: Session = Depends(get_db)):
    """Insert comprehensive schemes into the database if they don't already exist."""
    from comprehensive_schemes_seed import COMPREHENSIVE_SCHEMES
    
    inserted_count = 0
    updated_count = 0
    
    for scheme_data in COMPREHENSIVE_SCHEMES:
        # Check if scheme already exists by name
        existing = db.query(Scheme).filter(Scheme.name == scheme_data["name"]).first()
        if not existing:
            scheme = Scheme(**scheme_data)
            db.add(scheme)
            inserted_count += 1
        else:
            # Update existing scheme with new fields
            for key, value in scheme_data.items():
                setattr(existing, key, value)
            updated_count += 1
    
    db.commit()
    
    return {
        "inserted": inserted_count,
        "updated": updated_count,
        "total_schemes": len(COMPREHENSIVE_SCHEMES),
        "message": f"Inserted {inserted_count} new schemes, updated {updated_count} existing schemes"
    }
