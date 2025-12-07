from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any
from pydantic import BaseModel
import logging

import sys
from pathlib import Path

# Add the backend directory to path
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from rag_agent.config.orchestrator import rag_system

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rag", tags=["RAG"])


class QueryRequest(BaseModel):
    """Request model for RAG queries."""
    query: str
    context: Optional[Dict[str, Any]] = None
    environment: str = "development"
    # Optional water management filters
    object_id: Optional[int] = None
    region: Optional[str] = None
    priority_level: Optional[str] = None
    resource_type: Optional[str] = None


class QueryResponse(BaseModel):
    """Response model for RAG queries."""
    query: str
    response: str
    sources: list
    confidence: float
    status: str
    # Water management metadata
    water_objects: Optional[list] = None
    regions: Optional[list] = None
    priority_levels: Optional[list] = None


@router.post("/query", response_model=QueryResponse)
async def query_rag_system(request: QueryRequest):
    """
    Process a query through the RAG system.
    
    Args:
        request: Query request with query text and optional context
        
    Returns:
        QueryResponse: RAG system response with sources and confidence
    """
    try:
        # Initialize the RAG system if not already done
        if not rag_system.supervisor_agent:
            rag_system.initialize(environment=request.environment)
        
        # Build context with water management filters
        context = request.context or {}
        if request.object_id:
            context['object_id'] = request.object_id
        if request.region:
            context['region'] = request.region
        if request.priority_level:
            context['priority_level'] = request.priority_level
        if request.resource_type:
            context['resource_type'] = request.resource_type
        
        # Process the query
        result = rag_system.query(
            user_query=request.query,
            context=context
        )
        
        # Extract water-specific metadata from sources
        water_objects = []
        regions = set()
        priority_levels = set()
        
        for source in result.get("sources", []):
            if isinstance(source, dict):
                # Extract water object metadata
                if source.get('object_name'):
                    water_objects.append({
                        'id': source.get('object_id'),
                        'name': source.get('object_name'),
                        'region': source.get('region'),
                        'resource_type': source.get('resource_type'),
                        'priority_level': source.get('priority_level')
                    })
                
                if source.get('region'):
                    regions.add(source.get('region'))
                if source.get('priority_level'):
                    priority_levels.add(source.get('priority_level'))
        
        return QueryResponse(
            query=result["query"],
            response=result["response"],
            sources=result.get("sources", []),
            confidence=result.get("confidence", 0.0),
            status="success",
            water_objects=water_objects if water_objects else None,
            regions=list(regions) if regions else None,
            priority_levels=list(priority_levels) if priority_levels else None
        )
        
    except Exception as e:
        logger.error(f"Error processing RAG query: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.get("/status")
async def get_system_status():
    """
    Get the current status of the RAG system.
    
    Returns:
        Dict: System status information
    """
    try:
        return {
            "status": "operational",
            "supervisor_agent": rag_system.supervisor_agent is not None,
            "specialist_agents": list(rag_system.specialist_agents.keys()),
            "available_tools": rag_system.config.get_available_tools(),
            "available_agents": rag_system.config.get_available_agents()
        }
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")


@router.post("/explain-priority/{object_id}")
async def explain_priority(object_id: int):
    """
    Explain the priority calculation for a specific water object.
    
    This is a convenience endpoint that queries the RAG system about
    why a specific object has its current priority level.
    
    Args:
        object_id: ID of the water object
        
    Returns:
        QueryResponse: Explanation of the priority with sources
    """
    try:
        # Initialize the RAG system if not already done
        if not rag_system.supervisor_agent:
            rag_system.initialize(environment="development")
        
        # Build query in Russian (primary language for water management)
        query = f"Объясни приоритет обследования для водного объекта с ID {object_id}. Почему такой приоритет? Как он рассчитывается?"
        
        # Process the query with object_id context
        result = rag_system.query(
            user_query=query,
            context={'object_id': object_id}
        )
        
        # Extract water-specific metadata
        water_objects = []
        regions = set()
        priority_levels = set()
        
        for source in result.get("sources", []):
            if isinstance(source, dict):
                if source.get('object_name'):
                    water_objects.append({
                        'id': source.get('object_id'),
                        'name': source.get('object_name'),
                        'region': source.get('region'),
                        'resource_type': source.get('resource_type'),
                        'priority_level': source.get('priority_level')
                    })
                
                if source.get('region'):
                    regions.add(source.get('region'))
                if source.get('priority_level'):
                    priority_levels.add(source.get('priority_level'))
        
        return QueryResponse(
            query=query,
            response=result["response"],
            sources=result.get("sources", []),
            confidence=result.get("confidence", 0.0),
            status="success",
            water_objects=water_objects if water_objects else None,
            regions=list(regions) if regions else None,
            priority_levels=list(priority_levels) if priority_levels else None
        )
        
    except Exception as e:
        logger.error(f"Error explaining priority for object {object_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error explaining priority: {str(e)}")


@router.post("/initialize")
async def initialize_system(environment: str = "development"):
    """
    Initialize the RAG system.
    
    Args:
        environment: Environment to initialize for (development, production, testing)
        
    Returns:
        Dict: Initialization status
    """
    try:
        rag_system.initialize(environment=environment)
        return {
            "status": "initialized",
            "environment": environment,
            "message": "RAG system initialized successfully"
        }
    except Exception as e:
        logger.error(f"Error initializing RAG system: {e}")
        raise HTTPException(status_code=500, detail=f"Error initializing system: {str(e)}")


@router.get("/tools/status")
async def get_tools_status():
    """
    Get the status of all tools in the system.
    
    Returns:
        Dict: Status of all tools
    """
    try:
        from rag_agent.tools.vector_search import get_vector_store_status
        from rag_agent.tools.web_search import get_web_search_status
        
        return {
            "vector_search": get_vector_store_status(),
            "web_search": get_web_search_status()
        }
    except Exception as e:
        logger.error(f"Error getting tools status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting tools status: {str(e)}")
