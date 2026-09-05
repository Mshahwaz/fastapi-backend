from fastapi import APIRouter, status, HTTPException
from schema import LoginRequest
from sqlmodel import Session, select
from pwdlib import PasswordHash
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from database import engine
from models import User

router=APIRouter()
password_hash=PasswordHash.recommended()

#Login (Authentication)
@router.post(
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
