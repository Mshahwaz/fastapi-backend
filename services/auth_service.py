from fastapi import HTTPException
from sqlmodel import Session, select
from jose import jwt, JWTError
from pwdlib import PasswordHash
from database import engine
from datetime import datetime, timedelta, timezone
from config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from models import User

password_hash=PasswordHash.recommended()

def authenticate_user(username: str, password: str):
    with Session(engine) as session:
        statement=select(User).where(
            User.username == username
        )
        db_user= session.exec(statement).first()
        if db_user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid Username or password"
            )
        if not password_hash.verify(
            password,
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