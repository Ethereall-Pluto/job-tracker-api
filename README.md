# Job Application Tracker API

[![CI](https://github.com/Ethereall-Pluto/job-tracker-api/actions/workflows/ci.yml/badge.svg)](https://github.com/Ethereall-Pluto/job-tracker-api/actions/workflows/ci.yml)

A small REST API for tracking job applications: log where you applied, update the status
as recruiters answer, and get a list of applications that need a follow-up
(no reply after 7 days).

I built it to replace the spreadsheet I use for my own job search.

**Stack:** Python, FastAPI, Pydantic, SQLite, pytest, Docker, GitHub Actions.

## Structure

| Module | Responsibility |
|---|---|
| `models.py` | Data shapes and validation (Pydantic). An empty company name or an unknown status is rejected with `422` before any code runs. |
| `repository.py` | `ApplicationRepository` — the only place that talks to SQLite. Raises `ApplicationNotFound` for missing IDs. |
| `follow_up.py` | The follow-up rule as a pure function: no database, no clock, so it's tested with plain data. |
| `api.py` | HTTP routes. Turns `ApplicationNotFound` into `404`, otherwise just connects requests to the repository. |

Design decisions:

- **Layers don't leak.** Routes don't know SQL, the repository doesn't know HTTP, the follow-up rule knows neither. Swapping SQLite for PostgreSQL only touches `repository.py`.
- **App factory (`create_app(db_path)`).** Tests get a fresh temporary database each; production uses `tracker.db`.
- **Parameterized SQL (`?` placeholders)** everywhere — no string formatting, so no SQL injection.
- **`today` is a parameter**, not a hidden `date.today()` call inside the logic, which makes date-dependent behavior testable.

## Run

With Docker:

```bash
docker build -t job-tracker-api .
docker run -p 8000:8000 -v tracker-data:/data job-tracker-api
```

The `tracker-data` volume keeps the database when the container is removed or rebuilt.

Without Docker:

```bash
pip install -r requirements.txt
uvicorn tracker.main:app --reload
```

Interactive docs: http://localhost:8000/docs. The database file defaults to `tracker.db`; set `TRACKER_DB` to put it elsewhere.

## Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/applications` | Log a new application (starts as `applied`) |
| `GET` | `/applications?status=interview` | List applications, optional status filter |
| `GET` | `/applications/{id}` | Get one application |
| `PATCH` | `/applications/{id}/status` | Change status: `applied`, `interview`, `offer`, `rejected` |
| `GET` | `/follow-ups?today=2026-10-27` | Unanswered applications older than 7 days (`today` defaults to the current date) |

Example:

```bash
curl -X POST localhost:8000/applications \
  -H "content-type: application/json" \
  -d '{"company": "Acme", "position": "CAD Specialist", "source": "Djinni", "applied_on": "2026-10-20"}'
```

```json
{"company": "Acme", "position": "CAD Specialist", "source": "Djinni", "applied_on": "2026-10-20", "id": 1, "status": "applied"}
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

GitHub Actions runs the tests on Python 3.10 and 3.12 on every push, then builds the Docker image, starts it and checks that the API answers.

Requires Python 3.10+.
