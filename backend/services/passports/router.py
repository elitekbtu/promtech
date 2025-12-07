from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from services.passports.service import PassportService
from services.passports.schemas import PassportUploadResponse, PassportTextResponse
from services.auth.service import get_current_user, require_expert
from typing import Optional


router = APIRouter(prefix="/passports", tags=["Passports"])


@router.post(
    "/{object_id}/upload",
    response_model=PassportUploadResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_expert)],
    summary="Upload passport PDF for water object",
    description="Upload a PDF passport document for a water object. Text will be automatically extracted. **Requires expert role.**"
)
async def upload_passport(
    object_id: int,
    file: UploadFile = File(..., description="PDF passport document"),
    db: Session = Depends(get_db)
):
    """
    Upload passport PDF document for a water object.
    
    - Validates PDF format
    - Saves file to disk
    - Extracts text automatically
    - Parses into structured sections
    - Updates water object with PDF URL
    
    **Requires expert role** - Only experts can upload passport documents.
    """
    
    pdf_url, text_extracted, extraction_method = await PassportService.upload_passport(
        db=db,
        object_id=object_id,
        file=file
    )
    
    return PassportUploadResponse(
        object_id=object_id,
        pdf_url=pdf_url,
        text_extracted=text_extracted,
        extraction_method=extraction_method,
        message="Passport uploaded successfully" if text_extracted else "Passport uploaded but text extraction failed"
    )


@router.get(
    "/{object_id}/text",
    response_model=Optional[PassportTextResponse],
    responses={
        404: {"description": "Water object or passport not found"}
    },
    summary="Get passport text content",
    description="Retrieve extracted text content from a water object's passport document."
)
async def get_passport_text(
    object_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get extracted passport text content.
    
    Returns:
    - Full text content
    - Structured sections (if successfully parsed)
    - Creation timestamp
    
    Returns 404 if water object doesn't exist or has no passport.
    
    **Requires authentication** - Both guests and experts can view passport text.
    """
    
    passport_text = PassportService.get_passport_text(db, object_id)
    
    if not passport_text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No passport text found for water object {object_id}"
        )
    
    return passport_text


@router.delete(
    "/{object_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"description": "Water object not found"}
    },
    summary="Delete passport document",
    description="Delete passport PDF file and extracted text for a water object."
)
async def delete_passport(
    object_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_expert)
):
    """
    Delete passport PDF and text data.
    
    - Removes PDF file from disk
    - Deletes passport text from database
    - Clears PDF URL from water object
    
    **Requires expert role** - Only experts can delete passport documents.
    """
    
    deleted = PassportService.delete_passport(db, object_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Water object with ID {object_id} not found"
        )
    
    return None
