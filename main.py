from fastapi import FastAPI, HTTPException , status, Header, Depends
from sqlmodel import Field, Session, SQLModel, create_engine, select
from pydantic import Field as pyField , BaseModel
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

app=FastAPI()
security=HTTPBearer()


DATABASE_URL=(
    "postgresql+psycopg://backend-svc-user:"
    "admin@localhost:5432/backend_db"
)

engine=create_engine(DATABASE_URL)


#Request Model from client side with schema validation
class User_create(SQLModel):
    name: str = pyField(min_length=2,max_length=50)
    age: int = pyField(ge=0,le=120)
    username: str
    password: str

#DATABASE MODEL for Database ops
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    age: int 
    username: str
    password: str

#RESPONSE MODEL for client query response
class UserResponse(SQLModel):
    id: int
    name: str
    age: int
    username: str

#To patch the feilds
class UserUpdate(SQLModel):
    name: str | None =pyField(default=None, min_length=2, max_length=50)
    age: int | None = pyField(default=None, ge=0,le=120)

# LoginRequest Model
class LoginRequest(BaseModel):
    username: str
    password: str

def create_db_and_table():
    SQLModel.metadata.create_all(engine)

create_db_and_table()

########################################

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
            age = user.age,
            username = user.username,
            password = user.password
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
#######################################

fake_users={ #Temp local DB user for testing
    "shah":{
        "username":"shah",
        "password": "secret"
    }
}

SECRET_KEY="my-super-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

#Login Authentication
@app.post(
    "/login",status_code=status.HTTP_200_OK
    )
def login(login_data: LoginRequest):

    # if ( ---Fake DB user authentication
    #     login_data.username not in fake_users
    #     or fake_users[login_data.username]["password"] != login_data.password
    # ):
    #     raise HTTPException(
    #         status_code=401, # 401 unauthorised
    #         detail="Inavlid username and password"
    #     )
    ##################### Actual DB query User authentication ######################
    with Session(engine) as session:
        statement=select(User).where(
            User.username == login_data.username
        )
        db_user= session.exec(statement).first()
        if db_user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid Username or password"
            )
        if db_user.password != login_data.password:
            raise HTTPException(
                status_code=401,
                detail="Invalid Username or password"
            )
    #################################################
    expire=datetime.now(timezone.utc)+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload={
        "sub":db_user.username,
        "exp":expire
    }
    token =jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return {
        "message" : "Login Successfull",
        # "access_token":"abc123", #fake token will used in authorization header for user authorization after login
        "access_token":token, #Generated JWT token
        "token_type":"bearer" 
    }

#Resuable Authenticatin dependency (This fn is responsible for user authentication)
def get_current_user(
credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
    #debug 
    # print("TOKEN:", credentials.credentials)
    token=credentials.credentials
    try:
        payload=jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        username=payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid Token"
            )
        # return username
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or Expired token"
        )
    with Session(engine) as session:
        statement=select(User).where(
            User.username == username
        )

        db_user=session.exec(statement).first()

        if db_user is None:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )
        return db_user

#Protected Endpoint For User authentication
@app.get("/protected")
def protected_route(
    current_user: User = Depends(get_current_user)
    ):
    #debug 
    # print("TOKEN:", credentials.credentials)
    # token=credentials.credentials
    # try:
    #     payload=jwt.decode(
    #         token,
    #         SECRET_KEY,
    #         algorithms=[ALGORITHM]
    #     )
    #     username=payload.get("sub")
    # if username is None:
    #     raise HTTPException(
    #         status_code=401,
    #         detail="Invalid Token"
    #     )
    # except JWTError:
    #     raise HTTPException(
    #         status_code=401,
    #         detail="Invalid or Expired token"
    #     )
    return {
        "message":"You are authenticated",
        "username":current_user.username,
        "user_id":current_user.id,
        "name": current_user.name
    }
