import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

from settings import settings
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import jwt

from database import database_connection
from models.User import User as UserModel
from sqlalchemy import select

secret_key = settings.JWT_SECRET_KEY
algorithm = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None  

class UserOut(BaseModel):
    username: str
    email: str

    class Config:
        from_attributes = True

class UserInDB(UserOut):
    hashed_password: str

class LoginForm(BaseModel):
    email: str
    password: str

class RegisterForm(BaseModel):
    username: str
    email: str
    password: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
router = APIRouter(prefix="/auth", tags=["auth"])
ph = PasswordHasher()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return ph.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False

def get_password_hash(password: str) -> str:
    return ph.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=algorithm)

def decode_access_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        email: str | None = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        return TokenData(email=email)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


# --- DB helpers ---

async def get_user_by_email(email: str, db: database_connection) -> UserModel | None:
    result = await db.execute(select(UserModel).where(UserModel.email == email))
    return result.scalar_one_or_none()

async def authenticate_user(email: str, password: str, db: database_connection) -> UserModel | None:
    user = await get_user_by_email(email, db)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: database_connection,
) -> UserModel:
    token_data = decode_access_token(token)
    user = await get_user_by_email(token_data.email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

current_user_dep = Annotated[UserModel, Depends(get_current_user)]

@router.post("/token", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: database_connection):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserOut)
async def read_current_user(current_user: current_user_dep):
    return current_user
@router.patch("/me", response_model=UserOut)
async def update_current_user(current_user: current_user_dep, form: RegisterForm, db: database_connection):
    if form.username:
        current_user.username = form.username
    if form.email:
        current_user.email = form.email
    if form.password:
        current_user.hashed_password = get_password_hash(form.password)
    db.add(current_user)
    await db.flush()
    await db.refresh(current_user)
    return current_user
@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(current_user: current_user_dep, db: database_connection):
    await db.delete(current_user)
    await db.flush()
    return None
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(form: RegisterForm, db: database_connection):
    existing = await db.execute(
        select(UserModel).where(
            (UserModel.email == form.email) | (UserModel.username == form.username)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered",
        )

    user = UserModel(
        username=form.username,
        email=form.email,
        hashed_password=get_password_hash(form.password),
    )
    db.add(user)
    await db.flush()  
    await db.refresh(user)
    return user

@router.get("/debug/{email}")
async def debug_user(email: str, db: database_connection):
    user = await get_user_by_email(email, db)
    if not user:
        return {"found": False}
    return {
        "found": True,
        "email": user.email,
        "username": user.username,
        "hash_preview": user.hashed_password[:20],
    }