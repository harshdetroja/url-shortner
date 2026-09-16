import os
from datetime import datetime, timedelta
from typing import Union, Any, Optional

from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from pwdlib import PasswordHash
from sqlmodel import select
from dotenv import load_dotenv

from db_models import SessionDep, User as UserDB

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv('REFRESH_TOKEN_EXPIRE_MINUTES', 10080))
ALGORITHM = os.getenv('ALGORITHM', 'HS256')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_REFRESH_SECRET_KEY = os.getenv('JWT_REFRESH_SECRET_KEY')

pwd_context = PasswordHash.recommended()

def get_hashed_pwd(password: str) -> str:
    return pwd_context.hash(password)

def verify_pwd(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password,hashed_password)

def create_access_token(subject: Union[str,Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp":expires_delta, "sub":str(subject)}
    encode_jwt = jwt.encode(to_encode,JWT_SECRET_KEY, ALGORITHM)
    return encode_jwt

def create_refresh_token(subject: Union[str,Any],expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp":expires_delta, "sub":str(subject)}
    encode_jwt = jwt.encode(to_encode,JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encode_jwt

def decode_token(token: str):

    try:
        payload = jwt.decode(token,JWT_SECRET_KEY,ALGORITHM)
        return payload
    except JWTError:
        return None

def decode_refresh_token(token: str):

    try:
        payload = jwt.decode(token,JWT_REFRESH_SECRET_KEY,ALGORITHM)
        return payload
    except JWTError:
        return None
    
class JWTBearer(HTTPBearer):

    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:

        credentials: HTTPAuthorizationCredentials = await super(JWTBearer,self).__call__(request)


        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403,detail="Invalid authentication scheme.")
            token = credentials.credentials
            return token
        else:
            raise HTTPException(status_code=403,detail="Invalid authorization code")


def verify_refresh_request(session: SessionDep, token: str = Depends(JWTBearer())):

    payload = decode_refresh_token(token)


    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or expired token"
        )
    
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or expired token"
        )
    
    user = session.exec(select(UserDB).where(UserDB.id == user_id)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

def verify_user(session: SessionDep, token: str = Depends(JWTBearer())):

    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or expired token"
        )
    
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or expired token"
        )
    
    user = session.exec(select(UserDB).where(UserDB.id == user_id)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user