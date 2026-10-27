# Job Application Tracker API

A small REST API for tracking job applications: log where you applied, update the status
as recruiters answer, and get a list of applications that need a follow-up
(no reply after 7 days).

I built it to replace the spreadsheet I use for my own job search.

**Stack:** Python, FastAPI, Pydantic, SQLite, pytest.

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

```bash
pip install fastapi uvicorn
uvicorn tracker.main:app --reload
```

Interactive docs: http://localhost:8000/docs

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
pip install pytest httpx
pytest
```

Requires Python 3.10+.
