from fastapi import APIRouter, HTTPException, Response, Depends
from authx import AuthX, AuthXConfig

from src.core.config import settings
from pydantic import BaseModel

router = APIRouter(prefix="/autn", tags=["Autn"])

config = AuthXConfig()
config.JWT_SECRET_KEY = settings.SECRET_KEY
config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
config.JWT_TOKEN_LOCATION = ["headers", "cookies"]

security = AuthX(config=config)

class UserLoginSchema(BaseModel):
    username: str
    password: str


@router.post("/login")
async def login(creds: UserLoginSchema, response: Response):
    if creds.username == "test" and creds.password == "test":
        token = security.create_access_token(uid="12345")
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
        return {"access_token": token}
    raise HTTPException(status_code=401, detail="Incorrect username or password")


@router.post("/protected", dependencies=[Depends(security.access_token_required)])
async def protected():
    return {"message": "Hello World"}

