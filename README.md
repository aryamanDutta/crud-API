# Task API (SQLite Version)

A simple CRUD API built with FastAPI and SQLite.

## Features

- Create tasks
- Read all tasks
- Read a task by ID
- Update tasks
- Delete tasks
- SQLite database persistence

## Why SQLite?

SQLite was chosen because it is lightweight, requires zero server setup, stores all data in a single file, and keeps data even after the application restarts.

## Database

The database is stored in:

```
tasks.db
```

It is created automatically when the application starts if it does not already exist.

The `tasks` table is also created automatically, and three sample tasks are inserted only on the first run.

## Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the server:

```bash
uvicorn main:app --reload
```

Open:

```
http://127.0.0.1:8000/docs
```

## Example SQL Query

```sql
SELECT * FROM tasks;
```

This query lists every task stored in the SQLite database.

## Project Structure

```
TaskAPI/
│
├── main.py
├── requirements.txt
├── tasks.db
├── README.md
└── images/
```

## API Endpoints

- GET `/tasks`
- GET `/tasks/{id}`
- POST `/tasks`
- PUT `/tasks/{id}`
- DELETE `/tasks/{id}`