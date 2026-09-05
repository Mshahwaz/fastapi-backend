from fastapi import HTTPException
from schema import User_create, UserUpdate
from sqlmodel import Session, select
from database import engine
from models import User
from pwdlib import PasswordHash
import logging

logging.basicConfig(
    level=logging.INFO
)
logger=logging.getLogger(__name__)
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

def get_all_users():
    with Session(engine) as session:
        users= session.exec(
            select(User)
        ).all()

        return users

def get_single_user(user_id: int):
    logging.info(f"Fetching user with id={user_id}")
    with Session(engine) as session:
        user=session.get(User, user_id)
        if not user:
            logger.warning(f"User with id={user_id} not found")
            raise HTTPException(
                status_code=404,
                detail=f"User with id {user_id} not found"
            )
        logging.info(f"User with id={user_id} found")    
        return user

def update_user_with_id(user_id: int,userobj: User_create):
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
        user.username = userobj.username
        user.password = password_hash.hash(userobj.password)

        session.add(user)
        session.commit()
        session.refresh(user)

        return user

def patch_user_with_userid(userobj: UserUpdate,user_id: int):
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

def delete_user(user_id):
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