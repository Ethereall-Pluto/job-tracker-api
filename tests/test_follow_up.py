from datetime import date

from tracker.follow_up import due_follow_ups
from tracker.models import Application, Status


def make(app_id: int, applied_on: date, status: Status = Status.APPLIED) -> Application:
    return Application(
        id=app_id, company="Acme", position="Engineer", source="Djinni", applied_on=applied_on, status=status
    )


def test_exactly_seven_days_is_due():
    apps = [make(1, date(2026, 10, 20))]
    assert due_follow_ups(apps, today=date(2026, 10, 27)) == apps


def test_six_days_is_not_due_yet():
    apps = [make(1, date(2026, 10, 21))]
    assert due_follow_ups(apps, today=date(2026, 10, 27)) == []


def test_answered_applications_are_skipped():
    apps = [
        make(1, date(2026, 10, 1), Status.INTERVIEW),
        make(2, date(2026, 10, 1), Status.REJECTED),
    ]
    assert due_follow_ups(apps, today=date(2026, 10, 27)) == []
