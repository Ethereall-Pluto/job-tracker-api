from datetime import date
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from tracker.follow_up import due_follow_ups
from tracker.models import Application, ApplicationCreate, Status, StatusUpdate
from tracker.repository import ApplicationNotFound, ApplicationRepository


def create_app(db_path: Path) -> FastAPI:
    """Build the app around one repository. Tests pass a temp database, production a real file."""
    app = FastAPI(title="Job Application Tracker")
    repo = ApplicationRepository(db_path)

    @app.exception_handler(ApplicationNotFound)
    def not_found(_: Request, exc: ApplicationNotFound) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.post("/applications", status_code=201)
    def create_application(data: ApplicationCreate) -> Application:
        return repo.create(data)

    @app.get("/applications")
    def list_applications(status: Status | None = None) -> list[Application]:
        return repo.list(status)

    @app.get("/applications/{application_id}")
    def get_application(application_id: int) -> Application:
        return repo.get(application_id)

    @app.patch("/applications/{application_id}/status")
    def update_status(application_id: int, update: StatusUpdate) -> Application:
        return repo.update_status(application_id, update.status)

    @app.get("/follow-ups")
    def follow_ups(today: date | None = None) -> list[Application]:
        return due_follow_ups(repo.list(Status.APPLIED), today or date.today())

    return app
