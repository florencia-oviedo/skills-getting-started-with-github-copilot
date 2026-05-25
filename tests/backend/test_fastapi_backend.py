import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activity_state():
    # Arrange
    original_participants = {
        activity_name: list(activity["participants"])
        for activity_name, activity in activities.items()
    }

    yield

    # Cleanup
    for activity_name, participants in original_participants.items():
        activities[activity_name]["participants"] = participants


def test_root_redirects_to_static_index():
    # Arrange
    # No special setup required

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities():
    # Arrange
    # No special setup required

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == activities


def test_signup_for_activity_success():
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/Chess Club/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_for_activity_rejects_duplicate_signup():
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/Chess Club/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_unknown_activity_returns_404():
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/Unknown Activity/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_existing_participant_success():
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/Chess Club/unregister?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from Chess Club"
    }
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_nonexistent_participant_returns_404():
    # Arrange
    email = "notfound@mergington.edu"

    # Act
    response = client.delete(f"/activities/Chess Club/unregister?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
