from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_database
from app.auth.schemas import UserRegister, UserLogin, UserResponse, TokenResponse
from app.auth.service import (
    get_user_by_email,
    create_user,
    verify_password,
    create_access_token,
    serialize_db_user
)
from app.auth.dependencies import get_current_user
from app.audit_trail.service import log_audit_event

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
async def register(payload: UserRegister, db = Depends(get_database)):
    existing_user = await get_user_by_email(db, payload.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists"
        )
    
    new_user = await create_user(
        db,
        name=payload.name,
        email=payload.email,
        password_raw=payload.password,
        firm_name=payload.firm_name,
        role=payload.role
    )
    
    user_serialized = serialize_db_user(new_user)
    token = create_access_token(data={"sub": user_serialized["id"]})
    
    # Audit log
    await log_audit_event(
        db,
        user_id=user_serialized["id"],
        action="register",
        resource_type="user",
        resource_id=user_serialized["id"],
        details=f"User {payload.email} registered with role {payload.role}"
    )
    
    return {"access_token": token, "token_type": "bearer", "user": user_serialized}

@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, db = Depends(get_database)):
    user = await get_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    user_serialized = serialize_db_user(user)
    token = create_access_token(data={"sub": user_serialized["id"]})
    
    # Audit log
    await log_audit_event(
        db,
        user_id=user_serialized["id"],
        action="login",
        resource_type="user",
        resource_id=user_serialized["id"],
        details=f"User {payload.email} logged in"
    )
    
    return {"access_token": token, "token_type": "bearer", "user": user_serialized}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user = Depends(get_current_user)):
    return current_user
