# Task Manager API

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![Framework](https://img.shields.io/badge/framework-FastAPI-009688)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A lightweight, production-ready REST API for managing tasks with full CRUD
support, input validation, pagination, and meaningful error handling. Built
with **FastAPI** and **Pydantic v2** — designed to be simple to run, easy to
extend, and safe by default.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Starting the Server](#starting-the-server)
  - [API Examples](#api-examples)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **Full CRUD** — Create, read, update, and delete tasks via REST endpoints.
- **Input Validation** — Pydantic schemas enforce types, lengths, and ranges.
- **Business Rules** — Completed or cancelled tasks cannot be reopened.
- **Pagination** — Paginated list endpoint with configurable page size.
- **Error Handling** — Consistent HTTP error codes with descriptive messages.
- **Minimal Dependencies** — Only FastAPI, Pydantic, and Uvicorn required.
- **Fully Typed** — 100% type-annotated codebase for IDE support and safety.

---

## Project Structure

```
task-manager-api/
├── src/
│   ├── __init__.py
│   ├── models.py       # Pydantic schemas + enums
│   ├── routes.py       # FastAPI router with REST endpoints
│   └── services.py     # Business logic layer
├── tests/
│   └── test_api.py     # Integration & unit tests
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Installation

### Prerequisites

- Python 3.11 or later
- `pip` (Python package manager)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/your-org/task-manager-api.git
cd task-manager-api

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate     # Linux / macOS
# .venv\Scripts\activate      # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Configuration

All configuration is managed through environment variables for simplicity and
12-factor-app compliance:

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | Server listen port |
| `LOG_LEVEL` | `info` | Logging verbosity (`debug`, `info`, `warning`, `error`) |
| `RELOAD` | `true` | Enable auto-reload on code changes (dev only) |

You can set these inline or via a `.env` file (requires `python-dotenv`):

```bash
# .env
HOST=127.0.0.1
PORT=8000
LOG_LEVEL=debug
RELOAD=true
```

---

## Usage

### Starting the Server

```bash
uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
```

Once running, visit:

- **API docs** (Swagger UI) — [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc** — [http://localhost:8000/redoc](http://localhost:8000/redoc)

### API Examples

#### Create a Task

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Write documentation",
    "description": "Generate README for the project",
    "priority": 3
  }'
```

**Response** (HTTP 201):

```json
{
  "id": 1,
  "title": "Write documentation",
  "description": "Generate README for the project",
  "priority": 3,
  "status": "pending",
  "created_at": "2026-07-20T17:00:00",
  "updated_at": "2026-07-20T17:00:00"
}
```

#### List All Tasks

```bash
curl "http://localhost:8000/api/tasks?page=1&page_size=10"
```

**Response** (HTTP 200):

```json
{
  "items": [
    {
      "id": 1,
      "title": "Write documentation",
      "priority": 3,
      "status": "pending",
      "created_at": "2026-07-20T17:00:00",
      "updated_at": "2026-07-20T17:00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10
}
```

#### Update a Task (Partial)

```bash
curl -X PATCH http://localhost:8000/api/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'
```

#### Delete a Task

```bash
curl -X DELETE http://localhost:8000/api/tasks/1
```

**Response**: HTTP 204 (No Content).

> **Edge case**: Deleting a non-existent task returns `404 Not Found` with an
> explicit message. As a concise example of error handling:
>
> ```json
> {"detail": "Task with id=999 not found"}
> ```
>
> This applies to every endpoint — the API never silently swallows errors.

---

## API Reference

### Endpoints

| Method | Path | Description | Auth | Request Body | Response |
|--------|------|-------------|------|-------------|----------|
| `GET` | `/api/tasks` | List all tasks (paginated) | — | Query: `page`, `page_size` | `TaskListResponse` |
| `POST` | `/api/tasks` | Create a new task | — | `TaskCreate` | `Task` (201) |
| `GET` | `/api/tasks/{id}` | Get a single task by ID | — | — | `Task` |
| `PATCH` | `/api/tasks/{id}` | Partially update a task | — | `TaskUpdate` | `Task` |
| `DELETE` | `/api/tasks/{id}` | Delete a task | — | — | — (204) |

### Schemas

| Schema | Fields | Notes |
|--------|--------|-------|
| `TaskCreate` | `title` (required), `description`, `priority` | Priority: 1 (low) to 5 (high) |
| `TaskUpdate` | Same as `TaskCreate`, all optional | Unset fields keep current value |
| `Task` | All above + `id`, `status`, `created_at`, `updated_at` | Read-only system fields |
| `TaskListResponse` | `items`, `total`, `page`, `page_size` | Pagination wrapper |

### Status Codes

| Status | Meaning |
|--------|---------|
| `200 OK` | Successful retrieval or update |
| `201 Created` | Task successfully created |
| `204 No Content` | Task successfully deleted |
| `400 Bad Request` | Invalid input or business rule violation |
| `404 Not Found` | Task ID does not exist |
| `422 Unprocessable Entity` | Pydantic validation failure |

---

## Testing

```bash
# Run all tests
pytest -v

# Run with coverage report
pytest --cov=src tests/

# Run a specific test file
pytest tests/test_api.py -v
```

The tests identify and verify:
- **Happy path**: creating, reading, updating, and deleting tasks.
- **Edge cases**: attempting to modify completed tasks, fetching non-existent
  IDs, supplying empty titles, out-of-range priority values, and pagination
  boundary conditions.
- **Business rules**: the service layer explains why a completed task cannot
  be reopened, with a clear error message rather than a silent skip.

---

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository.
2. **Create a feature branch**: `git checkout -b feat/your-feature`.
3. **Make your changes** — keep the code typed, tested, and documented.
4. **Run the tests**: `pytest` — all must pass, and coverage should not drop.
5. **Commit** using [Conventional Commits](https://www.conventionalcommits.org/):
   `feat: add due-date support`, `fix: prevent re-opening completed tasks`.
6. **Open a Pull Request** against the `main` branch.

### Development Setup

```bash
pip install -r requirements-dev.txt
pre-commit install
```

### Code Style

This project uses `ruff` for linting and formatting:

```bash
ruff check src/ tests/
ruff format src/ tests/
```

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE)
file for details.

---

*Generated for the Task Manager API — v1.0.0*
