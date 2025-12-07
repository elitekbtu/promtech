from typing import List, Optional
from pydantic import BaseModel, Field
from models import PriorityLevel


class PriorityStatistics(BaseModel):
    """Statistics about priority levels"""
    high: int = Field(..., description="Number of water objects with HIGH priority")
    medium: int = Field(..., description="Number of water objects with MEDIUM priority")
    low: int = Field(..., description="Number of water objects with LOW priority")
    total: int = Field(..., description="Total number of water objects")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "high": 15,
                "medium": 23,
                "low": 42,
                "total": 80
            }
        }
    }


class PriorityTableItem(BaseModel):
    """Water object with priority information for priority dashboard table"""
    id: int
    name: str
    region: str
    resource_type: str
    technical_condition: int = Field(..., ge=1, le=5)
    passport_date: Optional[str] = None
    priority: int = Field(..., description="Calculated priority score")
    priority_level: PriorityLevel
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "Озеро Барыккол",
                "region": "Акмолинская область",
                "resource_type": "lake",
                "technical_condition": 2,
                "passport_date": "2010-05-15",
                "priority": 18,
                "priority_level": "high"
            }
        }
    }


class PriorityTableResponse(BaseModel):
    """Paginated response for priority table"""
    items: List[PriorityTableItem]
    total: int
    limit: int
    offset: int
    has_more: bool
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "items": [
                    {
                        "id": 1,
                        "name": "Озеро Барыккол",
                        "region": "Акмолинская область",
                        "resource_type": "lake",
                        "technical_condition": 2,
                        "passport_date": "2010-05-15",
                        "priority": 18,
                        "priority_level": "high"
                    }
                ],
                "total": 80,
                "limit": 50,
                "offset": 0,
                "has_more": True
            }
        }
    }


class PriorityFilter(BaseModel):
    """Filters specific to priority dashboard"""
    priority_level: Optional[PriorityLevel] = Field(None, description="Filter by priority level")
    min_priority: Optional[int] = Field(None, ge=0, description="Minimum priority score")
    max_priority: Optional[int] = Field(None, ge=0, description="Maximum priority score")
    region: Optional[str] = Field(None, description="Filter by region")
    resource_type: Optional[str] = Field(None, description="Filter by resource type")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "priority_level": "high",
                "min_priority": 10,
                "region": "Акмолинская область"
            }
        }
    }
