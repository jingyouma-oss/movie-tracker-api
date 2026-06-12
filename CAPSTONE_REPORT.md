# Capstone Project Report

**Project Title:** Movie Tracker AI Assistant  
**Student:** Jingyou Ma  
**Course:** CSE552 Full Stack Software Development in the Age of AI Agents  
**Backend Repository:** https://github.com/jingyouma-oss/movie-tracker-api  
**Frontend Repository:** https://github.com/jingyouma-oss/movie-tracker-frontend  

## 1. Project Overview

Movie Tracker AI Assistant is a full stack web application for managing a personal movie watchlist. Users can browse saved movies, add new movies, update their watch status, delete movies, and store review information. The project extends a basic CRUD application into an AI-assisted system by adding personalized recommendations and an agent endpoint that can take actions through tool calls.

The application is designed for students, movie fans, and anyone who wants a simple way to organize movies they have watched, are currently watching, or plan to watch. Instead of only clicking buttons in the UI, users can also interact with an AI assistant using natural language.

## 2. Main Features

- Full movie CRUD: create, read, update, and delete movies.
- PostgreSQL persistence so data remains after server restarts.
- Two related database tables: movies and reviews.
- Next.js frontend with shared navigation, multiple pages, and responsive styling.
- FastAPI backend with organized files for database, models, schemas, and routes.
- AI chat endpoint for general movie discussion.
- Personalized recommendation endpoint that uses the user's saved movies as context.
- AI agent endpoint that can call tools, update records, and return an `agent_steps` log.
- Environment variables for secrets and API URLs.
- `.env` excluded from Git so the Claude API key is not committed.

## 3. Technical Architecture

The application uses a three-layer full stack architecture:

1. **Frontend:** Next.js App Router with TypeScript and Tailwind CSS.
2. **Backend:** FastAPI with Pydantic schemas, CORS middleware, and Anthropic Claude integration.
3. **Database:** PostgreSQL managed through Docker Compose and SQLAlchemy ORM.

The frontend communicates with the backend through `NEXT_PUBLIC_API_URL`. The backend communicates with PostgreSQL through `DATABASE_URL`, and communicates with Claude through `ANTHROPIC_API_KEY`.

```text
Browser
  -> Next.js Frontend
  -> FastAPI Backend
  -> PostgreSQL Database

FastAPI Backend
  -> Claude API for chat, recommendations, and agent reasoning
```

## 4. Database Design

The project uses at least two related tables with a one-to-many relationship.

### Movie Table

The movie table stores the main watchlist records.

- `id`
- `title`
- `director`
- `status`
- `genre`
- `release_year`
- `rating`

### Review Table

The review table stores review records connected to movies.

- `id`
- `movie_id`
- `reviewer_name`
- `content`
- `rating`

One movie can have many reviews. This relationship makes the project more than a simple single-table CRUD demo and matches the full stack project requirement for related database models.

## 5. Backend Implementation

The backend is organized into separate files:

- `database.py` configures the SQLAlchemy engine, session factory, and database dependency.
- `models.py` defines SQLAlchemy database models.
- `schemas.py` defines Pydantic validation and response schemas.
- `main.py` defines FastAPI routes, CORS, AI endpoints, and the agent endpoint.
- `docker-compose.yml` runs PostgreSQL and the backend service.

Important API functionality includes:

- `GET /movies`
- `GET /movies/{movie_id}`
- `POST /movies`
- `PUT /movies/{movie_id}`
- `DELETE /movies/{movie_id}`
- Review routes for movie review records
- `POST /ai/chat`
- `POST /ai/recommend`
- `POST /ai/agent`

The backend validates incoming data with Pydantic schemas and uses SQLAlchemy to read and write persistent records in PostgreSQL.

## 6. Frontend Implementation

The frontend is built with Next.js App Router, TypeScript, and Tailwind CSS. It includes shared navigation and multiple pages:

- Home page
- Movies list page
- Add movie page
- Movie detail page
- AI chat page

The movies page fetches data from the FastAPI backend and displays records in a responsive card grid. The create form allows users to add new movies, while the detail page supports updating and deleting records. The chat page provides AI features through two modes: general movie chat and personalized recommendations.

## 7. AI Recommendation Feature

The recommendation endpoint reads saved movie records from the database and builds a contextual prompt for Claude. This allows the assistant to recommend movies based on the user's actual watch history instead of giving generic suggestions.

For example, if the user has watched science fiction films such as *Inception* and *Interstellar*, the assistant can recommend related movies and explain why they match the user's taste.

## 8. AI Agent Feature

The agent endpoint goes beyond a normal chatbot. Instead of only generating text, it can decide which tools to call in order to complete a user's request.

The agent tools include:

- `get_movies`
- `get_movie_by_id`
- `add_movie`
- `update_movie_status`
- `delete_movie`

The agent loop sends the user's request to Claude with tool definitions. If Claude returns a tool use request, the backend executes the correct Python tool function, adds the result back into the conversation, and continues until Claude produces a final answer. The endpoint returns both the final response and an `agent_steps` list so the tool calls are visible for debugging and grading.

Example multi-step request:

```text
I just finished Dune: Part Two and want to give it 5 stars.
Also, what am I currently watching?
```

This requires the agent to update one movie and then retrieve the currently watching list.

## 9. Security and Reliability

- The Anthropic API key is stored in `.env`, not in source code.
- `.env` is excluded through `.gitignore`.
- CORS is configured so the frontend can communicate with the backend during development.
- PostgreSQL data persists through Docker volumes.
- Pydantic schemas validate request bodies.
- The agent has a maximum iteration limit to prevent infinite tool loops.
- The agent returns tool logs so behavior can be inspected.

## 10. What I Learned

This capstone helped me connect the major topics from the course into one complete project. I practiced building a database-backed API, connecting it to a Next.js frontend, adding AI-powered features, and designing an agent that can call tools. The most important lesson was that an AI agent is different from a normal chatbot because it can reason about a task, choose tools, observe tool results, and continue working until the task is complete.

## 11. Future Improvements

If I continued this project, I would add user authentication, richer review editing, search and filtering by genre, deployment for both frontend and backend, and more careful confirmation steps before destructive actions like deleting a movie. I would also improve the agent UI so users can see each tool call in an expandable "thinking steps" panel.
