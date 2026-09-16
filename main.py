from fastapi import FastAPI

from src.api.auth import router as auth_router
from src.api.tickets import router as ticket_router

app = FastAPI(
    title="Accepting applications for material support",
    description="Прием заявок для материального обеспечения на FastAPI",
    version="1.0.0",
    debug=True
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(ticket_router, prefix="/api/v1")
