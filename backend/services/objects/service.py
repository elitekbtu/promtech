from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, asc, desc, func
from models import WaterObject, PriorityLevel
from .schemas import (
    WaterObjectCreate,
    WaterObjectUpdate,
    WaterObjectFilter,
    PaginationParams,
)


class WaterObjectService:
    """Service layer for water object business logic"""

    @staticmethod
    def calculate_priority(technical_condition: int, passport_date: Optional[datetime]) -> int:
        """
        Calculate inspection priority score.
        Formula: (6 - technical_condition) * 3 + passport_age_years
        
        Args:
            technical_condition: Technical condition score (1-5)
            passport_date: Date of last passport inspection
            
        Returns:
            Priority score (higher = more urgent)
        """
        # Base score from technical condition (worse condition = higher score)
        condition_score = (6 - technical_condition) * 3
        
        # Additional score from passport age
        passport_age = 0
        if passport_date:
            passport_age = (datetime.now() - passport_date).days // 365
        
        return condition_score + passport_age

    @staticmethod
    def get_priority_level(priority_score: int) -> PriorityLevel:
        """
        Map priority score to priority level.
        
        Args:
            priority_score: Calculated priority score
            
        Returns:
            PriorityLevel: high (>=10), medium (6-9), or low (<=5)
        """
        if priority_score >= 10:
            return PriorityLevel.high
        elif priority_score >= 6:
            return PriorityLevel.medium
        else:
            return PriorityLevel.low

    @staticmethod
    def create(db: Session, water_object_data: WaterObjectCreate) -> WaterObject:
        """
        Create a new water object with calculated priority.
        
        Args:
            db: Database session
            water_object_data: Water object creation data
            
        Returns:
            Created WaterObject instance
        """
        # Calculate priority
        priority = WaterObjectService.calculate_priority(
            water_object_data.technical_condition,
            water_object_data.passport_date
        )
        priority_level = WaterObjectService.get_priority_level(priority)
        
        # Create database object
        db_water_object = WaterObject(
            **water_object_data.model_dump(),
            priority=priority,
            priority_level=priority_level
        )
        
        db.add(db_water_object)
        db.commit()
        db.refresh(db_water_object)
        
        return db_water_object

    @staticmethod
    def get_by_id(db: Session, water_object_id: int) -> Optional[WaterObject]:
        """
        Get water object by ID.
        
        Args:
            db: Database session
            water_object_id: Water object ID
            
        Returns:
            WaterObject or None if not found
        """
        return db.query(WaterObject).filter(
            WaterObject.id == water_object_id,
            WaterObject.deleted_at.is_(None)
        ).first()

    @staticmethod
    def update(
        db: Session,
        water_object_id: int,
        water_object_data: WaterObjectUpdate
    ) -> Optional[WaterObject]:
        """
        Update an existing water object.
        
        Args:
            db: Database session
            water_object_id: Water object ID
            water_object_data: Update data
            
        Returns:
            Updated WaterObject or None if not found
        """
        db_water_object = WaterObjectService.get_by_id(db, water_object_id)
        if not db_water_object:
            return None
        
        # Update fields
        update_data = water_object_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_water_object, field, value)
        
        # Recalculate priority if relevant fields changed
        if 'technical_condition' in update_data or 'passport_date' in update_data:
            db_water_object.update_priority()
        
        db_water_object.updated_at = datetime.now()
        db.commit()
        db.refresh(db_water_object)
        
        return db_water_object

    @staticmethod
    def delete(db: Session, water_object_id: int) -> bool:
        """
        Soft delete a water object.
        
        Args:
            db: Database session
            water_object_id: Water object ID
            
        Returns:
            True if deleted, False if not found
        """
        db_water_object = WaterObjectService.get_by_id(db, water_object_id)
        if not db_water_object:
            return False
        
        db_water_object.deleted_at = datetime.now()
        db.commit()
        
        return True

    @staticmethod
    def list_with_filters(
        db: Session,
        filters: Optional[WaterObjectFilter] = None,
        pagination: Optional[PaginationParams] = None
    ) -> tuple[List[WaterObject], int]:
        """
        List water objects with filtering, sorting, and pagination.
        
        Args:
            db: Database session
            filters: Optional filter parameters
            pagination: Optional pagination parameters
            
        Returns:
            Tuple of (list of WaterObjects, total count)
        """
        # Base query
        query = db.query(WaterObject).filter(WaterObject.deleted_at.is_(None))
        
        # Apply filters
        if filters:
            filter_conditions = []
            
            # Search by name or region (case-insensitive)
            if filters.search:
                search_pattern = f"%{filters.search}%"
                filter_conditions.append(
                    or_(
                        func.lower(WaterObject.name).like(func.lower(search_pattern)),
                        func.lower(WaterObject.region).like(func.lower(search_pattern))
                    )
                )
            
            if filters.region:
                filter_conditions.append(WaterObject.region == filters.region)
            
            if filters.resource_type:
                filter_conditions.append(WaterObject.resource_type == filters.resource_type)
            
            if filters.water_type:
                filter_conditions.append(WaterObject.water_type == filters.water_type)
            
            if filters.fauna:
                filter_conditions.append(WaterObject.fauna == filters.fauna)
            
            if filters.min_technical_condition is not None:
                filter_conditions.append(WaterObject.technical_condition >= filters.min_technical_condition)
            
            if filters.max_technical_condition is not None:
                filter_conditions.append(WaterObject.technical_condition <= filters.max_technical_condition)
            
            if filters.min_priority is not None:
                filter_conditions.append(WaterObject.priority >= filters.min_priority)
            
            if filters.max_priority is not None:
                filter_conditions.append(WaterObject.priority <= filters.max_priority)
            
            if filters.priority_level:
                filter_conditions.append(WaterObject.priority_level == filters.priority_level)
            
            if filters.passport_date_from:
                filter_conditions.append(WaterObject.passport_date >= filters.passport_date_from)
            
            if filters.passport_date_to:
                filter_conditions.append(WaterObject.passport_date <= filters.passport_date_to)
            
            if filter_conditions:
                query = query.filter(and_(*filter_conditions))
        
        # Get total count before pagination
        total = query.count()
        
        # Apply sorting
        if pagination:
            # Get the column to sort by
            sort_column = getattr(WaterObject, pagination.sort_by, WaterObject.id)
            
            if pagination.sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
            
            # Apply pagination
            query = query.limit(pagination.limit).offset(pagination.offset)
        
        items = query.all()
        
        return items, total

    @staticmethod
    def get_regions(db: Session) -> List[str]:
        """
        Get list of unique regions.
        
        Args:
            db: Database session
            
        Returns:
            List of region names
        """
        result = db.query(WaterObject.region).filter(
            WaterObject.deleted_at.is_(None)
        ).distinct().all()
        
        return [r[0] for r in result if r[0]]

    @staticmethod
    def count_by_priority_level(db: Session) -> dict:
        """
        Count water objects by priority level.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with counts by priority level
        """
        counts = {
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        result = db.query(
            WaterObject.priority_level,
            func.count(WaterObject.id)
        ).filter(
            WaterObject.deleted_at.is_(None)
        ).group_by(WaterObject.priority_level).all()
        
        for priority_level, count in result:
            counts[priority_level.name] = count
        
        return counts
