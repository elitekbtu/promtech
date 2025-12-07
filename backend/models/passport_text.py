from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class PassportText(Base):
    """
    Storage for water body passport document text content.
    Used for full-text search and RAG context retrieval.
    """
    __tablename__ = "passport_texts"

    id = Column(Integer, primary_key=True, index=True)
    
    # Link to water object
    water_object_id = Column(Integer, ForeignKey("water_objects.id"), nullable=False, index=True)
    
    # Document metadata
    document_title = Column(String, nullable=True)
    document_date = Column(DateTime, nullable=True)
    
    # Content sections (for structured retrieval)
    full_text = Column(Text, nullable=False)  # Complete passport text
    general_info = Column(Text, nullable=True)  # Общие сведения
    technical_params = Column(Text, nullable=True)  # Технические параметры
    ecological_state = Column(Text, nullable=True)  # Экологическое состояние
    recommendations = Column(Text, nullable=True)  # Рекомендации
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<PassportText(id={self.id}, water_object_id={self.water_object_id}, title='{self.document_title}')>"
