from pydantic import BaseModel, EmailStr
from datetime import datetime, date

class User(BaseModel):

    name: str
    email: EmailStr

class Url(BaseModel):

    original_url: str
    custom_alias: str
    expire_at: date
