from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from src.config import app_settings


security = HTTPBearer()


def get_api_key(auth: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if auth is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="API Key not provided"
        )
    if auth.credentials != app_settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key"
        )
    return auth.credentials
