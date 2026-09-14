from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date

class UserCreate(BaseModel):

    name: str
    email: EmailStr
    password: str = Field(min_length=8,max_length=12)

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8,max_length=12)

class Url(BaseModel):

    original_url: str
    custom_alias: str
    expire_at: date
