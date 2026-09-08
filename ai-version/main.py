import sqlite3
from contextlib import contextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

DB_PATH = "tasks.db"


# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------

@contextmanager
def get_conn():
    """Yield a sqlite3 connection, committing on success and closing always."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Create the tasks table if it doesn't exist, and seed it if empty."""
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        cur = conn.execute("SELECT COUNT(*) AS count FROM tasks")
        count = cur.fetchone()["count"]

        if count == 0:
            seed = [
                ("Buy groceries", 0),
                ("Write project report", 0),
                ("Walk the dog", 1),
            ]
            conn.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)", seed
            )


init_db()


# ---------------------------------------------------------------------------
# Schemas — identical shapes to the original in-memory version
# ---------------------------------------------------------------------------

class Task(BaseModel):
    id: int
    title: str
    done: bool


class TaskCreate(BaseModel):
    title: str
    done: bool = False


class TaskUpdate(BaseModel):
    title: str
    done: bool = False


def row_to_task(row: sqlite3.Row) -> dict:
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/tasks")
def get_tasks():
    with get_conn() as conn:
        rows = conn.execute("SELECT id, title, done FROM tasks").fetchall()
    return [row_to_task(r) for r in rows]


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return row_to_task(row)


@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")

    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (task.title, int(task.done)),
        )
        new_id = cur.lastrowid
        row = conn.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?", (new_id,)
        ).fetchone()

    return row_to_task(row)


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT id FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()

        if existing is None:
            raise HTTPException(status_code=404, detail="Task not found")

        conn.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (task.title, int(task.done), task_id),
        )
        row = conn.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()

    return row_to_task(row)


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT id FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()

        if existing is None:
            raise HTTPException(status_code=404, detail="Task not found")

        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    return {"message": "Task deleted"}