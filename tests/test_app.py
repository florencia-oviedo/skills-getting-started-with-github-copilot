from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


def test_unregister_existing_participant():
    original_participants = list(activities["Chess Club"]["participants"])

    try:
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Unregistered michael@mergington.edu from Chess Club"
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    finally:
        activities["Chess Club"]["participants"] = original_participants


def test_unregister_nonexistent_participant_returns_404():
    original_participants = list(activities["Chess Club"]["participants"])

    try:
        response = client.delete(
            "/activities/Chess Club/unregister?email=notfound@mergington.edu"
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"
        assert activities["Chess Club"]["participants"] == original_participants
    finally:
        activities["Chess Club"]["participants"] = original_participants
