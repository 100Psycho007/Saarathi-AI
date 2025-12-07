"""
Quick test script for AI extraction
"""
import asyncio
from services import bytez_client

async def test_extraction():
    print("Testing Bytez extraction...")
    print(f"Bytez enabled: {bytez_client.enabled()}")
    
    test_description = """
    This scheme provides financial assistance to students aged 16-30 years 
    from SC/ST/OBC categories for post-matric studies. Students must have 
    annual family income below Rs. 2,50,000. The scheme covers tuition fees 
    and provides maintenance allowance.
    """
    
    result = await bytez_client.extract_eligibility_from_text(
        scheme_name="Test Scholarship",
        state="Karnataka",
        category="student",
        description_text=test_description
    )
    
    print(f"\nExtraction result: {result}")
    print(f"Result type: {type(result)}")

if __name__ == "__main__":
    asyncio.run(test_extraction())
