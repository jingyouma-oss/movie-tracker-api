from fastapi import FastAPI
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel


app = FastAPI(title="Book Tracker API", version="1.0.0")


class BookCreate(BaseModel):
    title: str
    author: str
    status: str = "want_to_read"
    rating: Optional[int] = None


class BookUpdate(BaseModel):
    status: Optional[str] = None
    rating: Optional[int] = None


books_db = []
next_id = 1


@app.get("/")
def read_root():
    return {"message": "Welcome to Book Tracker API"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/books")
def get_books(status: Optional[str] = None):
    if status:
        return [book for book in books_db if book["status"] == status]
    return books_db


@app.get("/books/{book_id}")
def get_book(book_id: int):
    for book in books_db:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")


@app.post("/books", status_code=201)
def create_book(book: BookCreate):
    global next_id

    new_book = book.model_dump()
    new_book["id"] = next_id
    books_db.append(new_book)
    next_id += 1
    return new_book


@app.put("/books/{book_id}")
def update_book(book_id: int, updates: BookUpdate):
    for book in books_db:
        if book["id"] == book_id:
            if updates.status is not None:
                book["status"] = updates.status
            if updates.rating is not None:
                book["rating"] = updates.rating
            return book
    raise HTTPException(status_code=404, detail="Book not found")


@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    for index, book in enumerate(books_db):
        if book["id"] == book_id:
            books_db.pop(index)
            return {"message": f"Book {book_id} deleted"}
    raise HTTPException(status_code=404, detail="Book not found")
