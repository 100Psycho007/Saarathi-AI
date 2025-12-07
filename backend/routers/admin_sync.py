# backend/routers/admin_sync.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db
from ingestion.myscheme_ingestor import load_mock_myscheme_data
from ingestion.merge import upsert_schemes_from_source
from services.auth import require_admin

router = APIRouter(prefix="/api/admin/sync", tags=["admin-sync"])


@router.post("/myscheme")
def sync_myscheme(state: str, db: Session = Depends(get_db), _: dict = Depends(require_admin)):
    """
    Sync schemes for a given state from a mock myScheme JSON file.
    In production this can be replaced with real API calls to myScheme or data.gov.in.
    """
    data = load_mock_myscheme_data(state)
    if not data:
        raise HTTPException(status_code=404, detail=f"No mock data found for state '{state}'.")

    result = upsert_schemes_from_source(db, data, source="myscheme")
    return {
        "status": "ok",
        "state": state,
        "inserted": result["inserted"],
        "updated": result["updated"],
    }
