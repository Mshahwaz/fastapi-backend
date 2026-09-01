from fastapi import FastAPI, HTTPException , status, Header, Depends
from sqlmodel import Field, Session, SQLModel, create_engine, select
# from pydantic import Field -> This is create issue with SQL model field so will use alias
from pydantic import Field as pyField , BaseModel
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


app=FastAPI()
security=HTTPBearer()
############################## DATABASE SETUP BEGIN ##########################

#DATABASE URL -->Docker implementation
DATABASE_URL=(
    "postgresql+psycopg://backend-svc-user:"
    "admin@localhost:5432/backend_svc-db"
)

#create sqlalchemy engine engine that knows how our application connects to PostgreSQL.
engine=create_engine(DATABASE_URL)

#Request Model from client side with schema validation
class User_create(SQLModel):
    name: str = pyField(min_length=2,max_length=50)
    age: int = pyField(ge=0,le=120)

#DATABASE MODEL for Database ops
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    age: int 

#RESPONSE MODEL for client query response
class UserResponse(SQLModel):
    id: int
    name: str
    age: int

#To patch the feilds
class UserUpdate(SQLModel):
    name: str | None =pyField(default=None, min_length=2, max_length=50)
    age: int | None = pyField(default=None, ge=0,le=120)

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
@app.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse
    )
def create_user(user: User_create):
    with Session(engine) as session:
        #Business Rule 
        if user.age < 18:
            raise HTTPException(
                status_code=400,
                detail="User  must be al least 18 years"
            )
        ###############
        db_user=User(
            name = user.name,
            age = user.age
        ) #creating DB user obj mapped to user table
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user


#GET ALL USERS
@app.get(
    "/users",
    response_model=list[UserResponse]
    )
def get_users():
    with Session(engine) as session:
        users= session.exec(
            select(User)
        ).all()

        return users

####################### Query Parameter implementation ##################################
@app.get(
    "/users/search",
    response_model=list[UserResponse]
    )
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
@app.get(
    "/users/{user_id}",
    response_model=UserResponse
    )
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
@app.put(
    "/users/{user_id}",
    response_model=UserResponse
    )
def update_user(userobj: User_create,user_id: int):
    with Session(engine) as session:
        #Business Logic
        if userobj.age > 18:
            raise HTTPException(
                status_code=400,
                detail="User must be al least 18 years"
            )
        ###############           
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

        return user

#PATCH USER FEILDS
@app.patch(
    "/users/{user_id}",
    response_model=UserResponse
    )
def patch_user(userobj: UserUpdate,user_id: int):
    with Session(engine) as session:
        user=session.get(User,user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User not found with id {user_id}"
            )
        if userobj.name is not None:
            user.name=userobj.name
        if userobj.age is not None:
        #Business Logic
            if userobj.age < 18:
                raise HTTPException(
                status_code=400,
                detail="User must be al least 18 years"
            )
        ###############
            user.age=userobj.age
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


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

# user-agent headers
# @app.get("/headers")
# def read_headers(
#     user_agent: str | None = Header(default=None)
#     ):
#     return {
#         "user_agent":user_agent
#     }

# #Custom Header
# @app.get("/client-info")
# def client_version(
#     client_version: str | None = Header(default=True)
#     ):
#     return {
#         "client_version":client_version
#     }
###########################################################################################

# TOY Login for practice

class LoginRequest(BaseModel):
    username: str
    password: str

fake_users={
    "shah":{
        "username":"shah",
        "password": "secret"
    }
}

#Login Authentication
@app.post(
    "/login",
    )
def login(login_data: LoginRequest):
    user=fake_users.get(login_data.username)
    if not user:
        raise HTTPException(
            status_code=401, # 401 unauthorised
            detail="Inavlid username and password"
        )
    if user["password"] != login_data.password:
        raise HTTPException(
            status_code=401,
            detail="Inavlid username and password"
        )
    return {
        "message" : "Login Successfull",
        "access_token":"abc123", #fake token will used in authorization header for user authorization after login
        "token_type":"bearer" 
    }       

#Protected Endpoint using authorization

@app.get("/protected")
def protected_route(
    # authorization: str | None = Header(default=None)
    credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
    #debug 
    # print("TOKEN:", credentials.credentials)

    if credentials.credentials != "abc123":
        raise HTTPException(
            status_code=401,
            detail="Not Authenticated invalid token"
        )
    return {
        "message":"You are authenticated"
    }