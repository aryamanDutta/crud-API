# Task API — PostgreSQL + Docker

A simple CRUD API built with **FastAPI** and **PostgreSQL**, with the database running in Docker.

The API routes remain unchanged from the previous version; only the storage layer was replaced.

## Tech Stack

- Python
- FastAPI
- PostgreSQL 16
- psycopg
- Docker & Docker Compose

## Architecture

```text
Client → FastAPI → PostgreSQL
                    ↓
              Docker Volume
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/tasks` | Get all tasks |
| GET | `/tasks/{id}` | Get task by ID |
| POST | `/tasks` | Create task |
| PUT | `/tasks/{id}` | Update task |
| DELETE | `/tasks/{id}` | Delete task |

## Configuration

Database connection is stored in `.env`:

```env
DATABASE_URL=postgresql://taskuser:taskpassword@db:5432/taskdb
```

`.env` is gitignored and `.env.example` is included for setup.

## Run the Project

Make sure Docker Desktop is running, then:

```bash
docker compose up --build
```

API:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

## Database

PostgreSQL automatically creates the `tasks` table and seeds the initial tasks when the table is empty.

The database uses a Docker volume:

```text
postgres_data
```

so data persists across container restarts.

## Persistence Test

A task was created through the API, then the stack was restarted:

```bash
docker compose down
docker compose up -d
```

The task was still present after restarting, confirming database persistence.

## Screenshots

### Swagger API

![Swagger UI](images/swagger-ui.png)

### PostgreSQL Database

![PostgreSQL Database](images/postgres-docker.png)

## Author

**Aryaman Dutta**