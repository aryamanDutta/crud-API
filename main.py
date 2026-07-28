import sqlite3
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, field_validator

app = FastAPI(
    title="Task API",
    description="A simple CRUD API for managing tasks.",
    version="1.0"
)

# -----------------------------
# Convert FastAPI's default 422
# into assignment-required 400
# -----------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "Invalid request body"
        }
    )


# -----------------------------
# Request Models
# -----------------------------
class TaskCreate(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, value):
        if value.strip() == "":
            raise ValueError("Title cannot be empty")
        return value


class TaskUpdate(BaseModel):
    title: str
    done: bool

    @field_validator("title")
    @classmethod
    def validate_title(cls, value):
        if value.strip() == "":
            raise ValueError("Title cannot be empty")
        return value


# -----------------------------
# SQLite Database
# -----------------------------
conn = sqlite3.connect("tasks.db", check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    done INTEGER NOT NULL
)
""")

conn.commit()

cursor.execute("SELECT COUNT(*) FROM tasks")
count = cursor.fetchone()[0]

if count == 0:
    cursor.executemany(
        "INSERT INTO tasks(title, done) VALUES(?, ?)",
        [
            ("Learn FastAPI", 0),
            ("Build CRUD API", 0),
            ("Push to GitHub", 0)
        ]
    )
    conn.commit()

# -----------------------------
# Root Endpoint
# -----------------------------
@app.get("/", summary="API Information")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": [
            "/tasks"
        ]
    }


# -----------------------------
# Health Endpoint
# -----------------------------
@app.get("/health", summary="Health Check")
def health():
    return {
        "status": "ok"
    }


# -----------------------------
# Get All Tasks
# -----------------------------
@app.get("/tasks", summary="Get All Tasks")
def get_tasks():

    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()

    return [
        {
            "id": row["id"],
            "title": row["title"],
            "done": bool(row["done"])
        }
        for row in rows
    ]


# -----------------------------
# Get Task By ID
# -----------------------------
@app.get("/tasks/{task_id}", summary="Get Task By ID")
def get_task(task_id: int):

    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    )

    row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"])
    }


# -----------------------------
# Create Task
# -----------------------------
@app.post("/tasks", status_code=201, summary="Create Task")
def create_task(task: TaskCreate):

    cursor.execute(
        "INSERT INTO tasks(title, done) VALUES(?, ?)",
        (task.title, 0)
    )

    conn.commit()

    task_id = cursor.lastrowid

    return {
        "id": task_id,
        "title": task.title,
        "done": False
    }

# -----------------------------
# Update Task
# -----------------------------
@app.put("/tasks/{task_id}", summary="Update Task")
def update_task(task_id: int, updated_task: TaskUpdate):

    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    )

    if cursor.fetchone() is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    cursor.execute(
        """
        UPDATE tasks
        SET title = ?, done = ?
        WHERE id = ?
        """,
        (
            updated_task.title,
            int(updated_task.done),
            task_id
        )
    )

    conn.commit()

    return {
        "id": task_id,
        "title": updated_task.title,
        "done": updated_task.done
    }


# -----------------------------
# Delete Task
# -----------------------------
@app.delete("/tasks/{task_id}", status_code=204, summary="Delete Task")
def delete_task(task_id: int):

    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    )

    if cursor.fetchone() is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    cursor.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    conn.commit()

    return