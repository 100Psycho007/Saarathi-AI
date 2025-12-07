"""
Mock AI Layer for Government Scheme Navigator

This module provides a rule-based AI assistant that simulates LLM-like behavior
without requiring external API calls. It is intentionally structured so we can
swap it with a real LLM client later without changing the rest of the app.

Key functions:
- summarize_scheme: Generate human-friendly scheme summaries
- explain_eligibility: Explain why a user is/isn't eligible for a scheme
- answer_user_question: Handle user questions with context-aware responses

All responses are structured with headings, bullets, and emojis to feel
more like a real AI assistant while remaining 100% local and rule-based.
"""

from typing import List, Dict, Optional
from enum import Enum
import schemas
from models import Scheme


class QuestionType(str, Enum):
    """Classification of user question types for better response handling."""
    HOW_TO_APPLY = "how_to_apply"
    DOCUMENTS = "documents"
    ELIGIBILITY = "eligibility"
    BENEFITS = "benefits"
    GENERAL = "general"


def _safe_str(value) -> str:
    """Safely convert a value to string, returning empty string for None."""
    return "" if value is None else str(value)


def classify_question(text: str) -> QuestionType:
    """
    Classify user question into one of the predefined types with improved NLP.
    
    Args:
        text: The user's question text
        
    Returns:
        QuestionType enum indicating the question category
    """
    q = (text or "").lower().strip()
    
    # Normalize common variations
    q = q.replace("'", "").replace("?", "").replace("!", "")
    
    # HOW TO APPLY patterns
    apply_patterns = [
        "how to apply", "how do i apply", "how can i apply",
        "apply for", "application process", "how to get",
        "registration", "register for", "sign up"
    ]
    if any(pattern in q for pattern in apply_patterns):
        return QuestionType.HOW_TO_APPLY
    
    # DOCUMENTS patterns
    doc_patterns = [
        "document", "documents", "proof", "certificate",
        "what do i need", "what documents", "papers needed",
        "requirements", "what to submit", "upload"
    ]
    if any(pattern in q for pattern in doc_patterns):
        return QuestionType.DOCUMENTS
    
    # ELIGIBILITY patterns
    eligibility_patterns = [
        "eligible", "eligibility", "qualify", "am i eligible",
        "can i get", "do i qualify", "who can apply",
        "criteria", "requirements for", "who is eligible"
    ]
    if any(pattern in q for pattern in eligibility_patterns):
        return QuestionType.ELIGIBILITY
    
    # BENEFITS patterns
    benefit_patterns = [
        "benefit", "benefits", "what do i get", "what will i get",
        "how much", "amount", "money", "financial help",
        "what is provided", "advantages", "perks"
    ]
    if any(pattern in q for pattern in benefit_patterns):
        return QuestionType.BENEFITS
    
    return QuestionType.GENERAL


def _find_scheme_by_name(question: str, schemes: List[Scheme]) -> Optional[Scheme]:
    """
    Try to find a specific scheme mentioned in the user's question with fuzzy matching.
    
    Args:
        question: User's question text
        schemes: List of available schemes
        
    Returns:
        Matching Scheme object or None
    """
    q_lower = question.lower().strip()
    
    # Remove common words that don't help matching
    stop_words = {"the", "a", "an", "for", "of", "in", "to", "and", "or", "is", "are"}
    q_words = [w for w in q_lower.split() if w not in stop_words and len(w) > 2]
    
    best_match = None
    best_score = 0
    
    for scheme in schemes:
        scheme_name = _safe_str(getattr(scheme, "name", "")).lower()
        category = _safe_str(getattr(scheme, "category", "")).lower()
        short_desc = _safe_str(getattr(scheme, "short_description", "")).lower()
        
        # Direct name match (highest priority)
        if scheme_name and scheme_name in q_lower:
            return scheme
        
        # Calculate match score
        score = 0
        name_words = [w for w in scheme_name.split() if w not in stop_words and len(w) > 2]
        
        # Count matching words
        for q_word in q_words:
            if q_word in scheme_name:
                score += 3
            elif q_word in category:
                score += 2
            elif q_word in short_desc:
                score += 1
        
        # Bonus for matching multiple significant words
        matches = sum(1 for word in name_words if word in q_lower)
        if matches >= 2:
            score += 5
        
        if score > best_score:
            best_score = score
            best_match = scheme
    
    # Only return if we have a reasonable match
    return best_match if best_score >= 3 else None


def summarize_scheme(scheme: Scheme | schemas.SchemeRead, language: str = "en") -> str:
    """
    Generate a structured, LLM-like summary of a government scheme.
    
    Used by the assistant router to provide quick scheme overviews.
    Returns a well-formatted plain text summary with line breaks and bullets.
    
    Args:
        scheme: The scheme object to summarize
        language: Language code (currently only "en" supported)
        
    Returns:
        Formatted multi-line string summary
    """
    name = _safe_str(getattr(scheme, "name", ""))
    category = _safe_str(getattr(scheme, "category", ""))
    state = _safe_str(getattr(scheme, "state", ""))
    short_desc = _safe_str(getattr(scheme, "short_description", ""))
    
    # Determine target audience
    target = category if category else "eligible citizens"
    state_text = "Central" if state.lower() == "central" else state
    
    # Build structured summary
    lines = []
    lines.append(f"{name} is a welfare scheme in {state_text} mainly targeted at {target}.")
    lines.append("")
    lines.append("Key idea:")
    
    if short_desc:
        lines.append(f"- {short_desc}")
    else:
        lines.append("- Provides financial or other support to eligible citizens")
    
    lines.append("")
    lines.append("You can use this scheme if you meet the age, income, and occupation rules mentioned in the eligibility section.")
    
    return "\n".join(lines)


def explain_eligibility(
    profile: schemas.UserProfileCreate,
    scheme: Scheme | schemas.SchemeRead,
    eligibility_result: Dict,
    language: str = "en",
) -> str:
    """
    Generate a detailed explanation of eligibility status with structured formatting.
    
    Used by the assistant router to explain why a user is or isn't eligible
    for a specific scheme based on their profile.
    
    Args:
        profile: User's profile information
        scheme: The scheme being evaluated
        eligibility_result: Dict with 'eligible' (bool) and 'reasons' (list)
        language: Language code (currently only "en" supported)
        
    Returns:
        Formatted multi-line explanation with headings and bullets
    """
    eligible = eligibility_result.get("eligible", False)
    reasons: List[str] = eligibility_result.get("reasons", [])
    
    name = _safe_str(getattr(scheme, "name", "this scheme"))
    
    # Extract profile details
    state = _safe_str(profile.state) if profile.state else "not specified"
    age = _safe_str(profile.age) if profile.age else "not provided"
    occupation = _safe_str(profile.occupation) if profile.occupation else "not specified"
    income = f"₹{profile.annual_income:,}" if profile.annual_income is not None else "not provided"
    
    lines = []
    
    if eligible:
        lines.append(f"✅ Eligibility result for '{name}'")
        lines.append("")
        lines.append("You are LIKELY ELIGIBLE based on:")
        lines.append(f"- State: {state}")
        lines.append(f"- Age: {age}")
        lines.append(f"- Occupation: {occupation}")
        lines.append(f"- Annual income: {income}")
        lines.append("")
        lines.append("Why you fit:")
        
        # Add specific reasons if available, otherwise generic ones
        if reasons:
            for reason in reasons:
                lines.append(f"- {reason}")
        else:
            lines.append("- Your profile matches the age range for this scheme.")
            lines.append("- Your occupation is allowed for this scheme.")
            if profile.annual_income is not None:
                lines.append("- Your income is within the required limits.")
        
        lines.append("")
        lines.append("Next step:")
        lines.append("- Review the detailed rules on the official portal and proceed with application if everything matches.")
    else:
        lines.append(f"❌ Eligibility result for '{name}'")
        lines.append("")
        lines.append("You are NOT eligible with the current details.")
        lines.append("")
        lines.append("Main reasons:")
        
        if reasons:
            for reason in reasons:
                lines.append(f"- {reason}")
        else:
            lines.append("- The profile does not match the required conditions.")
        
        lines.append("")
        lines.append("What you can do:")
        lines.append("- Double-check your details (age, income, state, occupation).")
        lines.append("- Explore other schemes that may match your profile better.")
    
    return "\n".join(lines)


def answer_user_question(
    question: str,
    profile: Optional[schemas.UserProfileCreate],
    schemes: List[Scheme],
) -> str:
    """
    Handle user questions with context-aware, structured responses.
    
    Used by the assistant chat endpoint to provide intelligent answers
    based on question type, available schemes, and user profile.
    
    This function classifies the question, attempts to find relevant schemes,
    and generates a formatted response with headings, bullets, and emojis.
    
    Args:
        question: The user's question text
        profile: Optional user profile for personalized responses
        schemes: List of available schemes (may be filtered by state/category)
        
    Returns:
        Formatted multi-line response string
    """
    q_lower = question.lower().strip()
    
    # Handle greetings naturally
    greetings = ["hi", "hello", "hey", "hii", "helo", "namaste", "good morning", "good afternoon", "good evening"]
    if q_lower in greetings or any(q_lower.startswith(g + " ") or q_lower.startswith(g + ",") for g in greetings):
        if profile and profile.name:
            return f"Hi {profile.name}! 👋\n\nI'm here to help you discover government schemes you might be eligible for.\n\nYou can ask me:\n• 'What schemes am I eligible for?'\n• 'How do I apply for [scheme name]?'\n• 'What documents do I need?'\n\nWhat would you like to know?"
        else:
            return "Hi there! 👋\n\nI'm your AI assistant for government schemes.\n\nI can help you:\n• Find schemes you're eligible for\n• Explain how to apply\n• Answer questions about benefits and documents\n\nFill out your profile on the left to get personalized recommendations, or just ask me anything!"
    
    # Handle thank you
    thanks = ["thank", "thanks", "thank you", "thankyou", "thx", "ty"]
    if any(t in q_lower for t in thanks):
        return "You're welcome! 😊\n\nFeel free to ask if you have more questions about government schemes or eligibility."
    
    q_type = classify_question(question)
    target_scheme = _find_scheme_by_name(question, schemes)
    
    lines = []
    
    # Add context intro only for specific question types
    if profile and q_type in [QuestionType.ELIGIBILITY, QuestionType.BENEFITS]:
        state = _safe_str(profile.state) if profile.state else "not specified"
        occupation = _safe_str(profile.occupation) if profile.occupation else "not specified"
        age = _safe_str(profile.age) if profile.age else "not provided"
        lines.append(f"Based on your profile (State: {state}, Occupation: {occupation}, Age: {age}):\n")
    
    # Handle different question types
    if q_type == QuestionType.HOW_TO_APPLY:
        # Try to use target scheme or first available scheme
        scheme_to_use = target_scheme or (schemes[0] if schemes else None)
        
        if scheme_to_use:
            scheme_name = _safe_str(getattr(scheme_to_use, "name", ""))
            application_process = _safe_str(getattr(scheme_to_use, "application_process", ""))
            official_link = _safe_str(getattr(scheme_to_use, "official_link", ""))
            
            lines.append(f"📝 How to apply for '{scheme_name}'")
            lines.append("")
            lines.append("Suggested steps:")
            
            if application_process:
                # Split by common delimiters and format as steps
                steps = application_process.replace(". ", ".\n").split("\n")
                for i, step in enumerate(steps, 1):
                    step = step.strip()
                    if step:
                        lines.append(f"- Step {i}: {step}")
            else:
                lines.append("- Step 1: Visit the official government portal")
                lines.append("- Step 2: Register or login with your credentials")
                lines.append("- Step 3: Fill out the application form with required details")
                lines.append("- Step 4: Upload necessary documents")
                lines.append("- Step 5: Submit and save the acknowledgment receipt")
            
            lines.append("")
            lines.append("Tip:")
            if official_link:
                lines.append(f"- Always cross-check the latest instructions on the official portal: {official_link}")
            else:
                lines.append("- Always cross-check the latest instructions on the official government portal")
        else:
            lines.append("📝 How to apply for government schemes")
            lines.append("")
            lines.append("General application process:")
            lines.append("- Step 1: Visit the official scheme portal or government website")
            lines.append("- Step 2: Register with your mobile number and create an account")
            lines.append("- Step 3: Fill the online application form with accurate details")
            lines.append("- Step 4: Upload required documents (ID, address, income proof, etc.)")
            lines.append("- Step 5: Submit the form and note down the application reference number")
            lines.append("")
            lines.append("Tip:")
            lines.append("- Keep digital copies of all documents ready before starting")
            lines.append("- Check the scheme's official website for specific requirements")
    
    elif q_type == QuestionType.DOCUMENTS:
        lines.append("📂 Common documents needed for many schemes:")
        lines.append("")
        lines.append("- ID proof (Aadhaar card)")
        lines.append("- Address proof (Aadhaar, ration card, voter ID, etc.)")
        lines.append("- Income certificate (from Tehsildar or competent authority)")
        lines.append("- Bank passbook or cancelled cheque (for direct benefit transfer)")
        lines.append("- Caste / category certificate (if applicable - SC/ST/OBC)")
        lines.append("- Age proof (birth certificate, school certificate)")
        lines.append("- Passport-size photographs")
        lines.append("")
        lines.append("Always confirm the exact list on the official website of the scheme.")
    
    elif q_type == QuestionType.ELIGIBILITY:
        if profile and schemes:
            state = _safe_str(profile.state) if profile.state else "not specified"
            occupation = _safe_str(profile.occupation) if profile.occupation else "not specified"
            age = _safe_str(profile.age) if profile.age else "not provided"
            
            lines.append("✅ Understanding eligibility")
            lines.append("")
            lines.append(f"For your profile (state: {state}, occupation: {occupation}, age: {age}), eligibility usually depends on:")
            lines.append("")
            lines.append("- Age range allowed by the scheme")
            lines.append("- Income limits (annual family income)")
            lines.append("- Whether your occupation matches the target group")
            lines.append("- State or region (some schemes are state-specific)")
            lines.append("- Category (General, SC, ST, OBC, etc.)")
            lines.append("")
            
            if schemes:
                lines.append("In our database, schemes that may be relevant include:")
                for scheme in schemes[:3]:
                    scheme_name = _safe_str(getattr(scheme, "name", ""))
                    lines.append(f"- {scheme_name}")
        else:
            lines.append("✅ Understanding eligibility")
            lines.append("")
            lines.append("Eligibility for government schemes typically depends on:")
            lines.append("- Your age (many schemes have age limits)")
            lines.append("- Your annual income (most schemes have income ceilings)")
            lines.append("- Your occupation or profession")
            lines.append("- Your state of residence")
            lines.append("- Your social category (if applicable)")
            lines.append("")
            lines.append("Fill out your profile to get personalized eligibility results!")
    
    elif q_type == QuestionType.BENEFITS:
        lines.append("💰 What you can get from government schemes:")
        lines.append("")
        
        if schemes:
            lines.append("Based on available schemes, benefits typically include:")
            lines.append("")
            
            # Extract benefits from schemes
            benefit_types = set()
            for scheme in schemes[:5]:
                short_desc = _safe_str(getattr(scheme, "short_description", "")).lower()
                if "scholarship" in short_desc or "education" in short_desc:
                    benefit_types.add("scholarships")
                if "subsidy" in short_desc or "financial" in short_desc:
                    benefit_types.add("subsidies")
                if "pension" in short_desc:
                    benefit_types.add("pensions")
                if "loan" in short_desc:
                    benefit_types.add("loans")
                if "insurance" in short_desc:
                    benefit_types.add("insurance")
            
            if benefit_types:
                for benefit in sorted(benefit_types):
                    lines.append(f"- {benefit.capitalize()}")
            
            lines.append("")
            lines.append("Specific schemes in our database:")
            for scheme in schemes[:3]:
                scheme_name = _safe_str(getattr(scheme, "name", ""))
                short_desc = _safe_str(getattr(scheme, "short_description", ""))
                lines.append(f"- {scheme_name}: {short_desc}")
        else:
            lines.append("- Scholarships for students (education support)")
            lines.append("- Subsidies for farmers (seeds, equipment, irrigation)")
            lines.append("- Pensions for senior citizens and widows")
            lines.append("- Interest-free or low-interest loans")
            lines.append("- Health insurance coverage")
            lines.append("- Housing assistance")
            lines.append("- Skill development training")
    
    else:  # GENERAL
        # Try to understand what they're asking about
        keywords = {
            "scholarship": "scholarships and education support",
            "farmer": "farmer welfare schemes",
            "pension": "pension schemes",
            "loan": "loan and subsidy programs",
            "student": "student benefits and scholarships",
            "women": "women empowerment schemes",
            "senior": "senior citizen benefits",
        }
        
        topic = None
        for keyword, description in keywords.items():
            if keyword in q_lower:
                topic = description
                break
        
        if topic:
            # They're asking about a specific topic
            relevant_schemes = [s for s in schemes if keyword in _safe_str(getattr(s, "category", "")).lower() 
                              or keyword in _safe_str(getattr(s, "short_description", "")).lower()]
            
            if relevant_schemes:
                lines.append(f"I found some schemes related to {topic}:")
                lines.append("")
                for scheme in relevant_schemes[:3]:
                    scheme_name = _safe_str(getattr(scheme, "name", ""))
                    short_desc = _safe_str(getattr(scheme, "short_description", ""))
                    lines.append(f"• {scheme_name}")
                    if short_desc:
                        lines.append(f"  {short_desc}")
                    lines.append("")
                
                lines.append("Want to know more? Ask me:")
                lines.append("• 'How do I apply for [scheme name]?'")
                lines.append("• 'Am I eligible for [scheme name]?'")
            else:
                lines.append(f"I understand you're asking about {topic}.")
                lines.append("")
                lines.append("I don't have specific schemes matching that in our current database, but you can:")
                lines.append("• Fill out your profile to see all eligible schemes")
                lines.append("• Ask about specific scheme names")
                lines.append("• Try 'What schemes am I eligible for?'")
        else:
            # Generic unclear question
            lines.append("I'm not sure I understood your question. 🤔")
            lines.append("")
            lines.append("I can help you with:")
            lines.append("• Finding schemes you're eligible for")
            lines.append("• Explaining how to apply for specific schemes")
            lines.append("• Listing required documents")
            lines.append("• Understanding benefits and eligibility criteria")
            lines.append("")
            lines.append("Try asking something like:")
            lines.append("• 'What scholarships are available?'")
            lines.append("• 'Show me farmer schemes'")
            lines.append("• 'How do I apply for PM-KISAN?'")
    
    return "\n".join(lines)
