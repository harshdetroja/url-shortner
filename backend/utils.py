from passlib.context import CryptContext
from jose import jwt
import os 
from datetime import datetime, timedelta
from typing import Union, Any


ACCESS_TOKEN_EXPIRE_MINUTES = os.environ['ACCESS_TOKEN_EXPIRE_MINUTES']  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = os.environ['REFRESH_TOKEN_EXPIRE_MINUTES'] # 7 days
ALGORITHM = os.environ['ALGORITHM']
JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']   # should be kept secret
JWT_REFRESH_SECRET_KEY = os.environ['JWT_REFRESH_SECRET_KEY']    # should be kept secret

pwd_context = CryptContext(schemes=["bycrypt"],deprecated=auto)

def get_hashed_pwd(password: str) -> str:
    return pwd_context.hash(password)

def verify_pwd(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password,hashed_password)

def create_access_token(subject: Union[str,Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta()
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp":expires_delta, "sub":str(subject)}
    encode_jwt = jwt.encode(to_encode,JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str,Any],expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta()
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp":expires_delta, "sub":str(subject)}
    encode_jwt = jwt.encode(to_encode,JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt