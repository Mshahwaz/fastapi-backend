from fastapi import APIRouter, status, BackgroundTasks, HTTPException, Depends
from schema import (
    User_create,
    UserResponse,
    UserUpdate
    # LoginRequest
)
from models import User  
from sqlmodel import Session
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
from database import get_session

logging.basicConfig(
    level=logging.INFO
)
logger=logging.getLogger(__name__)
router=APIRouter()


#CREATE USER 
@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse
    )
def register_user(user: User_create,session: Session = Depends(get_session)):
    response=create_user(user,session)
    return response
    #-- whole logic will be performed by user-service--#(tested)


#GET ALL USERS
@router.get(
    "/users",
    response_model=list[UserResponse]
    )
def get_users(session: Session = Depends(get_session)):
    response=get_all_users(session)
    return response
    #-- whole logic will be performed by user-service--#(tested)

# # GET A Single User with user id
@router.get(
    "/users/{user_id}",
    response_model=UserResponse
    )
def get_user(user_id: int,session: Session = Depends(get_session)):
    response=get_single_user(user_id,session)
    return response
    #-- whole logic will be performed by user-service--#(tested)


#UPDATE USER DATA
@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK
    )
def update_user(userobj: User_create,user_id: int,session: Session = Depends(get_session)):
    response=update_user_with_id(user_id,userobj,session)
    return response
    #-- whole logic will be performed by user-service--#(tested)


#PATCH USER FEILDS
@router.patch(
    "/users/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK
    )
def patch_user(userobj: UserUpdate,user_id: int,session: Session = Depends(get_session)):
    response=patch_user_with_userid(userobj,user_id,session)
    return response
    #-- whole logic will be performed by user-service--#(tested)


@router.delete("/users/{user_id}")
def del_user(user_id: int,current_user: User = Depends(require_admin),session: Session = Depends(get_session)):
    response=delete_user(user_id,session)
    return response
    #-- whole logic will be performed by user-service--#(tested)