from fastapi import HTTPException, Depends, UploadFile, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import get_db
from models.user import User, UserRole
from services.auth.schemas import UserRead, Token, TokenData
from typing import Optional
from datetime import datetime, timedelta
import os
from pathlib import Path
import jwt

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

AVATARS_DIR = Path("uploads/avatars")
AVATARS_DIR.mkdir(parents=True, exist_ok=True)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(password, password_hash)


def create_access_token(user_id: int, email: str, role: UserRole, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        user_id: User's ID
        email: User's email
        role: User's role
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(user_id),
        "email": email,
        "role": role.value,
        "exp": expire
    }
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> TokenData:
    """
    Decode and validate JWT access token
    
    Args:
        token: JWT token string
        
    Returns:
        TokenData with user information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        email: str = payload.get("email")
        role_str: str = payload.get("role")
        
        if user_id is None or email is None or role_str is None:
            raise credentials_exception
        
        # Convert role string to UserRole enum
        try:
            role = UserRole(role_str)
        except ValueError:
            raise credentials_exception
        
        return TokenData(user_id=user_id, email=email, role=role)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise credentials_exception


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Dependency to get current authenticated user from JWT token
    
    Args:
        token: JWT token from Authorization header
        db: Database session
        
    Returns:
        Current authenticated User
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token_data = decode_access_token(token)
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.deleted_at:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deleted",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_current_user_role(current_user: User = Depends(get_current_user)) -> UserRole:
    """
    Dependency to get current user's role
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User's role
    """
    return current_user.role


def require_expert(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to require expert role
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if they have expert role
        
    Raises:
        HTTPException: If user is not an expert
    """
    if current_user.role != UserRole.expert:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This operation requires expert role",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return current_user


def save_avatar_file(file_data: bytes, user_id: int) -> str:
    """
    Save avatar file to disk
    
    Args:
        file_data: Image file bytes
        user_id: User ID
        
    Returns:
        Filename of saved avatar
    """
    filename = f"user_{user_id}_avatar.jpg"
    filepath = AVATARS_DIR / filename
    
    with open(filepath, 'wb') as f:
        f.write(file_data)
    
    return filename


async def create_user(
    name: str,
    surname: str,
    email: str,
    phone: str,
    password: str,
    avatar_file: Optional[UploadFile] = None,
    db: Session = Depends(get_db)
) -> Token:
    """
    Create a new user with optional avatar
    
    Args:
        name: User's first name
        surname: User's last name
        email: User's email
        phone: User's phone number
        password: User's password
        avatar_file: Optional avatar image file
        db: Database session
        
    Returns:
        Created user data (with role field)
    """
    # Check if email already exists
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if phone already exists
    if db.query(User).filter(User.phone == phone).first():
        raise HTTPException(status_code=400, detail="Phone already registered")

    # Create user without avatar first (default role is guest)
    new_user = User(
        name=name,
        surname=surname,
        email=email,
        phone=phone,
        password_hash=pwd_context.hash(password),
        avatar=None,
        role=UserRole.guest  # Default to guest role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Save avatar if provided
    if avatar_file:
        try:
            # Read file contents
            avatar_data = await avatar_file.read()
            
            # Save avatar file
            avatar_filename = save_avatar_file(avatar_data, new_user.id)
            
            # Update user with avatar filename
            new_user.avatar = avatar_filename
            db.commit()
            db.refresh(new_user)
        except Exception as e:
            # If avatar save fails, still return user but log error
            print(f"Error saving avatar for user {new_user.id}: {str(e)}")

    access_token = create_access_token(
        user_id=new_user.id,
        email=new_user.email,
        role=new_user.role
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserRead.model_validate(new_user)
    )


def login_user(email: str, password: str, db: Session = Depends(get_db)) -> Token:
    """
    Login user with email and password
    
    Args:
        email: User's email
        password: User's password
        db: Database session
        
    Returns:
        User data (with role field)
    """
    user = db.query(User).filter(User.email == email).first()
    
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if user.deleted_at:
        raise HTTPException(status_code=401, detail="User is deleted")
    
    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserRead.model_validate(user)
    )


def get_user(user_id: int, db: Session = Depends(get_db)) -> UserRead:
    """
    Get user by ID
    
    Args:
        user_id: User's ID
        db: Database session
        
    Returns:
        User data
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.deleted_at:
        raise HTTPException(status_code=404, detail="User is deleted")

    return UserRead.from_orm(user)


async def update_user_avatar(
    user_id: int,
    avatar_file: UploadFile,
    db: Session = Depends(get_db)
) -> UserRead:
    """
    Update user's avatar
    
    Args:
        user_id: User's ID
        avatar_file: New avatar image file
        db: Database session
        
    Returns:
        Updated user data
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.deleted_at:
        raise HTTPException(status_code=404, detail="User is deleted")
    
    try:
        # Read file contents
        avatar_data = await avatar_file.read()
        
        # Delete old avatar if exists
        if user.avatar:
            old_avatar_path = AVATARS_DIR / user.avatar
            if old_avatar_path.exists():
                os.remove(old_avatar_path)
        
        # Save new avatar
        avatar_filename = save_avatar_file(avatar_data, user.id)
        
        # Update user
        user.avatar = avatar_filename
        db.commit()
        db.refresh(user)
        
        return UserRead.from_orm(user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating avatar: {str(e)}")
