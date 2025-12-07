from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session
import logging

import sys
from pathlib import Path

# Add the backend directory to path
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from database import get_db
from models import WaterObject
from rag_agent.config.orchestrator import rag_system
from rag_agent.schemas.schemas import ExplainPriorityRequest, ExplainPriorityResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rag", tags=["RAG"])


class QueryRequest(BaseModel):
    """Request model for RAG queries."""
    query: str
    context: Optional[Dict[str, Any]] = None
    environment: str = "development"


class QueryResponse(BaseModel):
    """Response model for RAG queries."""
    query: str
    response: str
    sources: list
    confidence: float
    status: str


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
        
        # Process the query
        result = rag_system.query(
            user_query=request.query,
            context=request.context or {}
        )
        
        return QueryResponse(
            query=result["query"],
            response=result["response"],
            sources=result.get("sources", []),
            confidence=result.get("confidence", 0.0),
            status="success"
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


@router.post("/explain-priority/{object_id}", response_model=ExplainPriorityResponse)
async def explain_priority(
    object_id: int,
    request: ExplainPriorityRequest,
    db: Session = Depends(get_db)
):
    """
    Explain why a water object has a specific priority score.
    """
    # Get water object
    water_object = db.query(WaterObject).filter(WaterObject.id == object_id).first()
    if not water_object:
        raise HTTPException(status_code=404, detail="Water object not found")
    
    # Initialize RAG if needed
    if not rag_system.supervisor_agent:
        rag_system.initialize()
        
    # Construct prompt
    prompt = (
        f"Explain why the water object '{water_object.name}' (ID: {water_object.id}) "
        f"has a priority score of {water_object.priority} ({water_object.priority_level.value}). "
        f"Its technical condition is {water_object.technical_condition} (1-5 scale, where 5 is worst). "
        f"Passport date: {water_object.passport_date}. "
        f"Please provide a concise explanation of the risk factors."
    )
    
    if request.language == 'ru':
        prompt += " Please answer in Russian."
    
    try:
        result = rag_system.query(user_query=prompt)
        explanation = result["response"]
    except Exception as e:
        logger.error(f"Error generating explanation: {e}")
        explanation = "Could not generate explanation at this time."
        
    return ExplainPriorityResponse(
        object_id=water_object.id,
        priority=water_object.priority,
        priority_level=water_object.priority_level.value,
        explanation=explanation
    )
