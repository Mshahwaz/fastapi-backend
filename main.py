from fastapi import FastAPI, HTTPException , status, Header, Depends, Request
from sqlmodel import Field, Session, SQLModel, create_engine, select
from pydantic import Field as pyField , BaseModel
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from pwdlib import PasswordHash
import time
import httpx

#Required Parameters in JWT token creation
SECRET_KEY="my-super-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

password_hash = PasswordHash.recommended()
# use it as : hashed_password = password_hash.hash("password")
app=FastAPI()
security=HTTPBearer()


DATABASE_URL=(
    "postgresql+psycopg://backend-svc-user:"
    "backend-svc-pass@localhost:5432/backend_db"
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
    role: str = "user"

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
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse
    )
def register_user(user: User_create):
    #Business Rule 
    if user.age < 18:
        raise HTTPException(
            status_code=400,
            detail="User  must be al least 18 years"
        )
    ###############
    with Session(engine) as session:
        hashed_password = password_hash.hash(user.password)
        db_user=User(
            name = user.name,
            age = user.age,
            username = user.username,
            password = hashed_password,
            role = "user"
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
        if userobj.age < 18:
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

#Resuable Authenticatin dependency (This fn is responsible for user authentication)
def get_current_user(
credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
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

#Resuable admin verification dependency (This fn is responsible for admin authorization)
def require_admin(
    current_user: User = Depends(get_current_user)
    ):
        ########### Check if a user is a admin or normal user ################ 
    # time.sleep(10) - for middleware testing
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin Access required"
        )
    return current_user
    ####################################################################       

#DELETE USER with user id (Protected Endpoint only admin role can delete a user)
@app.delete("/users/{user_id}")
def del_user(user_id: int,current_user: User = Depends(require_admin)):
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

#Login (Authentication)
@app.post(
    "/login",status_code=status.HTTP_200_OK
    )
def login(login_data: LoginRequest):
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
        if not password_hash.verify(
            login_data.password,
            db_user.password
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid Username or password"
            )

    expire=datetime.now(timezone.utc)+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload={
        "sub":db_user.username,
        "role": db_user.role,
        "exp":expire
    }
    token =jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return {
        "message" : "Login Successfull",
        "access_token":token, #Generated JWT token
        "token_type":"bearer" 
    }


#Protected Endpoint (Accessible only for authenticated Users (anyone))
@app.get("/protected")
def protected_route(
    current_user: User = Depends(get_current_user)
    ):
    return {
        "message":"You are authenticated",
        "username":current_user.username,
        "user_id":current_user.id,
        "name": current_user.name,
        "role":current_user.role
    }

#Protected admin dashboard (accessible to admins only)
@app.get("/admin/dashboard")
def admin_dashboard(
    current_user: User = Depends(require_admin)
    ):
    return {
        "message" : " Welcome to Admin Dashboard ",
        "user": current_user.name
    }
#Global Exception handler for unexpected errors
@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exe: Exception
    ):
    return JSONResponse(
        status_code=500,
        content={
            "detail":"Internal server error occurred"
        }
    )

#Middleware to measure API query total time
@app.middleware("http")
async def request_timer(request: Request,call_next):
    
    start_time=time.time()
    
    print(request)
    
    response = await call_next(request)
    
    end_time=time.time()
    
    duration=end_time-start_time

    print(
        f"{request.method} {request.url.path}"
        f" completed in {duration:4f} seconds"
    )
    return response

#Calling external Api endpoint ( https://jsonplaceholder.typicode.com/users/{user_id} )
# #Sync/blocking version
# @app.get("/external-user/{user_id}")
# def get_external_user(user_id: int):
#     response = httpx.get(
#         f"https://jsonplaceholder.typicode.com/users/{user_id}"
#     )

#     return response.json

#async (coroutine endpoint)
@app.get("/external-user/{user_id}")
async def get_external_user(user_id: int):
    
    try:
        async with httpx.AsyncClient() as client:

            response = await client.get(
                f"https://jsonplaceholder.tpicode.com/uses",
                timeout=5.0
            )
            response.raise_for_status()

        return response.json()
    except httpx.HTTPStatusError: # For any Other exception like DNS failure, Connection issue, network failure
        raise HTTPException(
            status_code=502, # 502 - bad gatway - 
            detail="External API returned an error"
        )
    except httpx.ConnectError: # For any Other exception like DNS failure, Connection issue, network failure
        raise HTTPException(
            status_code=502, # 502 - bad gatway - 
            detail="External API returned an error"
        )
    except httpx.TimeoutException: # For any Other exception like DNS failure, Connection issue, network failure
        raise HTTPException(
            status_code=504, # 504 Gateway timeout  - 
            detail="External API returned an error"
        )