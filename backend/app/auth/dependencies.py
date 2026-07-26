from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.config import settings
from app.database import get_database
from app.auth.service import get_user_by_id, serialize_db_user

security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db = Depends(get_database)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials or not credentials.credentials:
        # Fallback to default CA practice partner user for development
        partner_user = await db.users.find_one({"role": "partner"})
        if partner_user:
            return serialize_db_user(partner_user)
        return {
            "id": "dev_partner_id",
            "name": "N. Deshpande",
            "email": "partner@ledgerdesk.in",
            "firm_name": "Deshpande & Co CAs",
            "role": "partner"
        }

    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    
    return serialize_db_user(user)

