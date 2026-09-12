from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from models import User, Url
from db_models import User as UserDB, Url as UrlDB, create_db_and_tables, SessionDep
from sqlmodel import select
import uvicorn as uv

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/users")
def create_user(user: User, session: SessionDep):
    user_db = session.exec(select(UserDB).where(UserDB.email == user.email)).first()
    if user_db:
        return {"message": "Email already exists"}
    db_user = UserDB(name=user.name,email=user.email)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return {"message": "User created successfully"}


@app.post("/urls")
def create_url(url: Url, session: SessionDep):
    db_url = UrlDB(original_url=url.original_url,expire_at=url.expire_at)
    session.add(db_url)
    session.commit()
    session.refresh(db_url)
    return {"message": "Url created successfully",
    "url": db_url}

@app.get("/urls/{user_id}")
def get_url(user_id: str, session: SessionDep):
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
    url = session.exec(Select(UrlDB).where(UrlDB.short_code == short_code)).first()
    if not url:
        raise HTTPException(status_code=404,detail="url not found")
    
    url.click_count += 1
    session.add(url)
    session.commit()

    original_url = url.original_url
    return RedirectResponse(url=original_url,status_code=302)