from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Enum as SQLEnum
from sqlalchemy.orm import validates
from database import Base
import enum


class ResourceType(str, enum.Enum):
    """Types of water resources"""
    lake = "озеро"
    canal = "канал"
    reservoir = "водохранилище"
    river = "река"
    other = "другое"


class WaterType(str, enum.Enum):
    """Water salinity classification"""
    fresh = "пресная"
    non_fresh = "непресная"


class FaunaType(str, enum.Enum):
    """Fauna presence classification"""
    fish_bearing = "рыбопродуктивная"
    non_fish_bearing = "нерыбопродуктивная"


class PriorityLevel(str, enum.Enum):
    """Priority classification based on inspection score"""
    high = "высокий"      # >= 10
    medium = "средний"    # 6-9
    low = "низкий"        # <= 5


class WaterObject(Base):
    """
    Water object model representing lakes, canals, reservoirs, and other water bodies.
    
    Priority calculation formula: (6 - technical_condition) * 3 + passport_age_years
    - technical_condition: 1-5 scale (1=worst, 5=best)
    - passport_age_years: calculated from passport_date to current date
    """
    __tablename__ = "water_objects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    region = Column(String, nullable=False, index=True)  # Улытауский район, etc.
    
    # Resource classification
    resource_type = Column(SQLEnum(ResourceType), nullable=False, index=True)
    water_type = Column(SQLEnum(WaterType), nullable=True)
    fauna = Column(SQLEnum(FaunaType), nullable=True)
    
    # Passport and condition
    passport_date = Column(DateTime, nullable=True)  # Date of last passport inspection
    technical_condition = Column(Integer, nullable=False, default=3)  # 1-5 scale
    
    # Geographic coordinates
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Passport document reference
    pdf_url = Column(String, nullable=True)  # URL or path to passport PDF
    
    # Priority fields (computed)
    priority = Column(Integer, nullable=False, default=0, index=True)  # Computed score
    priority_level = Column(SQLEnum(PriorityLevel), nullable=False, default=PriorityLevel.low, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    deleted_at = Column(DateTime, nullable=True)

    @validates('technical_condition')
    def validate_technical_condition(self, key, value):
        """Ensure technical_condition is between 1 and 5"""
        if value is not None and (value < 1 or value > 5):
            raise ValueError("technical_condition must be between 1 and 5")
        return value

    def calculate_priority(self) -> int:
        """
        Calculate inspection priority score.
        Formula: (6 - technical_condition) * 3 + passport_age_years
        
        Returns:
            int: Priority score (higher = more urgent)
        """
        from datetime import datetime
        
        # Base score from technical condition (worse condition = higher score)
        condition_score = (6 - self.technical_condition) * 3
        
        # Additional score from passport age
        passport_age = 0
        if self.passport_date:
            passport_age = (datetime.now() - self.passport_date).days // 365
        
        return condition_score + passport_age

    def get_priority_level(self, score: int) -> PriorityLevel:
        """
        Map priority score to level.
        
        Args:
            score: Priority score from calculate_priority()
            
        Returns:
            PriorityLevel: high (>=10), medium (6-9), or low (<=5)
        """
        if score >= 10:
            return PriorityLevel.high
        elif score >= 6:
            return PriorityLevel.medium
        else:
            return PriorityLevel.low

    def update_priority(self):
        """Calculate and update priority fields"""
        self.priority = self.calculate_priority()
        self.priority_level = self.get_priority_level(self.priority)

    def __repr__(self):
        return f"<WaterObject(id={self.id}, name='{self.name}', region='{self.region}', priority={self.priority})>"
