from fastapi import FastAPI, HTTPException , status, Header, Depends, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta, timezone
import time
import httpx
import logging
# from database import create_db_and_table (alembic)
from models import User
from routes.users import router as users_router
from routes.auth import router as auth_router
from dependencies.auth import (
    get_current_user,
    require_admin
)



#Logbasicconfig
logging.basicConfig(
    level=logging.INFO
)

#Creating logger
logger=logging.getLogger(__name__)


app=FastAPI()
app.include_router(users_router)
app.include_router(auth_router)


#Creating DB and Tables
# create_db_and_table() Alembic take care of this

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

#Middleware to measure total request processing time 
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
                f"https://jsonplaceholder.typicode.com/users/{user_id}",
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

@app.get("/health/live",status_code=status.HTTP_200_OK)
def health_check():
    return {
        "status": "live"
    }


@app.get("/health/ready",status_code=status.HTTP_200_OK)
def health_check():
    return {
        "status": "ready"
    }