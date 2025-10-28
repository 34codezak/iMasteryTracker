from __future__ import annotations

from starlette.testclient import TestClient

from imasterytracker.app import app

client = TestClient(app._api)


def test_stream_crud_cycle():
    create_response = client.post(
        "/api/streams",
        json={
            "name": "Systems Design",
            "focus": "Explore bounded contexts",
            "milestones_total": 4,
            "milestones_completed": 1,
        },
    )
    assert create_response.status_code == 201
    body = create_response.json()
    assert body["name"] == "Systems Design"

    list_response = client.get("/api/streams")
    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data) == 1

    delete_response = client.delete(f"/api/streams/{body['id']}")
    assert delete_response.status_code == 204

    assert client.get("/api/streams").json() == []


def test_import_validation_error():
    response = client.post(
        "/api/import",
        json={"streams": [{"name": "", "milestones_total": 0}]},
    )
    assert response.status_code == 400
    assert "Name" in response.json()["detail"]
