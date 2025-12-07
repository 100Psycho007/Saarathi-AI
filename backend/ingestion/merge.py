# backend/ingestion/merge.py

from datetime import datetime
from typing import List, Dict
from sqlalchemy.orm import Session

import models


def upsert_schemes_from_source(db: Session, items: List[Dict], source: str) -> Dict[str, int]:
    """
    Upsert schemes coming from a given external source.
    Each item should be a normalized dict with keys:
      - source_scheme_id (required)
      - name, state, category, short_description, full_description,
        min_age, max_age, min_income, max_income, occupation,
        official_link, application_process (all optional)
    """
    inserted = 0
    updated = 0

    for item in items:
        sid = item.get("source_scheme_id")
        if not sid:
            continue

        existing = (
            db.query(models.Scheme)
            .filter(models.Scheme.source == source)
            .filter(models.Scheme.source_scheme_id == sid)
            .first()
        )

        if existing:
            # Update mutable fields
            existing.name = item.get("name", existing.name)
            existing.state = item.get("state", existing.state)
            existing.category = item.get("category", existing.category)
            existing.short_description = item.get("short_description", existing.short_description)
            existing.full_description = item.get("full_description", existing.full_description)
            existing.min_age = item.get("min_age", existing.min_age)
            existing.max_age = item.get("max_age", existing.max_age)
            existing.min_income = item.get("min_income", existing.min_income)
            existing.max_income = item.get("max_income", existing.max_income)
            existing.occupation = item.get("occupation", existing.occupation)
            existing.official_link = item.get("official_link", existing.official_link)
            existing.application_process = item.get("application_process", existing.application_process)
            existing.last_synced_at = datetime.utcnow()
            updated += 1
        else:
            db.add(
                models.Scheme(
                    source=source,
                    source_scheme_id=sid,
                    name=item["name"],
                    state=item.get("state"),
                    category=item.get("category"),
                    short_description=item.get("short_description"),
                    full_description=item.get("full_description"),
                    min_age=item.get("min_age"),
                    max_age=item.get("max_age"),
                    min_income=item.get("min_income"),
                    max_income=item.get("max_income"),
                    occupation=item.get("occupation"),
                    official_link=item.get("official_link"),
                    application_process=item.get("application_process"),
                    last_synced_at=datetime.utcnow(),
                )
            )
            inserted += 1

    db.commit()
    return {"inserted": inserted, "updated": updated}
