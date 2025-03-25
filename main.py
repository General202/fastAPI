from fastapi import FastAPI
from pydantic import BaseModel, Field
import json

app = FastAPI()

library = {}

class Book(BaseModel):
    title: str = Field( title = "назва книги", min_length=2, max_length=150)
    author: str = Field( title = "author", min_length=2, max_length=150)
    pages: int = Field( title = "amount of pages", gt = 10)


def load_data():
    try:
        with open("library.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except(FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(data):
    with open("library.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

@app.get("/")
def get_all_books():
    library = load_data()
    return library

@app.post("/books/new")
def add_book(book: Book):
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



