from typing import Dict, List
from schemas import UserProfileCreate
from models import Scheme


def check_eligibility(profile: UserProfileCreate, scheme: Scheme) -> Dict:
    """
    Check if a user profile is eligible for a given scheme.
    STRICT VALIDATION: All criteria must match exactly.
    
    Args:
        profile: User profile data (Pydantic UserProfileCreate)
        scheme: Scheme model from database (SQLAlchemy Scheme)
    
    Returns:
        Dict with:
            - eligible: bool
            - reasons: List[str] of ineligibility reasons
            - score: float (0.0 to 1.0)
    """
    eligible = True
    reasons: List[str] = []
    
    # STRICT: Check state match (Central schemes apply to all states)
    if scheme.state.lower() != "central" and scheme.state.lower() != profile.state.lower():
        eligible = False
        reasons.append(f"This scheme is only for {scheme.state} residents.")
    
    # STRICT: Check age constraints
    if scheme.min_age is not None and profile.age < scheme.min_age:
        eligible = False
        reasons.append(f"Age must be at least {scheme.min_age} years.")
    
    if scheme.max_age is not None and profile.age > scheme.max_age:
        eligible = False
        reasons.append(f"Age must not exceed {scheme.max_age} years.")
    
    # STRICT: Check income constraints
    if scheme.min_income is not None:
        if profile.annual_income is None:
            eligible = False
            reasons.append("Income information is required for this scheme.")
        elif profile.annual_income < scheme.min_income:
            eligible = False
            reasons.append(f"Annual income must be at least ₹{scheme.min_income:,}.")
    
    if scheme.max_income is not None:
        if profile.annual_income is None:
            eligible = False
            reasons.append("Income information is required for this scheme.")
        elif profile.annual_income > scheme.max_income:
            eligible = False
            reasons.append(f"Annual income must not exceed ₹{scheme.max_income:,}.")
    
    # STRICT: Check occupation match
    if scheme.occupation is not None:
        if profile.occupation is None:
            eligible = False
            reasons.append(f"This scheme requires occupation to be specified as '{scheme.occupation}'.")
        elif scheme.occupation.lower() != profile.occupation.lower():
            eligible = False
            reasons.append(f"This scheme is only for {scheme.occupation}s.")
    
    # STRICT: Check gender match
    if scheme.gender is not None and scheme.gender.lower() != "any":
        if profile.gender is None:
            eligible = False
            reasons.append(f"This scheme requires gender to be specified.")
        elif scheme.gender.lower() != profile.gender.lower():
            eligible = False
            reasons.append(f"This scheme is only for {scheme.gender} applicants.")
    
    # STRICT: Check caste match
    if scheme.caste is not None and scheme.caste.lower() != "any":
        if profile.caste is None:
            eligible = False
            reasons.append(f"This scheme requires caste category to be specified.")
        else:
            # Handle multiple caste categories (e.g., "SC/ST/OBC")
            allowed_castes = [c.strip().lower() for c in scheme.caste.split("/")]
            if profile.caste.lower() not in allowed_castes:
                eligible = False
                reasons.append(f"This scheme is only for {scheme.caste} category.")
    
    # STRICT: Check disability requirement
    if scheme.disability is not None and scheme.disability.lower() != "any":
        if profile.disability is None:
            eligible = False
            reasons.append("This scheme requires disability status to be specified.")
        elif scheme.disability.lower() != profile.disability.lower():
            if scheme.disability.lower() == "yes":
                eligible = False
                reasons.append("This scheme is only for persons with disabilities.")
            else:
                eligible = False
                reasons.append("This scheme is not available for persons with disabilities.")
    
    # Calculate score
    score = 1.0 if eligible else 0.0
    
    return {
        "eligible": eligible,
        "reasons": reasons,
        "score": score
    }
