from fastapi import Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.core.security import verify_token
from app.core.exceptions import APIException
from app.core.error_codes import ErrorCode
from app.repositories.user_repo import UserRepository

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = verify_token(token)
    user_id = payload.get("sub")
    
    if user_id is None:
        raise APIException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=ErrorCode.INVALID_TOKEN
        )
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(int(user_id))
    
    if user is None:
        raise APIException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=ErrorCode.USER_NOT_FOUND
        )
    
    return user