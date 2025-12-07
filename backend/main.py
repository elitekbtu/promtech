from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter
from fastapi.staticfiles import StaticFiles
import os

from database import Base, engine
from faceid.router import router as faceid_router
from rag_agent.routes.live_query_router import router as rag_live_query_router
from rag_agent.routes.router import router as rag_router
from services.auth.router import router as auth_router
from services.objects.router import router as objects_router
from services.priorities.router import router as priorities_router
from services.passports.router import router as passports_router


app = FastAPI(title="GidroAtlas API", version="1.0.0", description="Water Resource Management System for Kazakhstan")

# CORS Configuration
# In production, replace ["*"] with specific frontend URLs
# Example: ["https://gidroatlas.kz", "https://app.gidroatlas.kz"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
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
app.include_router(objects_router, prefix="/api")
app.include_router(priorities_router, prefix="/api")
app.include_router(passports_router, prefix="/api")
app.include_router(faceid_router, prefix="/api/faceid", tags=["Face Verification"])
app.include_router(rag_router, tags=["RAG"])
app.include_router(rag_live_query_router, tags=["RAG Live Query"])

# Mount static files for passports
# Ensure the directory exists
os.makedirs("uploads/passports", exist_ok=True)
app.mount("/passports", StaticFiles(directory="uploads/passports"), name="passports")


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
