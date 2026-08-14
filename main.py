import os

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, field_validator


# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")


# -----------------------------
# FastAPI Application
# -----------------------------
app = FastAPI(
    title="Task API",
    description="A simple CRUD API for managing tasks.",
    version="1.0"
)


# -----------------------------
# Database Connection
# -----------------------------
conn = psycopg.connect(
    DATABASE_URL,
    row_factory=dict_row
)


# -----------------------------
# Create Database Table
# -----------------------------
def initialize_database():

    with conn.cursor() as cursor:

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT FALSE
            )
        """)

        conn.commit()

        # Seed example tasks only if table is empty
        cursor.execute("SELECT COUNT(*) AS count FROM tasks")

        count = cursor.fetchone()["count"]

        if count == 0:

            cursor.executemany(
                """
                INSERT INTO tasks (title, done)
                VALUES (%s, %s)
                """,
                [
                    ("Learn FastAPI", False),
                    ("Build CRUD API", False),
                    ("Push to GitHub", False)
                ]
            )

            conn.commit()


initialize_database()


# -----------------------------
# Convert FastAPI's default 422
# into assignment-required 400
# -----------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
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

    with conn.cursor() as cursor:

        cursor.execute("""
            SELECT id, title, done
            FROM tasks
            ORDER BY id
        """)

        return cursor.fetchall()


# -----------------------------
# Get Task By ID
# -----------------------------
@app.get("/tasks/{task_id}", summary="Get Task By ID")
def get_task(task_id: int):

    with conn.cursor() as cursor:

        cursor.execute(
            """
            SELECT id, title, done
            FROM tasks
            WHERE id = %s
            """,
            (task_id,)
        )

        task = cursor.fetchone()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    return task


# -----------------------------
# Create Task
# -----------------------------
@app.post(
    "/tasks",
    status_code=201,
    summary="Create Task"
)
def create_task(task: TaskCreate):

    with conn.cursor() as cursor:

        cursor.execute(
            """
            INSERT INTO tasks (title, done)
            VALUES (%s, %s)
            RETURNING id, title, done
            """,
            (task.title, False)
        )

        new_task = cursor.fetchone()

        conn.commit()

    return new_task


# -----------------------------
# Update Task
# -----------------------------
@app.put("/tasks/{task_id}", summary="Update Task")
def update_task(
    task_id: int,
    updated_task: TaskUpdate
):

    with conn.cursor() as cursor:

        cursor.execute(
            """
            UPDATE tasks
            SET title = %s,
                done = %s
            WHERE id = %s
            RETURNING id, title, done
            """,
            (
                updated_task.title,
                updated_task.done,
                task_id
            )
        )

        updated = cursor.fetchone()

        conn.commit()

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    return updated


# -----------------------------
# Delete Task
# -----------------------------
@app.delete(
    "/tasks/{task_id}",
    status_code=204,
    summary="Delete Task"
)
def delete_task(task_id: int):

    with conn.cursor() as cursor:

        cursor.execute(
            """
            DELETE FROM tasks
            WHERE id = %s
            RETURNING id
            """,
            (task_id,)
        )

        deleted = cursor.fetchone()

        conn.commit()

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    return