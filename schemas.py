from typing import Optional

from pydantic import BaseModel


class ReviewCreate(BaseModel):
    reviewer_name: str
    comment: str
    score: int
    watched_on: Optional[str] = None


class ReviewResponse(BaseModel):
    id: int
    movie_id: int
    reviewer_name: str
    comment: str
    score: int
    watched_on: Optional[str]

    model_config = {"from_attributes": True}


class MovieCreate(BaseModel):
    title: str
    director: str
    status: str = "want_to_watch"
    genre: str
    release_year: int
    rating: Optional[int] = None


class MovieUpdate(BaseModel):
    status: Optional[str] = None
    genre: Optional[str] = None
    release_year: Optional[int] = None
    rating: Optional[int] = None


class MovieResponse(BaseModel):
    id: int
    title: str
    director: str
    status: str
    genre: str
    release_year: int
    rating: Optional[int]

    model_config = {"from_attributes": True}


class MovieDetailResponse(MovieResponse):
    reviews: list[ReviewResponse]
