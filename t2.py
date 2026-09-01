from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app=FastAPI()

user_db=[] # act as a fake database
next_id=1 # used to gen user id

class User(BaseModel):
    name: str
    age: int

#CREATE USER
@app.post("/users") #create users
def create_user(user: User):
    # user_db.append(user)
    global next_id
    new_user={
        "id": next_id,
        "name": user.name,
        "age": user.age
    }
    user_db.append(new_user)
    next_id+=1
    return{
        "message": "User Created successfully",
        "user": new_user
    }

#GET ALL USERS
@app.get("/users")
def get_users():
    return {
        "users": user_db
    }

#GET ONE USER By ID
@app.get("/users/{user_id}")
def get_user(user_id: int):

    for user in user_db:
        if user["id"] == user_id:
            return user
    raise HTTPException(
        status_code=404,
        detail="User not found"
    )

#PUT (UPDATE DETAILS)
@app.put("/users/{user_id}")
def update_user(user_id: int,userobj: User):
    for user in user_db:
        if user["id"] == user_id:
            user["age"] = userobj.age
            user["name"] = userobj.name

            return user

    raise HTTPException(
        status_code=404,
        detail=f"User not found with id {user_id}"
    )

#DELETE USER
@app.delete("/users/{user_id}")
def delete_user(user_id):
    for user in user_db:
        if user["id"] == user_id:
            user_db.remove(user)

            return {
                "message" : f"User with id-{user_id} deleted successfully",
                "Current users" : user_db
            }
    raise HTTPException(
        status_code=404,
        detail="User not found"
    )