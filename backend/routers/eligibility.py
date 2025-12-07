from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict
from db import get_db
from models import Scheme
from schemas import UserProfileCreate, SchemeRead
from services.eligibility_service import check_eligibility

router = APIRouter(tags=["eligibility"])


@router.post("/eligibility/check")
def check_user_eligibility(profile: UserProfileCreate, db: Session = Depends(get_db)):
    """
    Check eligibility for all relevant schemes based on user profile.
    
    Returns schemes categorized as eligible or ineligible with reasons.
    """
    
    # Fetch schemes matching user's state or Central schemes
    schemes = db.query(Scheme).filter(
        (Scheme.state == profile.state) | (Scheme.state == "Central")
    ).all()
    
    eligible_schemes = []
    ineligible_schemes = []
    
    for scheme in schemes:
        # Check eligibility for each scheme
        eligibility_result = check_eligibility(profile, scheme)
        
        # Convert scheme to dict for response
        scheme_dict = {
            "id": scheme.id,
            "name": scheme.name,
            "short_description": scheme.short_description,
            "full_description": scheme.full_description,
            "category": scheme.category,
            "state": scheme.state,
            "min_age": scheme.min_age,
            "max_age": scheme.max_age,
            "max_income": scheme.max_income,
            "occupation": scheme.occupation,
            "official_link": scheme.official_link,
            "application_process": scheme.application_process
        }
        
        if eligibility_result["eligible"]:
            eligible_schemes.append(scheme_dict)
        else:
            ineligible_schemes.append(scheme_dict)
    
    return {
        "user_profile": profile.model_dump(),
        "eligible_schemes": eligible_schemes,
        "ineligible_schemes": ineligible_schemes
    }
