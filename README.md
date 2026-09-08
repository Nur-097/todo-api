# Task API

A simple CRUD (Create, Read, Update, Delete) API for managing a to-do list, built with FastAPI as part of the FlyRank Internship Backend Track. Data is stored in a SQLite database (`tasks.db`), so it survives a server restart.

## Why SQLite

SQLite was chosen because it's a single file with no separate server to install or run — perfect for a small project like this. It gives real persistence (data survives restarts) without any setup overhead, and it's built directly into Python's standard library.

## Where the database lives

`tasks.db` is created automatically the first time the app runs. It's git-ignored, so a fresh clone won't include it — instead, the app creates the file, creates the `tasks` table, and seeds 3 example tasks the first time it starts up. Restarting the server does not duplicate the seed data.

## How to run it

1. Clone this repo and move into it:

git clone https://github.com/Nur-097/todo-api.git
cd todo-api


2. Create and activate a virtual environment:

python -m venv venv
venv\Scripts\Activate.ps1


3. Install dependencies:

pip install fastapi uvicorn


4. Run the server:

uvicorn main:app --reload


5. Visit `http://localhost:8000` in your browser. On first run, `tasks.db` is created automatically with 3 example tasks.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Basic info about the API |
| GET | `/health` | Health check |
| GET | `/tasks` | List all tasks |
| GET | `/tasks/{id}` | Get a single task by id |
| POST | `/tasks` | Create a new task (requires a non-empty `title`) |
| PUT | `/tasks/{id}` | Update a task's title and/or done status |
| DELETE | `/tasks/{id}` | Delete a task |

All endpoints behave exactly as they did with the in-memory version from Assignment 1 — only the storage layer underneath changed, from a Python list to SQLite.

## Example request

curl -i http://localhost:8000/tasks/1

HTTP/1.1 200 OK
content-type: application/json

{"id":1,"title":"Buy milk","done":0}


## Swagger UI

Interactive API docs are available at `http://localhost:8000/docs` once the server is running — you can try every endpoint directly from the browser.

![Swagger UI screenshot](swagger-screenshot.png)

## Stage 4 — Exploring SQLite

Opened `tasks.db` directly in DB Browser for SQLite and ran queries by hand, confirming the API and DB Browser read the exact same file with no syncing required.

Ran `SELECT * FROM tasks WHERE done = 1;` in DB Browser — returned the single completed task ("Walk the dog"), confirming filtering works directly against the SQLite file.

Also confirmed that running `UPDATE tasks SET done = 1;` in DB Browser was reflected instantly through `GET /tasks` with no server restart, and that deleting all rows and restarting the server correctly re-triggered the seed logic — proving the seed-only-when-empty check works as intended.

![DB Browser screenshot](db-browser-screenshot.png)