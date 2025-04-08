from typing import Annotated
from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from jose import JWTError, jwt
from datetime import datetime, timedelta


import json

SECRET_KEY = "19109197bd5e7c289b92b2b355083ea26c71dee2085ceccc19308a7291b2ea06"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60*24*7

app = FastAPI()

templates = Jinja2Templates(directory="templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str


class UserInDB(User):
    hashed_password: str

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    
def token_create(data: dict):
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def authenticate_user(username: str, password: str):
    users = load_data("users.json")
    user = get_user(users, username)
    if user and password == user.hashed_password:
        return user
    
    return False


class Book(BaseModel):
    title: str = Field( title = "назва книги", min_length=2, max_length=150)
    author: str = Field( title = "author", min_length=2, max_length=150)
    pages: int = Field( title = "amount of pages", gt = 10)
    #picture: str = Field( title = "")


def load_data(filename="library.json"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except(FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(data):
    with open("library.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        return {"error": "Неправильний логін або пароль"}
    
    assess_token = token_create({"sub": user.username})
    return {"acces_token": user.username, "token_type": "bearer"}


@app.get("/")
def get_all_books(request: Request):
    library = load_data()
    return templates.TemplateResponse("index.html", {"request": request, "library": library})


@app.post("/books/new")
def add_book(book: Book, token: Annotated[str, Depends(oauth2_scheme)]):
    library = load_data()

    if book.author not in library:
        library[book.author] = []
    library[book.author].append(book.dict())
    save_data(library)
    return library


@app.put("/books/update")
def update_book(book: Book):
    library = load_data()

    if book.title in library:
        library[book.title] = book
        return {"message": "Книгу успішно оновлено!"}
    else:
        return {"message": "Книгу не знайдено!"}


@app.delete("/books/delete")
def delete_book(author: str, title: str):
    library = load_data()

    if author in library:
        for book in library[author]:
            if book["title"] == title:
                library[author].remove(book)
                save_data(library)
                return {"message": "Книгу успішно видалено!"}
            
    return {"message": "Книгу не знайдено!"}


@app.get("/books/{author}")
def get_author_books(author: str):
    library = load_data()
    if author in library:
        return library[author]
    else:
        return {"message": "Книг цього автора не знайдено!"}



