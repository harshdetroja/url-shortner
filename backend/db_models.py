from sqlmodel import SQLModel, Field, Session, create_engine
from datetime import date
from typing import Annotated
from fastapi import Depends 

class User(SQLModel, table=True):

    id: int | None = Field(unique=True,default=None, primary_key=True)
    name: str = Field(default=None)
    email: str = Field(unique=True, nullable=False)
    created_at: date = Field(default_factory=date.today)

class Url(SQLModel, table=True):
    id: str = Field(nullable=False, primary_key=True)
    original_url: str = Field(nullable=False)
    short_code: str = Field(nullable=False, unique=True)
    expire_at: date = Field(default=None)
    click_count: int = Field(default=0)
    created_at: date = Field(default_factory=date.today)
    user_id: str = Field(nullable=False, foreign_key="user.id")


sqlite_file_name = "url_shortener.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
