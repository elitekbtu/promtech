from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter

from database import Base, engine
from faceid.router import router as faceid_router
from rag_agent.routes.live_query_router import router as rag_live_query_router
from rag_agent.routes.router import router as rag_router
from services.auth.router import router as auth_router
from services.objects.router import router as objects_router


app = FastAPI(title="GidroAtlas API", version="1.0.0", description="Water Resource Management System for Kazakhstan")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()
router.prefix = "/api"


@router.get("/health", tags=["system"])
async def health():
    return {"health": "ok"}


app.include_router(router)
app.include_router(auth_router, prefix="/api/auth")
app.include_router(objects_router, prefix="/api", tags=["Water Objects"])
app.include_router(faceid_router, prefix="/api/faceid", tags=["Face Verification"])
app.include_router(rag_router, tags=["RAG"])
app.include_router(rag_live_query_router, tags=["RAG Live Query"])


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
