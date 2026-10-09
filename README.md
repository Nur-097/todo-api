# Task API

A CRUD to-do list API built with FastAPI and PostgreSQL, fully containerized with Docker Compose. Built for the FlyRank Internship Backend Track. The same API has run on three storage engines: memory (A1), SQLite (A2), and now Postgres in Docker (A3).

## Run everything (one command)

```
cp .env.example .env      # Windows PowerShell: copy .env.example .env
docker compose up --build
```

The API runs at http://localhost:8000 (Swagger UI at /docs). Postgres runs in its own container with a volume, so data survives `docker compose down` and `up`. On first start the `tasks` table is created and 3 example tasks are seeded, only if the table is empty.

## Environment variables

See `.env.example`. `DATABASE_URL` is used when running the app locally; docker compose sets its own connection string pointing at the `db` service. `.env` is git-ignored, and no credentials are hardcoded in the app code.

## Endpoints

| Method | Path | Success | Errors |
|--------|------|---------|--------|
| GET | / | 200 | |
| GET | /health | 200 | |
| GET | /tasks | 200 | |
| GET | /tasks/{id} | 200 | 404 |
| POST | /tasks | 201 | 400 |
| PUT | /tasks/{id} | 200 | 400, 404 |
| DELETE | /tasks/{id} | 204 | 404 |

Errors return JSON like `{"error": "Task not found"}`. All database access uses parameterized queries and lives in `repository.py`.

## Example

```
curl.exe -i http://localhost:8000/tasks

HTTP/1.1 200 OK
server: uvicorn
content-type: application/json

[{"id":1,"title":"Buy milk","done":false},{"id":2,"title":"Walk the dog","done":true},{"id":3,"title":"Finish assignment","done":false},{"id":4,"title":"Test Docker","done":false}]
```

## Data in Postgres

![Postgres data](db-postgres-screenshot.png)

## Swagger UI

Interactive docs at http://localhost:8000/docs.

![Swagger UI screenshot](swagger-screenshot.png)

## Run Postgres by hand (optional)

`docker compose up` already starts the database for you. To run only the database container yourself:

```
docker run --name taskdb -e POSTGRES_PASSWORD=dev -e POSTGRES_DB=tasks -p 5433:5432 -v taskdata:/var/lib/postgresql -d postgres
```

Port 5433 is used on the host because a local PostgreSQL service may already occupy 5432. Inside the container Postgres still listens on 5432. The volume is mounted at `/var/lib/postgresql` (not `.../data`) because Postgres 18+ images store data in a versioned subdirectory.

## Running without Docker for the app

1. `python -m venv venv` then `venv\Scripts\Activate.ps1`
2. `pip install -r requirements.txt`
3. Start the database (section above), set `DATABASE_URL` in `.env` to `postgres://postgres:dev@localhost:5433/tasks`
4. `uvicorn main:app --reload`

## History

- **A1:** in-memory list.
- **A2:** SQLite (`tasks.db`) with raw `sqlite3`. The AI-vs-me comparison for that assignment is in git history (tag `a2-done`).
- **A3:** this version.