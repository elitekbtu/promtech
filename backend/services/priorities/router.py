from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from database import get_db
from models import WaterObject, PriorityLevel
from services.auth.service import get_current_user
from services.objects.service import WaterObjectService
from .schemas import (
    PriorityStatistics,
    PriorityTableItem,
    PriorityTableResponse,
    PriorityFilter,
)


router = APIRouter(prefix="/priorities", tags=["Priorities"])


def require_expert(current_user = Depends(get_current_user)):
    """Dependency to require expert role for all priority endpoints"""
    from models import UserRole
    if current_user.role != UserRole.expert:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Priority information is only accessible to expert users. Guests do not have permission to view inspection priorities.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return current_user


@router.get(
    "/statistics",
    response_model=PriorityStatistics,
    dependencies=[Depends(require_expert)],
    summary="Get priority statistics",
    description="Get aggregated statistics about water objects by priority level. **Requires expert role.**"
)
async def get_priority_statistics(
    db: Session = Depends(get_db)
):
    """
    Get priority level statistics.
    
    **Expert only** - Returns count of water objects grouped by priority level (HIGH/MEDIUM/LOW).
    """
    
    counts = WaterObjectService.count_by_priority_level(db)
    
    return PriorityStatistics(
        high=counts.get("high", 0),
        medium=counts.get("medium", 0),
        low=counts.get("low", 0),
        total=counts.get("high", 0) + counts.get("medium", 0) + counts.get("low", 0)
    )


@router.get(
    "/table",
    response_model=PriorityTableResponse,
    dependencies=[Depends(require_expert)],
    summary="Get priority dashboard table",
    description="Get paginated list of water objects with priority information for dashboard display. Supports filtering and sorting. **Requires expert role.**"
)
async def get_priority_table(
    # Filter parameters
    priority_level: Optional[str] = Query(None, description="Filter by priority level (high/medium/low)"),
    min_priority: Optional[int] = Query(None, ge=0, description="Minimum priority score"),
    max_priority: Optional[int] = Query(None, ge=0, description="Maximum priority score"),
    region: Optional[str] = Query(None, description="Filter by region"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    
    # Pagination parameters
    limit: int = Query(50, gt=0, le=100, description="Maximum number of items (default 50)"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    sort_by: str = Query("priority", description="Field to sort by (default: priority)"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order (default: desc for highest priority first)"),
    
    # Dependencies
    db: Session = Depends(get_db)
):
    """
    Get priority dashboard table with filtering and sorting.
    
    **Expert only** - Returns water objects sorted by priority (highest first by default).
    
    Supports filtering by:
    - Priority level (high/medium/low)
    - Priority score range
    - Region
    - Resource type
    
    Default sorting: Priority descending (most urgent first)
    """
    
    # Build query
    query = db.query(WaterObject).filter(WaterObject.deleted_at.is_(None))
    
    # Apply filters
    if priority_level:
        try:
            level = PriorityLevel[priority_level.lower()]
            query = query.filter(WaterObject.priority_level == level)
        except KeyError:
            pass  # Invalid priority level, ignore filter
    
    if min_priority is not None:
        query = query.filter(WaterObject.priority >= min_priority)
    
    if max_priority is not None:
        query = query.filter(WaterObject.priority <= max_priority)
    
    if region:
        query = query.filter(WaterObject.region.ilike(f"%{region}%"))
    
    if resource_type:
        query = query.filter(WaterObject.resource_type == resource_type)
    
    # Get total count before pagination
    total = query.count()
    
    # Apply sorting
    sort_column = getattr(WaterObject, sort_by, WaterObject.priority)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)
    
    # Apply pagination
    items = query.offset(offset).limit(limit).all()
    
    # Convert to response items
    response_items = []
    for item in items:
        response_items.append(PriorityTableItem(
            id=item.id,
            name=item.name,
            region=item.region,
            resource_type=item.resource_type.value,
            technical_condition=item.technical_condition,
            passport_date=item.passport_date.isoformat() if item.passport_date else None,
            priority=item.priority,
            priority_level=item.priority_level
        ))
    
    has_more = (offset + len(items)) < total
    
    return PriorityTableResponse(
        items=response_items,
        total=total,
        limit=limit,
        offset=offset,
        has_more=has_more
    )


@router.get(
    "/top",
    response_model=list[PriorityTableItem],
    dependencies=[Depends(require_expert)],
    summary="Get top priority water objects",
    description="Get the top N water objects with highest inspection priority. **Requires expert role.**"
)
async def get_top_priorities(
    count: int = Query(10, gt=0, le=50, description="Number of top priority objects to return (max 50)"),
    db: Session = Depends(get_db)
):
    """
    Get top priority water objects.
    
    **Expert only** - Returns the water objects with highest inspection priority (most urgent first).
    Useful for quick dashboard view of critical objects requiring immediate attention.
    """
    
    items = db.query(WaterObject).filter(
        WaterObject.deleted_at.is_(None)
    ).order_by(
        desc(WaterObject.priority)
    ).limit(count).all()
    
    response_items = []
    for item in items:
        response_items.append(PriorityTableItem(
            id=item.id,
            name=item.name,
            region=item.region,
            resource_type=item.resource_type.value,
            technical_condition=item.technical_condition,
            passport_date=item.passport_date.isoformat() if item.passport_date else None,
            priority=item.priority,
            priority_level=item.priority_level
        ))
    
    return response_items
