from fastapi import HTTPException, Depends
from sqlmodel import Session, select
from models import User
from database import engine
from fastapi.security import HTTPAuthorizationCredentials , HTTPBearer
from config import (
    SECRET_KEY,
    ALGORITHM
)
from jose import jwt, JWTError

security=HTTPBearer()

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