# backend/routers/assistant.py

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db import get_db
import schemas
import models
from services import mock_ai, bytez_client
from services.eligibility_service import check_eligibility
from utils.rate_limiter import check_rate_limit

router = APIRouter(prefix="/assistant", tags=["assistant"])


class ChatRequest(BaseModel):
    text: str
    # All profile fields optional; if provided we use them
    name: Optional[str] = None
    state: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    annual_income: Optional[int] = None


class SuggestedScheme(BaseModel):
    scheme: schemas.SchemeRead
    summary: str
    eligibility_explanation: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    suggested_schemes: List[SuggestedScheme] = []


@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(
    payload: ChatRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    # Rate limiting check
    ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(ip):
        raise HTTPException(
            status_code=429,
            detail="Too many requests, please slow down."
        )
    
    # Build a temporary profile if enough fields are provided
    profile_obj: Optional[schemas.UserProfileCreate] = None
    if payload.state and payload.age is not None:
        profile_obj = schemas.UserProfileCreate(
            name=payload.name or "Guest",
            state=payload.state,
            age=payload.age,
            gender=payload.gender,
            occupation=payload.occupation,
            annual_income=payload.annual_income,
        )

    # Fetch schemes; if state known, filter by it + Central, else fetch a small set
    query = db.query(models.Scheme)
    if profile_obj:
        query = query.filter(
            (models.Scheme.state == profile_obj.state) | (models.Scheme.state == "Central")
        )
    else:
        # Fallback: just fetch some top schemes
        query = query.limit(10)

    schemes = query.all()

    suggested: List[SuggestedScheme] = []

    # If we have a profile, compute eligibility and explanation
    if profile_obj:
        for s in schemes:
            elig = check_eligibility(profile_obj, s)
            if elig.get("eligible"):
                summary = mock_ai.summarize_scheme(s)
                explanation = mock_ai.explain_eligibility(profile_obj, s, elig)
                suggested.append(
                    SuggestedScheme(
                        scheme=schemas.SchemeRead.from_orm(s),
                        summary=summary,
                        eligibility_explanation=explanation,
                    )
                )
        # Sort so that we don't overload; take top 3
        suggested = suggested[:3]
    else:
        # No profile: just send summaries without eligibility
        for s in schemes[:3]:
            summary = mock_ai.summarize_scheme(s)
            suggested.append(
                SuggestedScheme(
                    scheme=schemas.SchemeRead.from_orm(s),
                    summary=summary,
                    eligibility_explanation=None,
                )
            )

    # Generate main answer using Bytez or fallback to mock_ai
    answer = None
    if bytez_client.enabled():
        answer = await bytez_client.generate_answer(payload.text, profile_obj, schemes)
    
    # If Bytez disabled or failed, use mock_ai
    if answer is None:
        answer = mock_ai.answer_user_question(
            question=payload.text,
            profile=profile_obj,
            schemes=[s for s in schemes],
        )

    return ChatResponse(answer=answer, suggested_schemes=suggested)
