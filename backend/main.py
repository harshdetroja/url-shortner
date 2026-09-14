from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from models import UserCreate, UserLogin, Url
from db_models import User as UserDB, Url as UrlDB, create_db_and_tables, SessionDep
from base_62 import encode_base62
from sqlmodel import select
from datetime import date
import uvicorn as uv

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/users/signup")
def create_user(user: UserCreate, session: SessionDep):
    user_db = session.exec(select(UserDB).where(UserDB.email == user.email)).first()
    if user_db:
        return {"message": "Email already exists"}
    db_user = UserDB(name=user.name,email=user.email,password=user.password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return {"message": "User created successfully","user": db_user}

@app.post("/users/login")
def login_user(user:UserLogin, session: SessionDep):
    user_db = session.exec(select(UserDB).where(UserDB.email == user.email)).first()
    if not user_db:
        return HTTPException(status_code=404,detail="User doesn't exists.")
    
    if user_db.password != user.password:
        return {"message":"Incorrect password entered."}
    
    return {"message" : "User successfuly logged in.","user_id":user_db.id}


@app.post("/urls/{user_id}")
def create_url(url: Url, user_id: int, session: SessionDep):
    if url.custom_alias:
        url_db = session.exec(select(UrlDB).where(UrlDB.custom_alias == url.custom_alias)).first()

        if url_db:
            return HTTPException(status_code=409,detail="Custom alias already taken")
    
    db_url = UrlDB(original_url=url.original_url,custom_alias=url.custom_alias,expire_at=url.expire_at,user_id=user_id)
    session.add(db_url)
    session.flush()

    if url.custom_alias:
        db_url.short_code = url.custom_alias
    else:
        db_url.short_code = encode_base62(db_url.id+100000)
    session.commit()
    session.refresh(db_url)
    short_url = f"http://127.0.0.1:8000/{db_url.short_code}"
    return {"message": "Url created successfully",
    "url": short_url}

@app.get("/urls/{user_id}")
def get_url(user_id: int, session: SessionDep):
    urls = session.exec(select(UrlDB).where(UrlDB.user_id == user_id)).all()
    if not urls:
        raise HTTPException(status_code=404, detail="Urls not found")
    return {"message": "Url retrieved successfully",
    "urls": urls}

@app.get("/urls/{short_code}/stats")
def get_click_count(short_code: str, session: SessionDep):
    url = session.exec(select(UrlDB).where(UrlDB.short_code == short_code)).first()
    if not url:
        raise HTTPException(status_code=404, detail="Url not found")
    click_count = url.click_count
    return {"message": "Click count retrieved successfully",
    "short_code": short_code, "click_count": click_count}

@app.delete("/urls/{short_code}")
def delete_url(short_code: str, session: SessionDep):
    url = session.exec(select(UrlDB).where(UrlDB.short_code == short_code)).first()
    if not url:
        raise HTTPException(status_code=404,detail="url not found")
    session.delete(url)
    session.commit()
    return {"message": "Url deleted successfully",
    "short_code": short_code}

@app.get("/{short_code}")
def redirect_to_url(short_code: str, session: SessionDep):
    url = session.exec(select(UrlDB).where(UrlDB.short_code == short_code)).first()
    if not url:
        raise HTTPException(status_code=404,detail="url not found")
    
    if url.expire_at <= date.today():
        delete_url(short_code,session)
        raise HTTPException(status_code=404,detail="url expired")
    
    url.click_count += 1
    session.add(url)
    session.commit()

    original_url = url.original_url
    return RedirectResponse(url=original_url,status_code=302)