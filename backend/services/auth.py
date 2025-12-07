"""
Authentication service for admin access
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from db import get_db
from models import AdminUser

# Configuration from environment
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token scheme
security = HTTPBearer()

def get_user_by_username(db: Session, username: str) -> Optional[AdminUser]:
    """Get admin user by username from database"""
    return db.query(AdminUser).filter(AdminUser.username == username).first()

def create_admin_user(db: Session, username: str, password: str) -> AdminUser:
    """Create a new admin user in database"""
    hashed_password = get_password_hash(password)
    admin_user = AdminUser(
        username=username,
        hashed_password=hashed_password,
        created_at=datetime.utcnow()
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    return admin_user

def add_user(username: str, password: str, db: Session) -> bool:
    """Add a new user to database"""
    existing_user = get_user_by_username(db, username)
    if existing_user:
        return False
    
    create_admin_user(db, username, password)
    return True

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def authenticate_admin(username: str, password: str, db: Session) -> bool:
    """Authenticate admin credentials against database"""
    user = get_user_by_username(db, username)
    if not user:
        return False
    
    return verify_password(password, user.hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify JWT token and return payload"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception

def require_admin(token_payload: dict = Depends(verify_token), db: Session = Depends(get_db)) -> dict:
    """Dependency to require admin authentication"""
    username = token_payload.get("sub")
    
    if not username or not token_payload.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Verify user still exists in database
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return token_payload