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
from dependencies.auth import require_admin
from services.user_service import (
    create_user,
    get_all_users,
    get_single_user,
    update_user_with_id,
    patch_user_with_userid,
    delete_user
)

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
    response=create_user(user)
    return response
    #-- whole logic will be performed by user-service--#(tested)


#GET ALL USERS
@router.get(
    "/users",
    response_model=list[UserResponse]
    )
def get_users():
    response=get_all_users()
    return response
    #-- whole logic will be performed by user-service--#(tested)
    # with Session(engine) as session:
    #     users= session.exec(
    #         select(User)
    #     ).all()

    #     return users

# # GET A Single User with user id
@router.get(
    "/users/{user_id}",
    response_model=UserResponse
    )
def get_user(user_id: int):
    response=get_single_user(user_id)
    return response
    #-- whole logic will be performed by user-service--#(tested)
    # logging.info(f"Fetching user with id={user_id}")
    # with Session(engine) as session:
    #     user=session.get(User, user_id)
    #     if not user:
    #         logger.warning(f"User with id={user_id} not found")
    #         raise HTTPException(
    #             status_code=404,
    #             detail=f"User with id {user_id} not found"
    #         )
    #     logging.info(f"User with id={user_id} found")    
    #     return user

#UPDATE USER DATA
@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK
    )
def update_user(userobj: User_create,user_id: int):
    response=update_user_with_id(user_id,userobj)
    return response
    #-- whole logic will be performed by user-service--#(tested)
    # with Session(engine) as session:
    #     #Business Logic
    #     if userobj.age < 18:
    #         raise HTTPException(
    #             status_code=400,
    #             detail="User must be al least 18 years"
    #         )
    #     ###############           
    #     user=session.get(User, user_id)
    #     if not user:
    #         raise HTTPException(
    #             status_code=404,
    #             detail=f"User not found with id {user_id}"
    #         )

    #     user.name=userobj.name
    #     user.age=userobj.age
    #     user.username = userobj.username
    #     user.password = password_hash.hash(userobj.password)

    #     session.add(user)
    #     session.commit()
    #     session.refresh(user)

    #     return user

#PATCH USER FEILDS
@router.patch(
    "/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK
    )
def patch_user(userobj: UserUpdate,user_id: int):
    response=patch_user_with_userid(userobj,user_id)
    return response
    #-- whole logic will be performed by user-service--#(tested)
    # with Session(engine) as session:
    #     user=session.get(User,user_id)
    #     if not user:
    #         raise HTTPException(
    #             status_code=404,
    #             detail=f"User not found with id {user_id}"
    #         )
    #     if userobj.name is not None:
    #         user.name=userobj.name
    #     if userobj.age is not None:
    #     #Business Logic
    #         if userobj.age < 18:
    #             raise HTTPException(
    #             status_code=400,
    #             detail="User must be al least 18 years"
    #         )
    #     ###############
    #         user.age=userobj.age
    #     session.add(user)
    #     session.commit()
    #     session.refresh(user)
    #     return user

@router.delete("/users/{user_id}")
def del_user(user_id: int,current_user: User = Depends(require_admin)):
    response=delete_user(user_id)
    return response
    #-- whole logic will be performed by user-service--#(tested)
    # with Session(engine) as session:
    #     user=session.get(User, user_id)
    #     if not user:
    #         raise HTTPException(
    #             status_code=404,
    #             detail=f"User not found with id {user_id}"
    #         )
    #     session.delete(user)
    #     session.commit()
    #     return {
    #         "message" : f"User with id {user_id} has been removed successfully"
    #     }