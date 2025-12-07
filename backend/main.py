import os
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from db import Base, engine, get_db
from routers import schemes, eligibility, assistant, admin_sync, admin_ai, auth

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Gov Scheme Navigator API")

# CORS middleware - allow production and local dev
frontend_origin = os.getenv("FRONTEND_ORIGIN")
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://saarathi-ai.netlify.app",  # Production Netlify
]
if frontend_origin:
    origins.append(frontend_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions gracefully"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors without exposing internals"""
    # Log the error for debugging
    print(f"Unhandled error: {type(exc).__name__} - {repr(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )

# Include routers
app.include_router(schemes.router, prefix="/api")
app.include_router(eligibility.router, prefix="/api")
app.include_router(assistant.router, prefix="/api")
app.include_router(auth.router)
app.include_router(admin_sync.router)
app.include_router(admin_ai.router)

@app.get("/")
def read_root():
    return {"status": "ok", "service": "AI Gov Scheme Navigator API"}


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Enhanced health check with DB and AI mode status"""
    try:
        # Test database connection
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "error"
    
    # Check AI mode
    from services import bytez_client
    ai_mode = "bytez" if bytez_client.enabled() else "mock"
    
    return {
        "status": "ok",
        "db": db_status,
        "ai_mode": ai_mode
    }


@app.get("/api/test-bytez")
async def test_bytez():
    """Test endpoint to check if Bytez is working"""
    from services import bytez_client
    import traceback
    
    result = {
        "bytez_enabled": bytez_client.enabled(),
        "api_key_set": bool(bytez_client.BYTEZ_API_KEY),
        "api_key_preview": bytez_client.BYTEZ_API_KEY[:10] + "..." if bytez_client.BYTEZ_API_KEY else None,
        "model_id": bytez_client.BYTEZ_MODEL_ID,
        "use_bytez_llm": bytez_client.USE_BYTEZ_LLM,
    }
    
    if bytez_client.enabled():
        try:
            # Test with simple message
            answer = await bytez_client.generate_answer("Say hello", None, [])
            result["test_response"] = answer
            result["test_success"] = answer is not None
            
            if answer is None:
                result["note"] = "Check backend terminal for error logs"
        except Exception as e:
            result["test_error"] = str(e)
            result["test_traceback"] = traceback.format_exc()
            result["test_success"] = False
    
    return result
