from fastapi import FastAPI, HTTPException , status
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi.responses import FileResponse

app=FastAPI()

############################## DATABASE SETUP BEGIN ##########################

#DATABASE URL -->Docker implementation
DATABASE_URL=(
    "postgresql+psycopg://backend-svc-user:"
    "admin@localhost:5432/backend_svc-db"
)

#create sqlalchemy engine engine that knows how our application connects to PostgreSQL.
engine=create_engine(DATABASE_URL)

#Request Model from client side
class User_create(SQLModel):
    name: str
    age: int

#describing db table(model) using python
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    age: int

#CREATE DB TABLE
def create_db_and_table():
    SQLModel.metadata.create_all(engine)

create_db_and_table()

##################### DATABASE SETUP END ####################################

#TO serve HTML
@app.get("/")
def home():
    return FileResponse("fronend/index.html")

######################### CRUD OPERATIONS #######################################
#CREATE USER 
@app.post("/users",status_code=status.HTTP_201_CREATED)
def create_user(user: User_create):
    with Session(engine) as session:
        new_user=User(
            name = user.name,
            age = user.age
        ) #creating DB user obj mapped to user table
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user


#GET ALL USERS
@app.get("/users")
def get_users():
    with Session(engine) as session:
        users= session.exec(
            select(User)
        ).all()

        return users

####################### Query Parameter implementation ##################################
@app.get("/users/search")
def search_users(name: str | None = None):
    with Session(engine) as session:

        users=session.exec(
            select(User)
            ).all()
    if name:
        users=[
            user for user in users if user.name.lower() == name.lower() # list comnprehension
        ]
        return users
    raise HTTPException(
        status_code=404,
        detail="No search Found"
    )

# GET A Single User with user id
@app.get("/users/{user_id}")
def get_user(user_id: int):
    with Session(engine) as session:
        user=session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User with id {user_id} not found"
            )
        return user

#UPDATE USER DATA
@app.put("/users/{user_id}")
def update_user(userobj: User_create,user_id: int):
    with Session(engine) as session:
        user=session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User not found with id {user_id}"
            )

        user.name=userobj.name
        user.age=userobj.age

        session.add(user)
        session.commit()
        session.refresh(user)

        return get_user(user_id)

#DELETE USER with user id
@app.delete("/users/{user_id}")
def del_user(user_id: int):
    with Session(engine) as session:
        user=session.get(User, user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User not found with id {user_id}"
            )
        session.delete(user)
        session.commit()
        return {
            "message" : f"User with id {user_id} has been removed successfully"
        }
########################################################################################

