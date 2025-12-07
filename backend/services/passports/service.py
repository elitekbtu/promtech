from typing import Optional
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from pathlib import Path
import os
from pypdf import PdfReader
from io import BytesIO
from datetime import datetime
from models import WaterObject, PassportText
from .schemas import PassportTextResponse


# File storage configuration from environment
PASSPORT_STORAGE_PATH = os.getenv("PASSPORT_STORAGE_PATH", "uploads/passports")
PASSPORT_BASE_URL = os.getenv("PASSPORT_BASE_URL", "/uploads/passports")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10485760))  # 10MB default

# Create storage directory if it doesn't exist
Path(PASSPORT_STORAGE_PATH).mkdir(parents=True, exist_ok=True)


class PassportService:
    """Service layer for passport document management"""
    
    @staticmethod
    def save_pdf_file(file_data: bytes, object_id: int) -> str:
        """
        Save passport PDF file to disk
        
        Args:
            file_data: PDF file bytes
            object_id: Water object ID
            
        Returns:
            Relative file path for storage in database
        """
        filename = f"object_{object_id}_passport.pdf"
        filepath = Path(PASSPORT_STORAGE_PATH) / filename
        
        with open(filepath, 'wb') as f:
            f.write(file_data)
        
        # Return URL path for database storage
        return f"{PASSPORT_BASE_URL}/{filename}"
    
    @staticmethod
    def extract_text_from_pdf(file_data: bytes) -> str:
        """
        Extract all text from PDF file
        
        Args:
            file_data: PDF file bytes
            
        Returns:
            Extracted text content
        """
        try:
            # Read PDF from bytes
            pdf_file = BytesIO(file_data)
            reader = PdfReader(pdf_file)
            
            # Extract text from all pages
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
            
            return text.strip()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to extract text from PDF: {str(e)}"
            )
    
    @staticmethod
    def parse_passport_sections(full_text: str) -> dict:
        """
        Parse passport text into structured sections
        
        This is a simple parser. In production, you might use more sophisticated
        NLP techniques or regex patterns based on your passport document format.
        
        Args:
            full_text: Complete extracted text
            
        Returns:
            Dictionary with section names and content
        """
        sections = {
            "general_info": None,
            "technical_params": None,
            "ecological_state": None,
            "recommendations": None
        }
        
        # Simple keyword-based parsing
        # You can customize these keywords based on your actual passport format
        text_lower = full_text.lower()
        
        # Try to extract sections based on common keywords
        # This is a basic implementation - adjust based on your document structure
        
        if "общая информация" in text_lower or "general information" in text_lower:
            # Extract general info section (simplified)
            start_idx = text_lower.find("общая информация")
            if start_idx == -1:
                start_idx = text_lower.find("general information")
            if start_idx != -1:
                end_idx = text_lower.find("технические параметры", start_idx)
                if end_idx == -1:
                    end_idx = text_lower.find("technical parameters", start_idx)
                if end_idx != -1:
                    sections["general_info"] = full_text[start_idx:end_idx].strip()
        
        if "технические параметры" in text_lower or "technical parameters" in text_lower:
            start_idx = text_lower.find("технические параметры")
            if start_idx == -1:
                start_idx = text_lower.find("technical parameters")
            if start_idx != -1:
                end_idx = text_lower.find("экологическое состояние", start_idx)
                if end_idx == -1:
                    end_idx = text_lower.find("ecological state", start_idx)
                if end_idx != -1:
                    sections["technical_params"] = full_text[start_idx:end_idx].strip()
        
        if "экологическое состояние" in text_lower or "ecological state" in text_lower:
            start_idx = text_lower.find("экологическое состояние")
            if start_idx == -1:
                start_idx = text_lower.find("ecological state")
            if start_idx != -1:
                end_idx = text_lower.find("рекомендации", start_idx)
                if end_idx == -1:
                    end_idx = text_lower.find("recommendations", start_idx)
                if end_idx != -1:
                    sections["ecological_state"] = full_text[start_idx:end_idx].strip()
        
        if "рекомендации" in text_lower or "recommendations" in text_lower:
            start_idx = text_lower.find("рекомендации")
            if start_idx == -1:
                start_idx = text_lower.find("recommendations")
            if start_idx != -1:
                sections["recommendations"] = full_text[start_idx:].strip()
        
        return sections
    
    @staticmethod
    async def upload_passport(
        db: Session,
        object_id: int,
        file: UploadFile
    ) -> tuple[str, bool, str]:
        """
        Upload passport PDF and extract text
        
        Args:
            db: Database session
            object_id: Water object ID
            file: Uploaded PDF file
            
        Returns:
            Tuple of (pdf_url, text_extracted, extraction_method)
        """
        # Verify water object exists
        water_object = db.query(WaterObject).filter(
            WaterObject.id == object_id,
            WaterObject.deleted_at.is_(None)
        ).first()
        
        if not water_object:
            raise HTTPException(
                status_code=404,
                detail=f"Water object with ID {object_id} not found"
            )
        
        # Validate file type (content-type header)
        if not file.content_type == "application/pdf":
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are accepted. Content-Type must be application/pdf"
            )
        
        # Validate filename extension
        if file.filename and not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are accepted. File must have .pdf extension"
            )
        
        # Read file data
        file_data = await file.read()
        
        # Validate file size
        if len(file_data) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
            )
        
        # Validate PDF magic number (file signature)
        if not file_data.startswith(b'%PDF'):
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF file. File does not have valid PDF signature"
            )
        
        # Save PDF file
        pdf_url = PassportService.save_pdf_file(file_data, object_id)
        
        # Update water object with PDF URL and passport date
        water_object.pdf_url = pdf_url
        water_object.passport_date = datetime.now().date()
        
        # Recalculate priority based on new passport date
        from services.objects.service import WaterObjectService
        water_object.priority = WaterObjectService.calculate_priority(
            technical_condition=water_object.technical_condition,
            passport_date=water_object.passport_date
        )
        water_object.priority_level = WaterObjectService.get_priority_level(water_object.priority)
        
        db.commit()
        
        # Extract text from PDF
        text_extracted = False
        extraction_method = None
        
        try:
            full_text = PassportService.extract_text_from_pdf(file_data)
            
            if full_text:
                # Parse sections
                sections = PassportService.parse_passport_sections(full_text)
                
                # Check if we found any sections
                has_sections = any(v is not None for v in sections.values())
                extraction_method = "sections" if has_sections else "full_text"
                
                # Save or update passport text
                passport_text = db.query(PassportText).filter(
                    PassportText.object_id == object_id
                ).first()
                
                if passport_text:
                    # Update existing
                    passport_text.full_text = full_text
                    passport_text.general_info = sections.get("general_info")
                    passport_text.technical_params = sections.get("technical_params")
                    passport_text.ecological_state = sections.get("ecological_state")
                    passport_text.recommendations = sections.get("recommendations")
                else:
                    # Create new
                    passport_text = PassportText(
                        object_id=object_id,
                        full_text=full_text,
                        general_info=sections.get("general_info"),
                        technical_params=sections.get("technical_params"),
                        ecological_state=sections.get("ecological_state"),
                        recommendations=sections.get("recommendations")
                    )
                    db.add(passport_text)
                
                db.commit()
                text_extracted = True
        except Exception as e:
            # Log error but don't fail the upload
            print(f"Warning: Text extraction failed for object {object_id}: {str(e)}")
            # PDF is still saved, just no text extracted
        
        return pdf_url, text_extracted, extraction_method
    
    @staticmethod
    def get_passport_text(db: Session, object_id: int) -> Optional[PassportTextResponse]:
        """
        Get passport text for a water object
        
        Args:
            db: Database session
            object_id: Water object ID
            
        Returns:
            PassportTextResponse or None if not found
        """
        # Verify water object exists
        water_object = db.query(WaterObject).filter(
            WaterObject.id == object_id,
            WaterObject.deleted_at.is_(None)
        ).first()
        
        if not water_object:
            raise HTTPException(
                status_code=404,
                detail=f"Water object with ID {object_id} not found"
            )
        
        # Get passport text
        passport_text = db.query(PassportText).filter(
            PassportText.object_id == object_id
        ).first()
        
        if not passport_text:
            return None
        
        return PassportTextResponse.model_validate(passport_text)
    
    @staticmethod
    def delete_passport(db: Session, object_id: int) -> bool:
        """
        Delete passport PDF and text for a water object
        
        Args:
            db: Database session
            object_id: Water object ID
            
        Returns:
            True if deleted, False if not found
        """
        # Verify water object exists
        water_object = db.query(WaterObject).filter(
            WaterObject.id == object_id,
            WaterObject.deleted_at.is_(None)
        ).first()
        
        if not water_object:
            return False
        
        # Delete PDF file if exists
        if water_object.pdf_url:
            # Extract filename from URL
            filename = water_object.pdf_url.split("/")[-1]
            filepath = Path(PASSPORT_STORAGE_PATH) / filename
            if filepath.exists():
                filepath.unlink()
            
            # Clear PDF URL from water object
            water_object.pdf_url = None
        
        # Delete passport text if exists
        passport_text = db.query(PassportText).filter(
            PassportText.object_id == object_id
        ).first()
        
        if passport_text:
            db.delete(passport_text)
        
        db.commit()
        return True
