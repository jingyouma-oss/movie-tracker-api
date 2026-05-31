# Movie Tracker API

This FastAPI backend powers the Movie Tracker app for CSE552 Mini Project 2. It uses SQLAlchemy with PostgreSQL and exposes CRUD endpoints for movies and reviews.

## Main features

- movie list, detail, create, update, and delete endpoints
- review list, create, and delete endpoints
- one-to-many relationship between `movies` and `reviews`
- automatic sample data seeding for quick demos
- CORS enabled for the local Next.js frontend

## Run locally

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000` and Swagger docs at `http://localhost:8000/docs`.
