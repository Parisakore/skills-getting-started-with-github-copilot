import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

# Original activities data for resetting between tests
ORIGINAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Competitive basketball team for all skill levels",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["alex@mergington.edu"]
    },
    "Tennis Club": {
        "description": "Learn tennis techniques and participate in friendly matches",
        "schedule": "Saturdays, 9:00 AM - 11:00 AM",
        "max_participants": 12,
        "participants": ["lucas@mergington.edu", "aria@mergington.edu"]
    },
    "Art Studio": {
        "description": "Explore painting, drawing, and sculpture techniques",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["isabella@mergington.edu"]
    },
    "Music Ensemble": {
        "description": "Join our band or orchestra and perform at school events",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 25,
        "participants": ["noah@mergington.edu", "ava@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop argumentation skills and compete in debate competitions",
        "schedule": "Mondays and Fridays, 3:30 PM - 4:30 PM",
        "max_participants": 16,
        "participants": ["mason@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments and explore STEM topics",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 22,
        "participants": ["grace@mergington.edu", "ethan@mergington.edu"]
    }
}

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities data before each test for isolation."""
    from src.app import activities
    activities.clear()
    activities.update(ORIGINAL_ACTIVITIES)

class TestRootEndpoint:
    def test_get_root_redirects_to_static_index(self):
        # Arrange: No special setup needed

        # Act: Make GET request to root endpoint
        response = client.get("/")

        # Assert: Should redirect to static index.html
        assert response.status_code == 200
        # Note: FastAPI TestClient follows redirects by default

class TestGetActivities:
    def test_get_activities_returns_all_activities(self):
        # Arrange: Activities are reset by fixture

        # Act: Make GET request to activities endpoint
        response = client.get("/activities")

        # Assert: Should return 200 and contain all activities
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9  # All activities present
        assert "Chess Club" in data
        assert "Programming Class" in data

        # Verify structure of one activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

class TestSignupForActivity:
    def test_signup_success_adds_participant(self):
        # Arrange: Prepare test data
        test_email = "newstudent@mergington.edu"
        activity_name = "Chess Club"

        # Act: Make POST request to signup endpoint
        response = client.post(f"/activities/{activity_name}/signup?email={test_email}")

        # Assert: Should return 200 with success message
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert f"Signed up {test_email} for {activity_name}" in data["message"]

        # Assert: Participant should be added to activity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert test_email in activities_data[activity_name]["participants"]

    def test_signup_duplicate_participant_fails(self):
        # Arrange: Sign up once first
        existing_email = "michael@mergington.edu"
        activity_name = "Chess Club"
        client.post(f"/activities/{activity_name}/signup?email={existing_email}")

        # Act: Try to sign up the same participant again
        response = client.post(f"/activities/{activity_name}/signup?email={existing_email}")

        # Assert: Should return 400 with error message
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Student is already signed up for this activity" in data["detail"]

    def test_signup_nonexistent_activity_fails(self):
        # Arrange: Use invalid activity name
        test_email = "test@mergington.edu"
        invalid_activity = "Nonexistent Activity"

        # Act: Try to sign up for non-existent activity
        response = client.post(f"/activities/{invalid_activity}/signup?email={test_email}")

        # Assert: Should return 404 with error message
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

class TestRemoveFromActivity:
    def test_remove_participant_success_removes_participant(self):
        # Arrange: Sign up a participant first
        test_email = "removeme@mergington.edu"
        activity_name = "Programming Class"
        client.post(f"/activities/{activity_name}/signup?email={test_email}")

        # Act: Make DELETE request to remove endpoint
        response = client.delete(f"/activities/{activity_name}/signup?email={test_email}")

        # Assert: Should return 200 with success message
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert f"Removed {test_email} from {activity_name}" in data["message"]

        # Assert: Participant should be removed from activity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert test_email not in activities_data[activity_name]["participants"]

    def test_remove_participant_not_signed_up_fails(self):
        # Arrange: Use email not signed up
        not_signed_email = "notsigned@mergington.edu"
        activity_name = "Gym Class"

        # Act: Try to remove participant who isn't signed up
        response = client.delete(f"/activities/{activity_name}/signup?email={not_signed_email}")

        # Assert: Should return 400 with error message
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Student is not signed up for this activity" in data["detail"]

    def test_remove_from_nonexistent_activity_fails(self):
        # Arrange: Use invalid activity name
        test_email = "test@mergington.edu"
        invalid_activity = "Nonexistent Activity"

        # Act: Try to remove from non-existent activity
        response = client.delete(f"/activities/{invalid_activity}/signup?email={test_email}")

        # Assert: Should return 404 with error message
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]