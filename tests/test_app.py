import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src import app as application_module


client = TestClient(application_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Arrange: backup activities before each test and restore after."""
    original = copy.deepcopy(application_module.activities)
    yield
    application_module.activities.clear()
    application_module.activities.update(original)


def test_get_activities_returns_200_and_structure():
    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_adds_participant():
    activity = "Chess Club"
    email = "testuser@example.com"

    # Arrange
    before = len(application_module.activities[activity]["participants"])

    # Act
    resp = client.post(f"/activities/{quote(activity)}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert email in application_module.activities[activity]["participants"]
    assert len(application_module.activities[activity]["participants"]) == before + 1


def test_signup_duplicate_returns_400():
    activity = "Chess Club"
    email = application_module.activities[activity]["participants"][0]

    # Act
    resp = client.post(f"/activities/{quote(activity)}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 400


def test_unregister_removes_participant():
    activity = "Programming Class"
    email = "tempuser@example.com"

    # Arrange: ensure participant exists
    application_module.activities[activity]["participants"].append(email)
    before = len(application_module.activities[activity]["participants"])

    # Act
    resp = client.delete(f"/activities/{quote(activity)}/participants", params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert email not in application_module.activities[activity]["participants"]
    assert len(application_module.activities[activity]["participants"]) == before - 1


def test_unregister_nonexistent_returns_400():
    activity = "Programming Class"
    email = "nobody@example.com"

    # Arrange: ensure email is not present
    if email in application_module.activities[activity]["participants"]:
        application_module.activities[activity]["participants"].remove(email)

    # Act
    resp = client.delete(f"/activities/{quote(activity)}/participants", params={"email": email})

    # Assert
    assert resp.status_code == 400
