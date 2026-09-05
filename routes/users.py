from fastapi import APIRouter, status, BackgroundTasks, HTTPException, Depends
from pwdlib import PasswordHash
from schema import (
    User_create,
    UserResponse,
    UserUpdate,
    LoginRequest
)
from sqlmodel import Session, select
from models import User  
from database import engine
import logging

logging.basicConfig(
    level=logging.INFO
)
logger=logging.getLogger(__name__)
router=APIRouter()
password_hash=PasswordHash.recommended()

#CREATE USER 
@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse
    )
def register_user(user: User_create,background_task: BackgroundTasks):
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
            role = "role"
        ) #creating DB user obj mapped to user table
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        ##Background Task
        # background_task.add_task(send_email) #Will execute after sending request response back 

        return db_user


#GET ALL USERS
@router.get(
    "/users",
    response_model=list[UserResponse]
    )
def get_users():
    with Session(engine) as session:
        users= session.exec(
            select(User)
        ).all()

        return users

# # GET A Single User with user id
@router.get(
    "/users/{user_id}",
    response_model=UserResponse
    )
def get_user(user_id: int):
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

#UPDATE USER DATA
@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK
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
        user.username = userobj.username
        user.password = password_hash.hash(userobj.password)

        session.add(user)
        session.commit()
        session.refresh(user)

        return user

#PATCH USER FEILDS
@router.patch(
    "/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK
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

@router.delete("/users/{user_id}")
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