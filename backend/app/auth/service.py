from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt
from passlib.context import CryptContext
from bson import ObjectId
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def serialize_db_user(user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not user:
        return None
    res = user.copy()
    res["id"] = str(res["_id"])
    if "_id" in res:
        del res["_id"]
    if "password_hash" in res:
        del res["password_hash"]
    return res

async def get_user_by_email(db, email: str) -> Optional[Dict[str, Any]]:
    user = await db.users.find_one({"email": email.lower()})
    return user

async def get_user_by_id(db, user_id: str) -> Optional[Dict[str, Any]]:
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        return user
    except Exception:
        return None

async def create_user(db, name: str, email: str, password_raw: str, firm_name: str, role: str) -> Dict[str, Any]:
    hashed = hash_password(password_raw)
    new_user = {
        "name": name,
        "email": email.lower(),
        "password_hash": hashed,
        "firm_name": firm_name,
        "role": role,
        "created_at": datetime.utcnow()
    }
    result = await db.users.insert_one(new_user)
    new_user["_id"] = result.inserted_id
    return new_user
