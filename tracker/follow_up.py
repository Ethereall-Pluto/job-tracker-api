from datetime import date, timedelta

from tracker.models import Application, Status

FOLLOW_UP_AFTER = timedelta(days=7)


def due_follow_ups(applications: list[Application], today: date) -> list[Application]:
    """Applications with no reply a week after sending — time to write to the recruiter.

    Pure function: no database, no clock. The caller passes `today`, which keeps it trivial to test.
    """
    return [
        app
        for app in applications
        if app.status is Status.APPLIED and app.applied_on + FOLLOW_UP_AFTER <= today
    ]
