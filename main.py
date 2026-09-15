from fastapi import FastAPI
from uvicorn import lifespan
from src.api.auth import router as auth_router

app = FastAPI(
    title="Accepting applications for material support",
    description="Прием заявок для материального обеспечения на FastAPI",
    version="1.0.0",
    debug=True
)

app.include_router(auth_router, prefix="/api/v1")
