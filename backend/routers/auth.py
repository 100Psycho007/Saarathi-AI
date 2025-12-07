"""
Authentication router for admin login
"""
from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from services.auth import authenticate_admin, create_access_token, require_admin, JWT_EXPIRE_MINUTES

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    confirm_password: str
    registration_key: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class UserInfo(BaseModel):
    username: str
    is_admin: bool

@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """Admin login endpoint"""
    if not authenticate_admin(credentials.username, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=JWT_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": credentials.username, "is_admin": True},
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=JWT_EXPIRE_MINUTES * 60  # Convert to seconds
    )

@router.get("/me", response_model=UserInfo)
async def get_current_user(token_payload: dict = Depends(require_admin)):
    """Get current authenticated user info"""
    return UserInfo(
        username=token_payload["sub"],
        is_admin=token_payload.get("is_admin", False)
    )

@router.post("/logout")
async def logout():
    """Logout endpoint (client should delete token)"""
    return {"message": "Successfully logged out"}

@router.get("/check")
async def check_auth(token_payload: dict = Depends(require_admin)):
    """Check if current token is valid"""
    return {"authenticated": True, "username": token_payload["sub"]}

@router.get("/users")
async def list_users(token_payload: dict = Depends(require_admin)):
    """List registered users (admin only, for debugging)"""
    from services.auth import load_users
    users = load_users()
    return {"users": list(users.keys())}

@router.post("/register")
async def register_admin(registration: RegisterRequest):
    """Register a new admin (requires registration key)"""
    import os
    from services.auth import add_user, load_users
    
    # Check registration key
    REGISTRATION_KEY = os.getenv("ADMIN_REGISTRATION_KEY", "buildathon-admin-2025")
    if registration.registration_key != REGISTRATION_KEY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid registration key"
        )
    
    # Validate passwords match
    if registration.password != registration.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Validate password strength
    if len(registration.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    # Check if username already exists
    users = load_users()
    if registration.username in users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Add the new user
    success = add_user(registration.username, registration.password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )
    
    return {
        "message": "Admin registration successful",
        "username": registration.username,
        "note": "You can now login with your credentials"
    }