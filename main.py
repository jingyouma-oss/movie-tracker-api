from contextlib import asynccontextmanager

import anthropic
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from pydantic import ValidationError

from database import Base, SessionLocal, engine, get_db
from models import Movie, Review
from schemas import (
    AgentRequest,
    ChatRequest,
    MovieCreate,
    MovieDetailResponse,
    MovieResponse,
    MovieUpdate,
    ReviewCreate,
    ReviewResponse,
)


Base.metadata.create_all(bind=engine)
ai_client = anthropic.Anthropic()

GENERAL_SYSTEM_PROMPT = """You are a helpful movie assistant for a personal movie tracking app.
Help users discuss movies they have watched, explore genres, compare directors, and discover what to watch next.
Be conversational, enthusiastic about movies, and concise in your responses."""

RECOMMENDATION_PROMPT_TEMPLATE = """You are a personalized movie recommendation assistant.

{movie_context}

Based on this viewing history, provide thoughtful and specific recommendations.
Explain why each recommendation matches their taste.
Keep responses concise and give 2-3 recommendations unless asked for more."""

AGENT_SYSTEM_PROMPT = """You are an AI agent for a personal movie tracker.
You can look up movies, add new ones, update a movie's status and rating, and delete movies.
Use tools whenever you need to inspect or change the saved collection.
Do not guess which movies are in the tracker when you can check with a tool first.
If a request refers to a movie indirectly, use the tools to identify the correct movie before taking action.
After using tools, give a clear and concise final answer summarizing what you did."""

# Week 6 Agent Loop Notes
# 1. When response.stop_reason == "tool_use", the model is asking the app to execute
#    one or more tools before it can finish the answer.
# 2. tool_use_id links each returned tool result to the exact tool call that produced it,
#    so the model knows which output belongs to which request.
# 3. Tool results are added back as a "user" role message because they become fresh
#    context for the next model turn, similar to the environment reporting new facts.
# 4. Without a max-iterations safeguard, a bad prompt or tool loop could keep calling
#    tools forever and never return a final answer.

tools = [
    {
        "name": "get_movies",
        "description": "Get movies from the tracker. Optionally filter by status such as watched, watching, or want_to_watch.",
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": "Optional movie status filter. Use watched, watching, or want_to_watch.",
                }
            },
            "required": [],
        },
    },
    {
        "name": "get_movie_by_id",
        "description": "Get one saved movie by its numeric id when you already know which movie record to inspect.",
        "input_schema": {
            "type": "object",
            "properties": {
                "movie_id": {
                    "type": "integer",
                    "description": "The numeric id of the movie to retrieve.",
                }
            },
            "required": ["movie_id"],
        },
    },
    {
        "name": "add_movie",
        "description": "Add a new movie to the tracker with its title, director, genre, release year, and optional status or rating.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Movie title."},
                "director": {"type": "string", "description": "Movie director."},
                "genre": {"type": "string", "description": "Movie genre."},
                "release_year": {
                    "type": "integer",
                    "description": "Movie release year as a four-digit number.",
                },
                "status": {
                    "type": "string",
                    "description": "Optional status. Use watched, watching, or want_to_watch.",
                },
                "rating": {
                    "type": "integer",
                    "description": "Optional user rating from 1 to 5.",
                },
            },
            "required": ["title", "director", "genre", "release_year"],
        },
    },
    {
        "name": "update_movie_status",
        "description": "Update an existing movie's status and optionally set its rating when the user says they started, finished, or rated a movie.",
        "input_schema": {
            "type": "object",
            "properties": {
                "movie_id": {
                    "type": "integer",
                    "description": "The numeric id of the movie to update.",
                },
                "status": {
                    "type": "string",
                    "description": "New movie status. Use watched, watching, or want_to_watch.",
                },
                "rating": {
                    "type": "integer",
                    "description": "Optional new rating from 1 to 5.",
                },
            },
            "required": ["movie_id", "status"],
        },
    },
    {
        "name": "delete_movie",
        "description": "Delete a movie from the tracker when the user wants to remove it from their collection.",
        "input_schema": {
            "type": "object",
            "properties": {
                "movie_id": {
                    "type": "integer",
                    "description": "The numeric id of the movie to delete.",
                }
            },
            "required": ["movie_id"],
        },
    },
]


def seed_database():
    db = SessionLocal()
    try:
      if db.query(Movie).count() > 0:
          return

      seeded_movies = [
          Movie(
              title="Inception",
              director="Christopher Nolan",
              status="watched",
              genre="Sci-Fi",
              release_year=2010,
              rating=5,
          ),
          Movie(
              title="Interstellar",
              director="Christopher Nolan",
              status="watched",
              genre="Sci-Fi",
              release_year=2014,
              rating=5,
          ),
          Movie(
              title="Spirited Away",
              director="Hayao Miyazaki",
              status="watched",
              genre="Animation",
              release_year=2001,
              rating=5,
          ),
          Movie(
              title="Parasite",
              director="Bong Joon-ho",
              status="watching",
              genre="Thriller",
              release_year=2019,
              rating=4,
          ),
          Movie(
              title="Dune: Part Two",
              director="Denis Villeneuve",
              status="want_to_watch",
              genre="Sci-Fi",
              release_year=2024,
              rating=None,
          ),
      ]

      db.add_all(seeded_movies)
      db.commit()

      for movie in seeded_movies:
          db.refresh(movie)

      seeded_reviews = [
          Review(
              movie_id=seeded_movies[0].id,
              reviewer_name="Jingyou Ma",
              comment="A smart, layered story with impressive visuals.",
              score=5,
              watched_on="2026-05-30",
          ),
          Review(
              movie_id=seeded_movies[1].id,
              reviewer_name="Jingyou Ma",
              comment="Emotional and visually stunning from beginning to end.",
              score=5,
              watched_on="2026-05-28",
          ),
          Review(
              movie_id=seeded_movies[2].id,
              reviewer_name="Jingyou Ma",
              comment="Beautiful animation and a memorable coming-of-age story.",
              score=5,
              watched_on="2026-05-12",
          ),
          Review(
              movie_id=seeded_movies[3].id,
              reviewer_name="Jingyou Ma",
              comment="Tense and thoughtful so far. I still need to finish it.",
              score=4,
              watched_on="2026-05-27",
          ),
          Review(
              movie_id=seeded_movies[0].id,
              reviewer_name="Movie Club",
              comment="The ending always makes me think about the whole plot again.",
              score=5,
              watched_on="2026-04-18",
          ),
      ]

      db.add_all(seeded_reviews)
      db.commit()
    finally:
      db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_database()
    yield


app = FastAPI(title="Movie Tracker API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to Movie Tracker API"}


@app.get("/health")
def health():
    return {"status": "ok"}


def ensure_ai_key():
    if not ai_client.api_key:
        raise HTTPException(
            status_code=500,
            detail="ANTHROPIC_API_KEY is missing. Add it to the backend .env file before using AI features.",
        )


def build_history_payload(request: ChatRequest) -> list[dict[str, str]]:
    try:
        history = [message.model_dump() for message in request.conversation_history]
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return history + [{"role": "user", "content": request.message}]


def request_claude_reply(messages: list[dict[str, str]], system_prompt: str) -> str:
    ensure_ai_key()
    response = ai_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
    )
    return response.content[0].text


def serialize_movie(movie: Movie) -> dict[str, int | str | None]:
    return {
        "id": movie.id,
        "title": movie.title,
        "director": movie.director,
        "status": movie.status,
        "genre": movie.genre,
        "release_year": movie.release_year,
        "rating": movie.rating,
    }


def get_movies_fn(db: Session, status: str | None = None) -> list[dict[str, int | str | None]]:
    query = db.query(Movie)
    if status:
        query = query.filter(Movie.status == status)
    movies = query.order_by(Movie.id.asc()).all()
    return [serialize_movie(movie) for movie in movies]


def get_movie_by_id_fn(db: Session, movie_id: int) -> dict[str, int | str | None]:
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie is None:
        return {"error": "Movie not found", "movie_id": movie_id}
    return serialize_movie(movie)


def add_movie_fn(
    db: Session,
    title: str,
    director: str,
    genre: str,
    release_year: int,
    status: str = "want_to_watch",
    rating: int | None = None,
) -> dict[str, int | str | None]:
    movie = Movie(
        title=title,
        director=director,
        genre=genre,
        release_year=release_year,
        status=status,
        rating=rating,
    )
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return serialize_movie(movie)


def update_movie_status_fn(
    db: Session,
    movie_id: int,
    status: str,
    rating: int | None = None,
) -> dict[str, int | str | None]:
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie is None:
        return {"error": "Movie not found", "movie_id": movie_id}

    movie.status = status
    if rating is not None:
        movie.rating = rating

    db.commit()
    db.refresh(movie)
    return serialize_movie(movie)


def delete_movie_fn(db: Session, movie_id: int) -> dict[str, int | str | bool]:
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie is None:
        return {"error": "Movie not found", "movie_id": movie_id}

    title = movie.title
    db.delete(movie)
    db.commit()
    return {"success": True, "movie_id": movie_id, "title": title}


def run_agent(
    user_message: str,
    tool_functions: dict[str, callable],
    db: Session,
    max_iterations: int = 5,
) -> tuple[str, list[dict]]:
    ensure_ai_key()
    messages: list[dict] = [{"role": "user", "content": user_message}]
    agent_steps: list[dict] = []

    for _ in range(max_iterations):
        response = ai_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=AGENT_SYSTEM_PROMPT,
            messages=messages,
            tools=tools,
        )

        if response.stop_reason != "tool_use":
            final_text = "".join(
                block.text for block in response.content if getattr(block, "type", None) == "text"
            ).strip()
            return final_text, agent_steps

        assistant_blocks = []
        tool_result_blocks = []

        for block in response.content:
            assistant_blocks.append(block)

            if getattr(block, "type", None) != "tool_use":
                continue

            tool_name = block.name
            tool_input = block.input
            result = tool_functions[tool_name](db=db, **tool_input)
            agent_steps.append(
                {
                    "tool": tool_name,
                    "input": tool_input,
                    "result": result,
                }
            )
            tool_result_blocks.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result),
                }
            )

        messages.append({"role": "assistant", "content": assistant_blocks})
        messages.append({"role": "user", "content": tool_result_blocks})

    return "I reached the maximum number of tool steps before finishing the request.", agent_steps


def build_movie_context(db: Session) -> str:
    movies = db.query(Movie).order_by(Movie.rating.desc().nullslast(), Movie.id.asc()).all()
    watched_movies = [movie for movie in movies if movie.status == "watched"]
    watching_movies = [movie for movie in movies if movie.status == "watching"]
    want_to_watch = [movie for movie in movies if movie.status == "want_to_watch"]

    context = "Here is the user's movie library:\n"

    if watched_movies:
        context += "\nWatched movies:\n"
        for movie in watched_movies:
            rating_str = f" (rated {movie.rating}/5)" if movie.rating else ""
            context += f"- {movie.title} directed by {movie.director}, {movie.genre}, {movie.release_year}{rating_str}\n"

    if watching_movies:
        context += "\nCurrently watching:\n"
        for movie in watching_movies:
            context += f"- {movie.title} directed by {movie.director}, {movie.genre}, {movie.release_year}\n"

    if want_to_watch:
        context += "\nWant to watch:\n"
        for movie in want_to_watch:
            context += f"- {movie.title} directed by {movie.director}, {movie.genre}, {movie.release_year}\n"

    if not movies:
        context += "No movies tracked yet.\n"

    return context


@app.get("/movies", response_model=list[MovieResponse])
def get_movies(status: str | None = None, genre: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Movie)
    if status:
        query = query.filter(Movie.status == status)
    if genre:
        query = query.filter(Movie.genre == genre)
    return query.order_by(Movie.id.asc()).all()


@app.get("/movies/stats")
def get_movie_stats(db: Session = Depends(get_db)):
    total_movies = db.query(Movie).count()
    status_rows = db.query(Movie.status, func.count(Movie.id)).group_by(Movie.status).all()
    status_counts = {status: count for status, count in status_rows}
    average_rating = db.query(func.avg(Movie.rating)).filter(Movie.rating.is_not(None)).scalar()
    total_reviews = db.query(Review).count()

    return {
        "total_movies": total_movies,
        "total_reviews": total_reviews,
        "by_status": {
            "want_to_watch": status_counts.get("want_to_watch", 0),
            "watching": status_counts.get("watching", 0),
            "watched": status_counts.get("watched", 0),
        },
        "average_rating": average_rating,
    }


@app.get("/movies/{movie_id}", response_model=MovieDetailResponse)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@app.post("/movies", response_model=MovieResponse, status_code=201)
def create_movie(data: MovieCreate, db: Session = Depends(get_db)):
    movie = Movie(**data.model_dump())
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie


@app.put("/movies/{movie_id}", response_model=MovieResponse)
def update_movie(movie_id: int, updates: MovieUpdate, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(movie, field, value)

    db.commit()
    db.refresh(movie)
    return movie


@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    db.delete(movie)
    db.commit()
    return {"message": f"Movie {movie_id} deleted"}


@app.get("/movies/{movie_id}/reviews", response_model=list[ReviewResponse])
def get_movie_reviews(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return db.query(Review).filter(Review.movie_id == movie_id).order_by(Review.id.asc()).all()


@app.post("/movies/{movie_id}/reviews", response_model=ReviewResponse, status_code=201)
def create_review(movie_id: int, data: ReviewCreate, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    review = Review(movie_id=movie_id, **data.model_dump())
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@app.delete("/reviews/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")

    db.delete(review)
    db.commit()
    return {"message": f"Review {review_id} deleted"}


@app.post("/ai/chat")
def chat_with_assistant(request: ChatRequest):
    messages = build_history_payload(request)
    reply = request_claude_reply(messages, GENERAL_SYSTEM_PROMPT)
    return {
        "reply": reply,
        "updated_history": messages + [{"role": "assistant", "content": reply}],
    }


@app.post("/ai/recommend")
def get_recommendations(request: ChatRequest, db: Session = Depends(get_db)):
    messages = build_history_payload(request)
    system_prompt = RECOMMENDATION_PROMPT_TEMPLATE.format(
        movie_context=build_movie_context(db)
    )
    reply = request_claude_reply(messages, system_prompt)
    return {
        "reply": reply,
        "updated_history": messages + [{"role": "assistant", "content": reply}],
    }


@app.post("/ai/agent")
def movie_agent(request: AgentRequest, db: Session = Depends(get_db)):
    tool_functions = {
        "get_movies": get_movies_fn,
        "get_movie_by_id": get_movie_by_id_fn,
        "add_movie": add_movie_fn,
        "update_movie_status": update_movie_status_fn,
        "delete_movie": delete_movie_fn,
    }
    response_text, agent_steps = run_agent(request.message, tool_functions, db)
    return {
        "response": response_text,
        "agent_steps": agent_steps,
    }
