from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from services.auth.service import create_user, login_user, get_user, update_user_avatar
from services.auth.schemas import UserLogin, UserRead, Token
from typing import Optional
from pydantic import EmailStr, ValidationError
import re

router = APIRouter()


def validate_email(email: str) -> str:
    """Validate email format"""
    email = email.strip().lower()
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise HTTPException(status_code=422, detail="Invalid email format")
    return email


def validate_password(password: str) -> str:
    """Validate password requirements"""
    if len(password) < 8:
        raise HTTPException(status_code=422, detail="Password must be at least 8 characters long")
    if len(password) > 72:
        raise HTTPException(status_code=422, detail="Password must be at most 72 characters long")
    return password


def validate_name(name: str, field_name: str) -> str:
    """Validate name fields"""
    name = name.strip()
    if len(name) < 2:
        raise HTTPException(status_code=422, detail=f"{field_name} must be at least 2 characters long")
    if len(name) > 50:
        raise HTTPException(status_code=422, detail=f"{field_name} must be at most 50 characters long")
    return name


@router.post("/register", response_model=Token, tags=["auth"])
async def register(
    name: str = Form(..., description="User's first name", example="John"),
    surname: str = Form(..., description="User's last name", example="Doe"),
    email: str = Form(..., description="User's email address", example="john.doe@example.com"),
    phone: str = Form(..., description="User's phone number", example="+77001234567"),
    password: str = Form(..., description="User's password (8-72 characters)", example="SecurePass123"),
    avatar: Optional[UploadFile] = File(None, description="User's avatar image (optional)"),
    db: Session = Depends(get_db)
):
    """
    Register a new expert user with optional avatar image for Face ID.
    
    **Registration creates expert users only.**
    All registered users receive the expert role.
    
    Unauthenticated users can access the system as guests without registration.
    
    Returns JWT token with user data.
    
    The token should be stored by the frontend and sent in Authorization header for subsequent requests.
    """
    # Validate inputs
    name = validate_name(name, "Name")
    surname = validate_name(surname, "Surname")
    email = validate_email(email)
    password = validate_password(password)
    
    # Force role to expert (registration is expert-only)
    role = "expert"
    
    return await create_user(
        name=name,
        surname=surname,
        email=email,
        phone=phone,
        password=password,
        role=role,
        avatar_file=avatar,
        db=db
    )
@router.post("/token", response_model=Token, tags=["auth"])
async def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2-compatible token endpoint for Swagger UI authentication.
    
    Use email as username.
    Returns JWT access token if credentials are valid.
    """
    return login_user(
        email=form_data.username,  # Use email as username
        password=form_data.password,
        db=db
    )


@router.post("/login", response_model=Token, tags=["auth"])
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login with email and password (JSON body).
    
    **Expert users only** - Login is restricted to registered experts.
    
    Unauthenticated users automatically have guest access to view water objects
    without priority information. No login required for guest functionality.
    
    Returns JWT token with user data if credentials are valid.
    The token should be stored and sent in Authorization header:
    Authorization: Bearer <access_token>
    
    Note: For Swagger UI, use the /token endpoint instead.
    """
    return login_user(
        email=credentials.email,
        password=credentials.password,
        db=db
    )


@router.post("/logout", tags=["auth"])
async def logout():
    """
    Logout endpoint.
    """
    return {
        "message": "Logout successful.",
        "success": True
    }


@router.put("/{user_id}/avatar", response_model=UserRead, tags=["auth"])
async def update_avatar(
    user_id: int,
    avatar: UploadFile = File(..., description="New avatar image"),
    db: Session = Depends(get_db)
):
    """
    Update user's avatar image for Face ID.
    
    This will replace the existing avatar with a new one.
    """
    return await update_user_avatar(
        user_id=user_id,
        avatar_file=avatar,
        db=db
    )
