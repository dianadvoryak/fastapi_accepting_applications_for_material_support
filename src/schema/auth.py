import uuid

from pydantic import BaseModel, EmailStr

class UserRegisterSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    department: str

class UserLoginSchema(BaseModel):
    username: str
    password: str

class UserResponseSchema(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    department: str
    role: str

    class Config:
        from_attributes = True