from fastapi import HTTPException
from schema import User_create
from sqlmodel import Session
from database import engine
from models import User
from pwdlib import PasswordHash

password_hash=PasswordHash.recommended()

def create_user(user: User_create):
    if user.age < 18:
        raise HTTPException(
            status_code=400,
            detail="User  must be al least 18 years"
        )   

    with Session(engine) as session:
        hashed_password = password_hash.hash(user.password)
        db_user=User(
            name = user.name,
            age = user.age,
            username = user.username,
            password = hashed_password,
            role = "role"
        ) #creating DB user obj mapped to user table
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user