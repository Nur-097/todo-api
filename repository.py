import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]


def get_conn():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT FALSE
            )
        """)
        count = conn.execute("SELECT COUNT(*) AS n FROM tasks").fetchone()["n"]
        if count == 0:
            for title, done in [
                ("Buy milk", False),
                ("Walk the dog", True),
                ("Finish assignment", False),
            ]:
                conn.execute(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                    (title, done),
                )
                

def list_tasks():
    with get_conn() as conn:
        return conn.execute("SELECT * FROM tasks ORDER BY id").fetchall()


def get_task(task_id: int):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM tasks WHERE id = %s", (task_id,)
        ).fetchone()

def create_task(title: str):
    with get_conn() as conn:
        return conn.execute(
            "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *",
            (title, False),
        ).fetchone()


def update_task(task_id: int, title: str | None, done: bool | None):
    with get_conn() as conn:
        return conn.execute(
            "UPDATE tasks SET title = COALESCE(%s, title), done = COALESCE(%s, done) "
            "WHERE id = %s RETURNING *",
            (title, done, task_id),
        ).fetchone()


def delete_task(task_id: int) -> bool:
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        return cur.rowcount > 0