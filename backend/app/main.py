from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.opportunities import router as opportunities_router

app = FastAPI(
    title="SkillBridge AI API",
    description="Backend API for SkillBridge AI — From Opportunity to Action.",
    version="0.1.0",
)

# Configure CORS for local development with Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/health",
    summary="Health Check",
    tags=["System"],
)
def health_check():
    return {
        "status": "healthy",
        "service": "SkillBridge AI API",
    }


# Include opportunities router with /api prefix
app.include_router(opportunities_router, prefix="/api", tags=["Opportunities"])
