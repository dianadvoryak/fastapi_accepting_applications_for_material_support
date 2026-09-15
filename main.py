from fastapi import FastAPI
from uvicorn import lifespan

app = FastAPI(
    title="Accepting applications for material support",
    description="Прием заявок для материального обеспечения на FastAPI",
    version="1.0.0",
    lifespan=lifespan,
    debug=True
)