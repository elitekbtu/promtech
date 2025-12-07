from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from database import get_db
from models import UserRole
from services.auth.service import get_current_user, get_user_role_or_guest
from services.objects.service import WaterObjectService
from services.objects.schemas import (
    WaterObjectCreate,
    WaterObjectUpdate,
    WaterObjectResponse,
    WaterObjectGuestResponse,
    WaterObjectListResponse,
    WaterObjectFilter,
    PaginationParams,
)


router = APIRouter(prefix="/objects", tags=["Water Objects"])


def require_expert(current_user = Depends(get_current_user)):
    """Dependency to require expert role"""
    if current_user.role != UserRole.expert:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint requires expert role. Guests cannot access priority information.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return current_user


@router.get(
    "/",
    summary="List water objects",
    description="Get a paginated list of water objects with optional filtering and sorting. Unauthenticated users and guests will not see priority information."
)
async def list_water_objects(
    # Filtering parameters
    search: Optional[str] = Query(None, description="Search by name or region (case-insensitive)"),
    region: Optional[str] = Query(None, description="Filter by region"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    water_type: Optional[str] = Query(None, description="Filter by water type"),
    fauna: Optional[str] = Query(None, description="Filter by fauna type"),
    min_technical_condition: Optional[int] = Query(None, ge=1, le=5, description="Minimum technical condition"),
    max_technical_condition: Optional[int] = Query(None, ge=1, le=5, description="Maximum technical condition"),
    min_priority: Optional[int] = Query(None, ge=0, description="Minimum priority score (expert only)"),
    max_priority: Optional[int] = Query(None, ge=0, description="Maximum priority score (expert only)"),
    priority_level: Optional[str] = Query(None, description="Filter by priority level (expert only)"),
    passport_date_from: Optional[str] = Query(None, description="Passport date from (ISO format)"),
    passport_date_to: Optional[str] = Query(None, description="Passport date to (ISO format)"),
    
    # Pagination parameters
    limit: int = Query(100, gt=0, le=100, description="Maximum number of items"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    sort_by: str = Query("id", description="Field to sort by"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    
    # Dependencies
    db: Session = Depends(get_db),
    user_role: UserRole = Depends(get_user_role_or_guest)
):
    """
    List water objects with filtering, sorting, and pagination.
    
    **Unauthenticated users and guests** see only basic information (no priority data).
    **Expert users** see full information including priorities and can filter by priority.
    
    No authentication required - defaults to guest view.
    """
    
    # Build filter object
    filters = WaterObjectFilter(
        search=search,
        region=region,
        resource_type=resource_type,
        water_type=water_type,
        fauna=fauna,
        min_technical_condition=min_technical_condition,
        max_technical_condition=max_technical_condition,
        min_priority=min_priority if user_role == UserRole.expert else None,
        max_priority=max_priority if user_role == UserRole.expert else None,
        priority_level=priority_level if user_role == UserRole.expert else None,
        passport_date_from=passport_date_from,
        passport_date_to=passport_date_to
    )
    
    # Build pagination object
    pagination = PaginationParams(
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Get filtered and paginated results
    items, total = WaterObjectService.list_with_filters(db, filters, pagination)
    
    # Convert to appropriate response type based on user role
    if user_role == UserRole.guest:
        # Convert to guest response (no priority data)
        response_items = [WaterObjectGuestResponse.model_validate(item) for item in items]
    else:
        # Return full response with priority data
        response_items = [WaterObjectResponse.model_validate(item) for item in items]
    
    # Build response
    has_more = (offset + len(items)) < total
    
    return {
        "items": response_items,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": has_more
    }


@router.get(
    "/{object_id}",
    responses={
        404: {"description": "Water object not found"},
        403: {"description": "Insufficient permissions (guest cannot see priorities)"}
    },
    summary="Get water object by ID",
    description="Retrieve detailed information about a specific water object. Unauthenticated users and guests will not see priority information."
)
async def get_water_object(
    object_id: int,
    db: Session = Depends(get_db),
    user_role: UserRole = Depends(get_user_role_or_guest)
):
    """
    Get detailed information about a water object.
    
    **Unauthenticated users and guests** see only basic information (no priority data).
    **Expert users** see full information including priority calculations.
    
    No authentication required - defaults to guest view.
    """
    
    water_object = WaterObjectService.get_by_id(db, object_id)
    
    if not water_object:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Water object with ID {object_id} not found"
        )
    
    # Return appropriate response based on role
    if user_role == UserRole.guest:
        # Return without priority information
        from services.objects.schemas import WaterObjectGuestResponse
        return WaterObjectGuestResponse.model_validate(water_object)
    else:
        # Return full information including priorities
        return WaterObjectResponse.model_validate(water_object)


@router.post(
    "/",
    response_model=WaterObjectResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_expert)],
    summary="Create new water object",
    description="Create a new water object. Priority is automatically calculated. **Requires expert role.**"
)
async def create_water_object(
    water_object_data: WaterObjectCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new water object.
    
    **Expert only** - Automatically calculates priority based on technical condition and passport age.
    """
    
    created_object = WaterObjectService.create(db, water_object_data)
    
    return WaterObjectResponse.model_validate(created_object)


@router.put(
    "/{object_id}",
    response_model=WaterObjectResponse,
    dependencies=[Depends(require_expert)],
    responses={
        404: {"description": "Water object not found"}
    },
    summary="Update water object",
    description="Update an existing water object. Priority is recalculated if condition or passport date changes. **Requires expert role.**"
)
async def update_water_object(
    object_id: int,
    water_object_data: WaterObjectUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a water object.
    
    **Expert only** - Automatically recalculates priority if technical condition or passport date changes.
    """
    
    updated_object = WaterObjectService.update(db, object_id, water_object_data)
    
    if not updated_object:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Water object with ID {object_id} not found"
        )
    
    return WaterObjectResponse.model_validate(updated_object)


@router.delete(
    "/{object_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_expert)],
    responses={
        404: {"description": "Water object not found"}
    },
    summary="Delete water object",
    description="Soft delete a water object. **Requires expert role.**"
)
async def delete_water_object(
    object_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a water object (soft delete).
    
    **Expert only** - The object is marked as deleted but not removed from the database.
    """
    
    deleted = WaterObjectService.delete(db, object_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Water object with ID {object_id} not found"
        )
    
    return None


@router.get(
    "/{object_id}/passport",
    response_model=dict,
    responses={
        404: {"description": "Water object not found or no passport available"}
    },
    summary="Get water object passport metadata",
    description="Retrieve passport document metadata for a water object. Available to all users."
)
async def get_water_object_passport(
    object_id: int,
    db: Session = Depends(get_db)
):
    """
    Get passport document metadata for a water object.
    
    Returns passport file URL and basic metadata.
    No authentication required.
    """
    
    water_object = WaterObjectService.get_by_id(db, object_id)
    
    if not water_object:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Water object with ID {object_id} not found"
        )
    
    if not water_object.pdf_url and not water_object.passport_date:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No passport document available for water object {object_id}"
        )
    
    return {
        "object_id": water_object.id,
        "object_name": water_object.name,
        "passport_date": water_object.passport_date,
        "pdf_url": water_object.pdf_url,
        "message": "Passport metadata retrieved successfully"
    }


@router.get(
    "/regions/list",
    response_model=List[str],
    summary="Get list of regions",
    description="Get a list of unique regions from all water objects."
)
async def list_regions(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get list of unique regions.
    
    Useful for filtering water objects by region.
    """
    
    regions = WaterObjectService.get_regions(db)
    
    return regions
