"""
Tests for the Mergington High School Activities API.

Uses the AAA (Arrange-Act-Assert) testing pattern for clarity and consistency.
"""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Fixture providing the test client for API calls."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Fixture to reset activities before each test for isolation.
    
    This ensures each test starts with a clean state to avoid
    test interdependencies.
    """
    original_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all available activities with proper structure."""
        # Arrange
        expected_activity_names = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Soccer Club",
            "Art Club",
            "Drama Club",
            "Debate Club",
            "Science Club"
        ]
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        for activity_name in expected_activity_names:
            assert activity_name in data, f"Activity '{activity_name}' not found"
            assert "description" in data[activity_name]
            assert "schedule" in data[activity_name]
            assert "participants" in data[activity_name]
            assert "max_participants" in data[activity_name]
    
    def test_get_activities_participants_are_lists(self, client, reset_activities):
        """Test that participants are returned as lists."""
        # Arrange
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["participants"], list), \
                f"Participants for {activity_name} should be a list"


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_successful(self, client, reset_activities):
        """Test successfully signing up a new participant for an activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in activities[activity_name]["participants"]
    
    def test_signup_activity_not_found(self, client, reset_activities):
        """Test that signing up for a non-existent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_duplicate_registration_prevents_double_signup(self, client, reset_activities):
        """Test that duplicate registrations are rejected with appropriate error."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered in initial data
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
    
    def test_signup_increases_participant_count(self, client, reset_activities):
        """Test that completing a signup increases the participant count by 1."""
        # Arrange
        activity_name = "Programming Class"
        email = "newprogrammer@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        assert len(activities[activity_name]["participants"]) == initial_count + 1
    
    def test_signup_response_contains_confirmation_message(self, client, reset_activities):
        """Test that signup response contains clear confirmation message."""
        # Arrange
        activity_name = "Art Club"
        email = "artist@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        data = response.json()
        
        # Assert
        assert "message" in data
        assert activity_name in data["message"]
        assert email in data["message"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_successful(self, client, reset_activities):
        """Test successfully unregistering an existing participant from an activity."""
        # Arrange
        activity_name = "Drama Club"
        email = "mason@mergington.edu"  # Already registered in initial data
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert email not in activities[activity_name]["participants"]
    
    def test_unregister_activity_not_found(self, client, reset_activities):
        """Test that unregistering from non-existent activity returns 404."""
        # Arrange
        activity_name = "Fake Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_student_not_registered(self, client, reset_activities):
        """Test that unregistering a non-registered student returns 404."""
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"  # Never registered
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert "not registered" in response.json()["detail"].lower()
    
    def test_unregister_decreases_participant_count(self, client, reset_activities):
        """Test that completing an unregister decreases the participant count by 1."""
        # Arrange
        activity_name = "Soccer Club"
        email = "liam@mergington.edu"  # Already registered in initial data
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        client.delete(f"/activities/{activity_name}/unregister?email={email}")
        
        # Assert
        assert len(activities[activity_name]["participants"]) == initial_count - 1
    
    def test_unregister_response_contains_confirmation_message(self, client, reset_activities):
        """Test that unregister response contains clear confirmation message."""
        # Arrange
        activity_name = "Science Club"
        email = "harper@mergington.edu"  # Already registered in initial data
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        data = response.json()
        
        # Assert
        assert "message" in data
        assert activity_name in data["message"]
        assert email in data["message"]


class TestIntegrationScenarios:
    """Integration tests for real-world usage scenarios."""
    
    def test_signup_then_unregister_flow(self, client, reset_activities):
        """Test the complete flow of signing up and then unregistering."""
        # Arrange
        activity_name = "Basketball Team"
        email = "player@mergington.edu"
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert signup was successful
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"]
        
        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert unregister was successful
        assert unregister_response.status_code == 200
        assert email not in activities[activity_name]["participants"]
    
    def test_multiple_signups_for_same_activity(self, client, reset_activities):
        """Test multiple different students can sign up for the same activity."""
        # Arrange
        activity_name = "Debate Club"
        emails = [
            "debater1@mergington.edu",
            "debater2@mergington.edu",
            "debater3@mergington.edu"
        ]
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Assert
        for email in emails:
            assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 3
