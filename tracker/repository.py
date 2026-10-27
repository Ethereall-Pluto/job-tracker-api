import sqlite3
from contextlib import closing
from datetime import date
from pathlib import Path

from tracker.models import Application, ApplicationCreate, Status

SCHEMA = """
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    position TEXT NOT NULL,
    source TEXT NOT NULL,
    applied_on TEXT NOT NULL,
    status TEXT NOT NULL
)
"""


class ApplicationNotFound(Exception):
    def __init__(self, application_id: int) -> None:
        super().__init__(f"application {application_id} not found")
        self.application_id = application_id


class ApplicationRepository:
    """Stores applications in SQLite. The only class that knows SQL exists."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        with self._connect() as conn:
            conn.execute(SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create(self, data: ApplicationCreate) -> Application:
        with closing(self._connect()) as conn, conn:
            cursor = conn.execute(
                "INSERT INTO applications (company, position, source, applied_on, status) "
                "VALUES (?, ?, ?, ?, ?)",
                (data.company, data.position, data.source, data.applied_on.isoformat(), Status.APPLIED.value),
            )
            return Application(id=cursor.lastrowid, status=Status.APPLIED, **data.model_dump())

    def get(self, application_id: int) -> Application:
        with closing(self._connect()) as conn:
            row = conn.execute("SELECT * FROM applications WHERE id = ?", (application_id,)).fetchone()
        if row is None:
            raise ApplicationNotFound(application_id)
        return _to_application(row)

    def list(self, status: Status | None = None) -> list[Application]:
        query = "SELECT * FROM applications"
        params: tuple = ()
        if status is not None:
            query += " WHERE status = ?"
            params = (status.value,)
        with closing(self._connect()) as conn:
            rows = conn.execute(query + " ORDER BY applied_on, id", params).fetchall()
        return [_to_application(row) for row in rows]

    def update_status(self, application_id: int, status: Status) -> Application:
        with closing(self._connect()) as conn, conn:
            cursor = conn.execute(
                "UPDATE applications SET status = ? WHERE id = ?", (status.value, application_id)
            )
        if cursor.rowcount == 0:
            raise ApplicationNotFound(application_id)
        return self.get(application_id)


def _to_application(row: sqlite3.Row) -> Application:
    return Application(
        id=row["id"],
        company=row["company"],
        position=row["position"],
        source=row["source"],
        applied_on=date.fromisoformat(row["applied_on"]),
        status=Status(row["status"]),
    )
