from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PassportUploadResponse(BaseModel):
    """Response after successful passport upload"""
    object_id: int = Field(..., description="Water object ID")
    pdf_url: str = Field(..., description="URL to access the PDF")
    text_extracted: bool = Field(..., description="Whether text extraction was successful")
    extraction_method: Optional[str] = Field(None, description="Method used for extraction (full_text, sections, etc.)")
    message: str = Field(..., description="Success message")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "object_id": 1,
                "pdf_url": "/uploads/passports/object_1_passport.pdf",
                "text_extracted": True,
                "extraction_method": "sections",
                "message": "Passport uploaded and text extracted successfully"
            }
        }
    }


class PassportTextResponse(BaseModel):
    """Response containing passport text content"""
    object_id: int
    full_text: Optional[str] = Field(None, description="Complete extracted text")
    general_info: Optional[str] = Field(None, description="General information section")
    technical_params: Optional[str] = Field(None, description="Technical parameters section")
    ecological_state: Optional[str] = Field(None, description="Ecological state section")
    recommendations: Optional[str] = Field(None, description="Recommendations section")
    created_at: datetime
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "object_id": 1,
                "full_text": "Complete passport text...",
                "general_info": "Name: Озеро Барыккол...",
                "technical_params": "Area: 12.5 km², Depth: 8m...",
                "ecological_state": "Good condition, clean water...",
                "recommendations": "Regular monitoring required...",
                "created_at": "2024-01-15T10:30:00"
            }
        }
    }
