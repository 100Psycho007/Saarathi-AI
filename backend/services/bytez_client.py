"""
Qwen3 Bytez Client - Optimized for Non-Thinking Mode

We explicitly disable Qwen3 thinking mode to:
- Avoid <think> blocks
- Prevent endless reasoning loops
- Keep responses short, gov-friendly
"""

import os
from typing import List, Optional
from bytez import Bytez
import schemas
import models

BYTEZ_API_KEY = os.getenv("BYTEZ_API_KEY")
BYTEZ_MODEL_ID = os.getenv("BYTEZ_MODEL_ID", "Qwen/Qwen3-1.7B")
USE_BYTEZ_LLM = os.getenv("USE_BYTEZ_LLM", "false").lower() == "true"

# Initialize SDK
_sdk = None
_model = None

def _init_sdk():
    global _sdk, _model
    if _sdk is None and BYTEZ_API_KEY:
        _sdk = Bytez(BYTEZ_API_KEY)
        _model = _sdk.model(BYTEZ_MODEL_ID)


def enabled() -> bool:
    return bool(BYTEZ_API_KEY) and USE_BYTEZ_LLM


def _build_messages(question: str, profile: Optional[schemas.UserProfileCreate], schemes: List[models.Scheme]):
    scheme_lines = "\n".join([f"- {s.name} ({s.state})" for s in schemes[:4]])
    
    system_prompt = """You are an Indian government welfare scheme assistant. Answer in **non-thinking mode**. Do NOT include <think> sections or internal reasoning.

Guidelines:
- Max 3–5 sentences
- Use bullet points only if needed
- If user says hi/hello → greet + ask what help they need, do NOT list schemes
- If unclear → ask 1 follow-up question instead of dumping info
- If referring to schemes → mention max 1–2 only"""

    user_message = f"""USER PROFILE:
State: {profile.state if profile else "unknown"}
Age: {profile.age if profile else "unknown"}
Occupation: {profile.occupation if profile else "unknown"}

AVAILABLE SCHEMES:
{scheme_lines}

QUESTION: {question}"""

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]


def generate_answer_sync(question, profile, schemes):
    """
    Generate answer using Bytez SDK (synchronous).
    Returns None if Bytez is disabled or fails (to trigger mock_ai fallback).
    """
    if not enabled():
        return None
    
    try:
        # Initialize SDK if needed
        _init_sdk()
        
        if _model is None:
            print("Bytez SDK not initialized")
            return None
        
        # Build messages
        messages = _build_messages(question, profile, schemes)
        
        print(f"Bytez: Sending request to {BYTEZ_MODEL_ID}")
        
        # Call Bytez SDK (synchronous)
        result = _model.run(messages)
        print(f"Bytez raw result type: {type(result)}")
        
        # The SDK returns a Response object with attributes
        # Check if it has error
        if hasattr(result, 'error') and result.error:
            print(f"Bytez API error: {result.error}")
            return None
        
        # Get the output text
        if hasattr(result, 'output'):
            output = result.output
        elif hasattr(result, 'text'):
            output = result.text
        elif hasattr(result, 'content'):
            output = result.content
        else:
            # Try to convert to string
            output = str(result)
        
        if output:
            output_str = str(output).strip()
            
            # If it's a dict-like string, try to parse it
            if output_str.startswith("{'role':") or output_str.startswith('{"role":'):
                try:
                    import ast
                    parsed = ast.literal_eval(output_str)
                    if isinstance(parsed, dict) and 'content' in parsed:
                        output_str = parsed['content']
                except:
                    pass
            
            # Remove <think> blocks
            import re
            output_str = re.sub(r'<think>.*?</think>', '', output_str, flags=re.DOTALL).strip()
            
            print(f"Bytez API success: {output_str[:100]}...")
            return output_str
        
        return None
        
    except Exception as e:
        print(f"Bytez SDK unexpected error: {type(e).__name__} - {e}")
        return None


async def generate_answer(question, profile, schemes):
    """
    Async wrapper for generate_answer_sync.
    """
    # Run synchronous Bytez call in thread pool to avoid blocking
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, generate_answer_sync, question, profile, schemes)


def extract_eligibility_sync(scheme_name: str, state: Optional[str], category: Optional[str], description_text: str) -> dict:
    """
    Use Qwen via Bytez to extract structured eligibility rules from free text.
    Returns a dict with extracted fields or empty dict on error.
    """
    if not enabled():
        return {}
    
    try:
        _init_sdk()
        
        if _model is None:
            print("Bytez SDK not initialized for extraction")
            return {}
        
        prompt = f"""You are an assistant that reads Indian government scheme descriptions and extracts eligibility rules.

SCHEME:
- Name: {scheme_name}
- State: {state or "unknown"}
- Category: {category or "unknown"}

DESCRIPTION TEXT:
{description_text}

TASK:
- Read the text carefully.
- Extract *only* what is explicitly given or very strongly implied.
- If something is not mentioned, return null for that field.
- Income is annual household income in INR if present.

RESPOND IN PURE JSON ONLY, NO EXPLANATION, with this exact structure:
{{
  "min_age": <number or null>,
  "max_age": <number or null>,
  "min_income": <number or null>,
  "max_income": <number or null>,
  "occupation": <string or null>,
  "gender": <string or null>,
  "notes": <string or null>
}}"""

        messages = [
            {"role": "system", "content": "You extract eligibility data from scheme descriptions. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        print(f"Bytez: Extracting eligibility for {scheme_name}")
        
        result = _model.run(messages)
        
        if hasattr(result, 'error') and result.error:
            print(f"Bytez extraction error: {result.error}")
            return {}
        
        # Get output
        if hasattr(result, 'output'):
            output = result.output
        elif hasattr(result, 'text'):
            output = result.text
        elif hasattr(result, 'content'):
            output = result.content
        else:
            output = str(result)
        
        if output:
            output_str = str(output).strip()
            
            # If output is a dict-like string, try to parse it first
            if output_str.startswith("{'role':") or output_str.startswith('{"role":'):
                try:
                    import ast
                    parsed = ast.literal_eval(output_str)
                    if isinstance(parsed, dict) and 'content' in parsed:
                        output_str = parsed['content']
                except:
                    pass
            
            print(f"Bytez raw output: {output_str[:200]}")
            
            # Try to extract JSON from response
            import json
            import re
            
            # Remove markdown code blocks if present
            output_str = re.sub(r'```json\s*', '', output_str)
            output_str = re.sub(r'```\s*', '', output_str)
            
            # Remove thinking blocks
            output_str = re.sub(r'<think>.*?</think>', '', output_str, flags=re.DOTALL).strip()
            
            # Try multiple JSON extraction strategies
            json_str = None
            
            # Strategy 1: Find JSON object with balanced braces
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', output_str)
            if json_match:
                json_str = json_match.group(0)
            
            # Strategy 2: If that fails, try to find anything between first { and last }
            if not json_str:
                first_brace = output_str.find('{')
                last_brace = output_str.rfind('}')
                if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                    json_str = output_str[first_brace:last_brace+1]
            
            if json_str:
                try:
                    # Try to fix common JSON issues
                    # Replace single quotes with double quotes
                    json_str = json_str.replace("'", '"')
                    # Fix null values
                    json_str = re.sub(r':\s*None\b', ': null', json_str)
                    json_str = re.sub(r':\s*True\b', ': true', json_str)
                    json_str = re.sub(r':\s*False\b', ': false', json_str)
                    
                    data = json.loads(json_str)
                    if isinstance(data, dict):
                        print(f"Bytez extraction success: {data}")
                        return data
                except json.JSONDecodeError as je:
                    print(f"JSON parse error: {je}")
                    print(f"Attempted to parse: {json_str[:200]}")
            
        return {}
        
    except Exception as e:
        print(f"Bytez extraction error: {type(e).__name__} - {e}")
        return {}


async def extract_eligibility_from_text(
    scheme_name: str,
    state: Optional[str],
    category: Optional[str],
    description_text: str,
) -> dict:
    """
    Async wrapper for extract_eligibility_sync.
    Use Qwen via Bytez to extract structured eligibility rules from free text.
    Returns a dict like:
    {
      "min_age": int | None,
      "max_age": int | None,
      "min_income": int | None,
      "max_income": int | None,
      "occupation": str | None,
      "gender": str | None,
      "notes": str | None
    }
    
    If Bytez is disabled or there is an error, return an empty dict.
    """
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, extract_eligibility_sync, scheme_name, state, category, description_text)
