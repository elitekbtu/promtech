from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from database import Base
from sqlalchemy.orm import relationship
import enum


class UserRole(str, enum.Enum):
    """User roles for GidroAtlas system"""
    guest = "guest"    # View only, no access to priorities
    expert = "expert"  # Full access including priorities and analytics


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    avatar = Column(String, nullable=True)

    role = Column(SQLEnum(UserRole), default=UserRole.guest, nullable=False)  # guest or expert

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_at = Column(DateTime, nullable=True)
