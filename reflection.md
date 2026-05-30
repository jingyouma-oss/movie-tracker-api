## Week 4 Reflection

1. What is the difference between the SQLAlchemy model and the Pydantic schema?
The SQLAlchemy model defines how data is stored in the database, including the table structure, column types, and constraints. The Pydantic schema defines the shape of request and response data for the API, so FastAPI can validate inputs and serialize outputs.

2. What does `Depends(get_db)` do? Why does every endpoint need it?
`Depends(get_db)` tells FastAPI to run the `get_db()` dependency and inject a database session into the endpoint. Each endpoint needs it because database work should happen inside a managed session that is opened for the request and closed afterward.

3. When you restarted the server and your data was still there — how does that feel compared to storing data in a Python list? What changed architecturally?
It feels much more realistic because the app no longer forgets its data when the process restarts. Architecturally, the source of truth moved from temporary in-memory state to a persistent PostgreSQL database accessed through SQLAlchemy.

4. What was the most confusing part of connecting the frontend to the backend?
The trickiest part was keeping track of which URL belonged to which environment, especially the difference between browser requests to `localhost` and Docker service-to-service connections using `db`. Once the environment variable and CORS settings were correct, the flow made much more sense.

5. When does CORS become a problem and why? In your own words.
CORS becomes a problem when the frontend and backend run on different origins, such as `localhost:3000` and `localhost:8000`, and the browser blocks the request for security reasons. The backend has to explicitly allow the frontend origin so the browser knows the cross-origin request is permitted.

6. What is the difference between `useEffect` with `[]` and without it?
`useEffect` with `[]` runs once after the component mounts, which is ideal for initial data fetching. Without `[]`, the effect runs after every render, which can accidentally cause repeated requests or render loops if the effect updates component state.
