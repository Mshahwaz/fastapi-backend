from sqlmodel import SQLModel, Field
# from pydantic import Field as pyField, BaseModel

# class User_create(SQLModel):
#     name: str = pyField(min_length=2,max_length=50)
#     age: int = pyField(ge=0,le=120)
#     username: str
#     password: str

#DATABASE MODEL for Database ops
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    age: int 
    username: str
    password: str
    role: str = "user"

# #RESPONSE MODEL for client query response
# class UserResponse(SQLModel):
#     id: int
#     name: str
#     age: int
#     username: str

# #Update model 
# class UserUpdate(SQLModel):
#     name: str | None =pyField(default=None, min_length=2, max_length=50)
#     age: int | None = pyField(default=None, ge=0,le=120)

# # LoginRequest Model
# class LoginRequest(BaseModel):
#     username: str
#     password: str
