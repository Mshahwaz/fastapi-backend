from fastapi import FastAPI, HTTPException , status, Header, Depends, Request, BackgroundTasks
from sqlmodel import Field, Session, SQLModel, create_engine, select
from pydantic import Field as pyField , BaseModel
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from pwdlib import PasswordHash
import time
import httpx
import logging
from config import (
    SECRET_KEY,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
)
from database import engine, create_db_and_table
from models import (
    User,
    # User_create,    ---|
    # UserResponse,      |-Imported from schema   
    # UserUpdate,        |-   
    # LoginRequest    ---|  
)
from schema import (
    User_create,
    UserResponse,
    UserUpdate,
    LoginRequest
)
from routes.users import router as users_router



# from dotenv import load_dotenv
# import os --not required as config handels 

#envvarsloader
# load_dotenv() -not required as config handels 

#Logbasicconfig
logging.basicConfig(
    level=logging.INFO
)

#Creating logger
logger=logging.getLogger(__name__)



#Required Parameters in JWT token creation --(Update) will be imported directly from config 
# SECRET_KEY=os.getenv("SECRET_KEY")
# ALGORITHM=os.getenv("ALGORITHM")
# ACCESS_TOKEN_EXPIRE_MINUTES=int(
#     os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES","30") # 30:default if not found 
# )

password_hash = PasswordHash.recommended()
# use it as : hashed_password = password_hash.hash("password")
app=FastAPI()
app.include_router(users_router)
security=HTTPBearer()

#Creating DB and Tables
create_db_and_table()

########################################

##### For BG TASK ####
def send_email():
    print("Sending Email...")
    time.sleep(5)
    print("Email Sent.!")
######################

# #CREATE USER -- Moved to routes/users 
# @app.post(
#     "/register",
#     status_code=status.HTTP_201_CREATED,
#     response_model=UserResponse
#     )
# def register_user(user: User_create,background_task: BackgroundTasks):
#     #Business Rule 
#     if user.age < 18:
#         raise HTTPException(
#             status_code=400,
#             detail="User  must be al least 18 years"
#         )
#     ###############
#     with Session(engine) as session:
#         hashed_password = password_hash.hash(user.password)
#         db_user=User(
#             name = user.name,
#             age = user.age,
#             username = user.username,
#             password = hashed_password,
#             role = "admin"
#         ) #creating DB user obj mapped to user table
#         session.add(db_user)
#         session.commit()
#         session.refresh(db_user)

#         ##Background Task
#         # background_task.add_task(send_email) #Will execute after sending request response back 

#         return db_user


# #GET ALL USERS -- Moved to routes/users 
# @app.get(
#     "/users",
#     response_model=list[UserResponse]
#     )
# def get_users():
#     with Session(engine) as session:
#         users= session.exec(
#             select(User)
#         ).all()

#         return users

# GET A Single User with user id -- Moved to routes/users 
# @app.get(
#     "/users/{user_id}",
#     response_model=UserResponse
#     )
# def get_user(user_id: int):
#     logging.info(f"Fetching user with id={user_id}")
#     with Session(engine) as session:
#         user=session.get(User, user_id)
#         if not user:
#             logger.warning(f"User with id={user_id} not found")
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"User with id {user_id} not found"
#             )
#         logging.info(f"User with id={user_id} found")    
#         return user

#UPDATE USER DATA -- Moved to routes/users 
# @app.put(
#     "/users/{user_id}",
#     response_model=UserResponse,
#     status_code=status.HTTP_200_OK
#     )
# def update_user(userobj: User_create,user_id: int):
#     with Session(engine) as session:
#         #Business Logic
#         if userobj.age < 18:
#             raise HTTPException(
#                 status_code=400,
#                 detail="User must be al least 18 years"
#             )
#         ###############           
#         user=session.get(User, user_id)
#         if not user:
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"User not found with id {user_id}"
#             )

#         user.name=userobj.name
#         user.age=userobj.age
#         user.username = userobj.username
#         user.password = password_hash.hash(userobj.password)

#         session.add(user)
#         session.commit()
#         session.refresh(user)

#         return user

#PATCH USER FEILDS -- Moved to routes/users 
# @app.patch(
#     "/users/{user_id}",
#     response_model=UserResponse,
#     status_code=status.HTTP_200_OK
#     )
# def patch_user(userobj: UserUpdate,user_id: int):
#     with Session(engine) as session:
#         user=session.get(User,user_id)
#         if not user:
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"User not found with id {user_id}"
#             )
#         if userobj.name is not None:
#             user.name=userobj.name
#         if userobj.age is not None:
#         #Business Logic
#             if userobj.age < 18:
#                 raise HTTPException(
#                 status_code=400,
#                 detail="User must be al least 18 years"
#             )
#         ###############
#             user.age=userobj.age
#         session.add(user)
#         session.commit()
#         session.refresh(user)
#         return user

#Resuable Authentication dependency (This fn is responsible for user authentication)
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
    
    # print(request)
    
    response = await call_next(request)
    
    end_time=time.time()
    
    duration=end_time-start_time

    # print(
    #     f"INFO: {request.method} {request.url.path}"
    #     f" completed in {duration:4f} seconds"
    # )
    logging.info(
        f" {request.method} {request.url.path}"
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

#Get request to external api
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
#Testing 
class External_api_users(BaseModel):
    id: int
    body: str
    title: str

#POST Request to External api
@app.post("/external-post")
async def send_to_external_api(user_data: External_api_users):
    payload ={
        "id":101,
        "userId":user_data.id,
        "title":user_data.title,
        "body":user_data.body
    }
    url="https://jsonplaceholder.typicode.com/posts"
    header={
        "content-Type": "application/json"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            headers=header,
            json=payload
        )
    # print(response.json()) Debig
    response_payload=response.json()
    response_payload.setdefault("status","Query Successfull")
    return response_payload