from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    director = Column(String, nullable=False)
    status = Column(String, nullable=False, default="want_to_watch")
    genre = Column(String, nullable=False)
    release_year = Column(Integer, nullable=False)
    rating = Column(Integer, nullable=True)

    reviews = relationship(
        "Review",
        back_populates="movie",
        cascade="all, delete-orphan",
    )


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False, index=True)
    reviewer_name = Column(String, nullable=False)
    comment = Column(Text, nullable=False)
    score = Column(Integer, nullable=False)
    watched_on = Column(String, nullable=True)

    movie = relationship("Movie", back_populates="reviews")
