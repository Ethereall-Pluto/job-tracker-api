import pytest
from fastapi.testclient import TestClient

from tracker.api import create_app


@pytest.fixture
def client(tmp_path):
    return TestClient(create_app(tmp_path / "test.db"))


def add(client: TestClient, company: str, applied_on: str = "2026-10-20") -> dict:
    response = client.post(
        "/applications",
        json={"company": company, "position": "CAD Specialist", "source": "Djinni", "applied_on": applied_on},
    )
    assert response.status_code == 201
    return response.json()


def test_new_application_starts_as_applied(client):
    created = add(client, "Acme")
    assert created["status"] == "applied"
    assert client.get(f"/applications/{created['id']}").json() == created


def test_empty_company_is_rejected(client):
    response = client.post(
        "/applications",
        json={"company": "", "position": "X", "source": "Djinni", "applied_on": "2026-10-20"},
    )
    assert response.status_code == 422


def test_unknown_id_returns_404(client):
    assert client.get("/applications/999").status_code == 404
    assert client.patch("/applications/999/status", json={"status": "offer"}).status_code == 404


def test_invalid_status_is_rejected(client):
    created = add(client, "Acme")
    response = client.patch(f"/applications/{created['id']}/status", json={"status": "ghosted"})
    assert response.status_code == 422


def test_filter_by_status(client):
    first = add(client, "Acme")
    add(client, "Globex")
    client.patch(f"/applications/{first['id']}/status", json={"status": "interview"})

    interviews = client.get("/applications", params={"status": "interview"}).json()

    assert [a["company"] for a in interviews] == ["Acme"]
    assert len(client.get("/applications").json()) == 2


def test_follow_ups_lists_only_stale_unanswered(client):
    stale = add(client, "Acme", applied_on="2026-10-10")
    add(client, "Globex", applied_on="2026-10-25")
    answered = add(client, "Initech", applied_on="2026-10-10")
    client.patch(f"/applications/{answered['id']}/status", json={"status": "rejected"})

    due = client.get("/follow-ups", params={"today": "2026-10-27"}).json()

    assert [a["id"] for a in due] == [stale["id"]]
