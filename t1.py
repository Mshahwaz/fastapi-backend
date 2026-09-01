from fastapi import FastAPI
from pydantic import BaseModel

app=FastAPI()

class User(BaseModel):
    name: str
    age: int

@app.get("/hello")
def hello(name: str="Guest"):
    return { "message" : f"Hello {name} from my backend" }

@app.post("/users")
def create_user(user: User):
    return {
        "message": f"Hello {user.name}, Welcome to backend your age is {user.age}"
    }