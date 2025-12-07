"""
Admin AI Router - AI-assisted eligibility extraction
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db
import models
from services import bytez_client
from services.auth import require_admin

router = APIRouter(prefix="/api/admin/ai", tags=["admin-ai"])


@router.post("/extract-eligibility/{scheme_id}")
async def ai_extract_eligibility_for_scheme(
    scheme_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    """
    Use AI (Qwen via Bytez) to extract eligibility info for a single scheme,
    and update the scheme's min_age, max_age, min_income, max_income, occupation.
    
    Returns the updated fields and raw AI response.
    """
    scheme = db.query(models.Scheme).filter(models.Scheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    if not bytez_client.enabled():
        raise HTTPException(
            status_code=400,
            detail="Bytez LLM not enabled. Cannot run AI extraction. Set USE_BYTEZ_LLM=true and BYTEZ_API_KEY in .env",
        )

    # Prefer full_description; fallback to short_description
    text = scheme.full_description or scheme.short_description
    if not text:
        raise HTTPException(
            status_code=400,
            detail="Scheme has no description text to analyze.",
        )

    result = await bytez_client.extract_eligibility_from_text(
        scheme_name=scheme.name,
        state=scheme.state,
        category=scheme.category,
        description_text=text,
    )

    if not result:
        raise HTTPException(
            status_code=500, 
            detail="AI did not return usable data. Check backend logs for details."
        )

    # Safely update fields if present
    def safe_int(v):
        try:
            return int(v) if v is not None else None
        except Exception:
            return None

    # Store original values for comparison
    original = {
        "min_age": scheme.min_age,
        "max_age": scheme.max_age,
        "min_income": scheme.min_income,
        "max_income": scheme.max_income,
        "occupation": scheme.occupation,
    }

    # Update only if AI provided a value
    if result.get("min_age") is not None:
        scheme.min_age = safe_int(result.get("min_age"))
    if result.get("max_age") is not None:
        scheme.max_age = safe_int(result.get("max_age"))
    if result.get("min_income") is not None:
        scheme.min_income = safe_int(result.get("min_income"))
    if result.get("max_income") is not None:
        scheme.max_income = safe_int(result.get("max_income"))

    occ = result.get("occupation")
    if isinstance(occ, str) and occ.strip():
        scheme.occupation = occ.strip().lower()

    # Commit changes
    db.commit()
    db.refresh(scheme)

    return {
        "status": "ok",
        "scheme_id": scheme.id,
        "scheme_name": scheme.name,
        "original_fields": original,
        "updated_fields": {
            "min_age": scheme.min_age,
            "max_age": scheme.max_age,
            "min_income": scheme.min_income,
            "max_income": scheme.max_income,
            "occupation": scheme.occupation,
        },
        "raw_ai_response": result,
    }


@router.post("/extract-eligibility-batch")
async def ai_extract_eligibility_batch(
    limit: int = 10,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    """
    Run AI extraction on multiple schemes at once.
    Useful for processing newly ingested schemes.
    
    Query params:
    - limit: max number of schemes to process (default 10, max 50)
    """
    if not bytez_client.enabled():
        raise HTTPException(
            status_code=400,
            detail="Bytez LLM not enabled. Cannot run AI extraction.",
        )

    # Cap limit
    limit = min(limit, 50)

    # Get schemes that have descriptions but no eligibility data
    schemes = db.query(models.Scheme).filter(
        models.Scheme.min_age == None,
        models.Scheme.max_age == None,
    ).limit(limit).all()

    if not schemes:
        return {
            "status": "ok",
            "message": "No schemes found that need extraction",
            "processed": 0,
            "results": []
        }

    results = []
    success_count = 0
    error_count = 0

    for scheme in schemes:
        try:
            text = scheme.full_description or scheme.short_description
            if not text:
                results.append({
                    "scheme_id": scheme.id,
                    "scheme_name": scheme.name,
                    "status": "skipped",
                    "reason": "no description"
                })
                continue

            result = await bytez_client.extract_eligibility_from_text(
                scheme_name=scheme.name,
                state=scheme.state,
                category=scheme.category,
                description_text=text,
            )

            if result:
                # Update scheme
                def safe_int(v):
                    try:
                        return int(v) if v is not None else None
                    except Exception:
                        return None

                if result.get("min_age") is not None:
                    scheme.min_age = safe_int(result.get("min_age"))
                if result.get("max_age") is not None:
                    scheme.max_age = safe_int(result.get("max_age"))
                if result.get("min_income") is not None:
                    scheme.min_income = safe_int(result.get("min_income"))
                if result.get("max_income") is not None:
                    scheme.max_income = safe_int(result.get("max_income"))

                occ = result.get("occupation")
                if isinstance(occ, str) and occ.strip():
                    scheme.occupation = occ.strip().lower()

                db.commit()
                success_count += 1

                results.append({
                    "scheme_id": scheme.id,
                    "scheme_name": scheme.name,
                    "status": "success",
                    "extracted": result
                })
            else:
                error_count += 1
                results.append({
                    "scheme_id": scheme.id,
                    "scheme_name": scheme.name,
                    "status": "error",
                    "reason": "AI returned no data"
                })

        except Exception as e:
            error_count += 1
            results.append({
                "scheme_id": scheme.id,
                "scheme_name": scheme.name,
                "status": "error",
                "reason": str(e)
            })

    return {
        "status": "ok",
        "processed": len(schemes),
        "success": success_count,
        "errors": error_count,
        "results": results
    }
