from fastapi import APIRouter, status #HTTPException
from schema import LoginRequest
from services.auth_service import authenticate_user

router=APIRouter()

#Login (Authentication)
@router.post(
    "/login",status_code=status.HTTP_200_OK
    )
def login(login_data: LoginRequest):
    response=authenticate_user(
        login_data.username,
        login_data.password
        )
    return response
    #-- whole logic will be perfomed by auth-service--#(tested)