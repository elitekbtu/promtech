from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from models import ResourceType, WaterType, FaunaType, PriorityLevel


class WaterObjectBase(BaseModel):
    """Base schema for water object with common fields"""
    name: str = Field(..., min_length=1, max_length=255, description="Water object name")
    region: str = Field(..., min_length=1, max_length=255, description="Administrative region")
    resource_type: ResourceType = Field(..., description="Type of water resource")
    water_type: Optional[WaterType] = Field(None, description="Water salinity type")
    fauna: Optional[FaunaType] = Field(None, description="Fauna presence")
    passport_date: Optional[datetime] = Field(None, description="Date of last passport inspection")
    technical_condition: int = Field(..., ge=1, le=5, description="Technical condition score (1=worst, 5=best)")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude coordinate")
    pdf_url: Optional[str] = Field(None, max_length=500, description="URL to passport PDF document")

    @field_validator('technical_condition')
    @classmethod
    def validate_technical_condition(cls, v):
        if v < 1 or v > 5:
            raise ValueError('technical_condition must be between 1 and 5')
        return v


class WaterObjectCreate(WaterObjectBase):
    """Schema for creating a new water object"""
    pass


class WaterObjectUpdate(BaseModel):
    """Schema for updating an existing water object (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    region: Optional[str] = Field(None, min_length=1, max_length=255)
    resource_type: Optional[ResourceType] = None
    water_type: Optional[WaterType] = None
    fauna: Optional[FaunaType] = None
    passport_date: Optional[datetime] = None
    technical_condition: Optional[int] = Field(None, ge=1, le=5)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    pdf_url: Optional[str] = Field(None, max_length=500)

    @field_validator('technical_condition')
    @classmethod
    def validate_technical_condition(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('technical_condition must be between 1 and 5')
        return v


class WaterObjectResponse(WaterObjectBase):
    """Schema for water object response (includes computed fields)"""
    id: int
    priority: int = Field(..., description="Computed priority score")
    priority_level: PriorityLevel = Field(..., description="Priority level classification")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WaterObjectGuestResponse(BaseModel):
    """Schema for guest users (no priority information)"""
    id: int
    name: str
    region: str
    resource_type: ResourceType
    water_type: Optional[WaterType]
    fauna: Optional[FaunaType]
    passport_date: Optional[datetime]
    latitude: Optional[float]
    longitude: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WaterObjectFilter(BaseModel):
    """Schema for filtering water objects"""
    region: Optional[str] = Field(None, description="Filter by region")
    resource_type: Optional[ResourceType] = Field(None, description="Filter by resource type")
    water_type: Optional[WaterType] = Field(None, description="Filter by water type")
    fauna: Optional[FaunaType] = Field(None, description="Filter by fauna type")
    min_technical_condition: Optional[int] = Field(None, ge=1, le=5, description="Minimum technical condition")
    max_technical_condition: Optional[int] = Field(None, ge=1, le=5, description="Maximum technical condition")
    min_priority: Optional[int] = Field(None, ge=0, description="Minimum priority score")
    max_priority: Optional[int] = Field(None, ge=0, description="Maximum priority score")
    priority_level: Optional[PriorityLevel] = Field(None, description="Filter by priority level")
    passport_date_from: Optional[datetime] = Field(None, description="Passport date from")
    passport_date_to: Optional[datetime] = Field(None, description="Passport date to")


class PaginationParams(BaseModel):
    """Schema for pagination parameters"""
    limit: int = Field(100, gt=0, le=100, description="Maximum number of items to return")
    offset: int = Field(0, ge=0, description="Number of items to skip")
    sort_by: str = Field("id", description="Field to sort by")
    sort_order: str = Field("asc", pattern="^(asc|desc)$", description="Sort order: asc or desc")


class WaterObjectListResponse(BaseModel):
    """Schema for paginated water object list response"""
    items: List[WaterObjectResponse]
    total: int = Field(..., description="Total number of items matching filter")
    limit: int
    offset: int
    has_more: bool = Field(..., description="Whether there are more items available")

    class Config:
        from_attributes = True
