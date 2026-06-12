# Capstone Demo Script

## Start the Backend

```powershell
cd C:\Users\84793\Documents\Codex\2026-05-30\movie-tracker-api
docker compose up --build
```

Backend API docs:

```text
http://localhost:8000/docs
```

## Start the Frontend

Open a second PowerShell window:

```powershell
cd C:\Users\84793\Documents\Codex\2026-05-30\movie-tracker-frontend
npm run dev
```

Frontend app:

```text
http://localhost:3000
```

## Demo Flow

1. Open `http://localhost:3000/movies`.
2. Show the movie list with multiple saved records.
3. Click `Add Movie` and show the create form.
4. Add a new movie and confirm it appears in the list.
5. Open a movie detail page and show update/delete functionality.
6. Open `http://localhost:3000/chat`.
7. Switch to `Movie Recommendations`.
8. Ask:

```text
Based on my watched movies, what should I watch next?
```

9. Take a screenshot showing the personalized AI recommendation.
10. Open `http://localhost:8000/docs`.
11. Run `POST /ai/agent` with:

```json
{
  "message": "I just finished Dune: Part Two and want to give it 5 stars. Also, what am I currently watching?"
}
```

12. Take a screenshot showing the response and `agent_steps` with multiple tool calls.

## Submission Checklist

- Backend GitHub repository link.
- Frontend GitHub repository link.
- Screenshot showing the app listing records or the AI recommendation.
- Screenshot showing `/ai/agent` with multiple tool calls.
- `CAPSTONE_REPORT.md` or `capstone_submission.txt` if the course portal allows file uploads.
