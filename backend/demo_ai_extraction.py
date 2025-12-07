"""
Demo script to show AI extraction working
"""
import asyncio
from sqlalchemy.orm import Session
from db import SessionLocal
import models
from services import bytez_client

async def demo_extraction():
    db = SessionLocal()
    
    try:
        # Find a scheme with good description
        scheme = db.query(models.Scheme).filter(
            models.Scheme.id == 35  # Chief Minister's Breakfast Scheme
        ).first()
        
        if not scheme:
            print("Scheme not found")
            return
        
        print(f"=== AI Extraction Demo ===\n")
        print(f"Scheme: {scheme.name}")
        print(f"State: {scheme.state}")
        print(f"Category: {scheme.category}\n")
        
        print(f"Description:")
        print(f"{scheme.full_description or scheme.short_description}\n")
        
        print(f"Current eligibility data:")
        print(f"  Age: {scheme.min_age} - {scheme.max_age}")
        print(f"  Income: {scheme.min_income} - {scheme.max_income}")
        print(f"  Occupation: {scheme.occupation}\n")
        
        print("Running AI extraction...\n")
        
        result = await bytez_client.extract_eligibility_from_text(
            scheme_name=scheme.name,
            state=scheme.state,
            category=scheme.category,
            description_text=scheme.full_description or scheme.short_description
        )
        
        print(f"AI Extracted:")
        print(f"  min_age: {result.get('min_age')}")
        print(f"  max_age: {result.get('max_age')}")
        print(f"  min_income: {result.get('min_income')}")
        print(f"  max_income: {result.get('max_income')}")
        print(f"  occupation: {result.get('occupation')}")
        print(f"  gender: {result.get('gender')}")
        print(f"  notes: {result.get('notes')}")
        
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(demo_extraction())
