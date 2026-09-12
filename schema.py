from sqlmodel import SQLModel
from pydantic import Field as pyField, BaseModel

#User create schema
class User_create(SQLModel):
    name: str = pyField(min_length=2,max_length=50)
    age: int = pyField(ge=0,le=120)
    username: str
    password: str
    email: str | None = None

#RESPONSE schema for client query response
class UserResponse(SQLModel):
    id: int
    name: str
    age: int
    username: str
    email: str | None = None

#Update user schema
class UserUpdate(SQLModel):
    name: str | None =pyField(default=None, min_length=2, max_length=50)
    age: int | None = pyField(default=None, ge=0,le=120)

# LoginRequest Schema
class LoginRequest(BaseModel):
    username: str
    password: str
