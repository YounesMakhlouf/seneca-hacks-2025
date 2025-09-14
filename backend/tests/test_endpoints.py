"""Integration tests for FastAPI endpoints."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from body_behavior_recommender.app import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_user_doc():
    """Mock user document from database."""
    return {
        "user_id": "test_user_1",
        "age": 30,
        "weight": 70.0,
        "height": 175.0,
        "bmi": 22.9,
        "fitness_level": "intermediate",
        "goals": "weight_loss",
        "join_date": "2024-01-01",
        "pref_music_genres": {"pop": 0.8, "rock": 0.6},
        "pref_meal_cuisines": {"italian": 0.9, "asian": 0.7},
        "pref_workout_focus": {"strength": 0.8, "cardio": 0.6},
        "allergens": ["nuts"],
        "diet_flags": ["vegetarian"],
        "equipment": ["dumbbells"],
    }


@pytest.fixture
def mock_sleep_docs():
    """Mock sleep documents from database."""
    return [
        {
            "user_id": "test_user_1",
            "date": "2024-01-15",
            "sleep_duration_minutes": 480,
            "deep_sleep_minutes": 120,
            "rem_sleep_minutes": 90,
            "light_sleep_minutes": 270,
            "sleep_efficiency": 85.0,
            "bedtime": "22:30",
            "wake_time": "06:30",
        }
    ]


@pytest.fixture
def mock_nutrition_docs():
    """Mock nutrition documents from database."""
    return [
        {
            "user_id": "test_user_1",
            "date": "2024-01-15",
            "calories_consumed": 2000,
            "protein_g": 120.0,
            "carbs_g": 250.0,
            "fat_g": 80.0,
            "fiber_g": 25.0,
            "sugar_g": 50.0,
            "sodium_mg": 2000.0,
        }
    ]


@pytest.fixture
def mock_activity_docs():
    """Mock activity documents from database."""
    return [
        {
            "user_id": "test_user_1",
            "date": "2024-01-15",
            "steps": 8000,
            "calories_burned": 300,
            "active_minutes": 45,
            "distance_km": 6.0,
            "heart_rate_avg": 140,
            "workout_duration": 30,
        }
    ]


class TestBasicEndpoints:
    """Test basic API endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns API information."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "description" in data
        assert "Body-to-Behavior Recommender" in data["name"]

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestStateEndpoint:
    """Test user state endpoint."""

    @patch("body_behavior_recommender.endpoints.db_get_user")
    @patch("body_behavior_recommender.endpoints.get_recent_entries")
    def test_get_state_success(
        self,
        mock_get_entries,
        mock_get_user,
        client,
        mock_user_doc,
        mock_sleep_docs,
        mock_nutrition_docs,
        mock_activity_docs,
    ):
        """Test successful state retrieval."""
        mock_get_user.return_value = mock_user_doc
        mock_get_entries.side_effect = [
            mock_sleep_docs,  # sleep entries
            mock_nutrition_docs,  # nutrition entries
            mock_activity_docs,  # activity entries
        ]

        response = client.get("/state?user_id=test_user_1")

        assert response.status_code == 200
        data = response.json()
        assert "Readiness" in data
        assert "Fuel" in data
        assert "Strain" in data
        assert all(0 <= data[key] <= 100 for key in ["Readiness", "Fuel", "Strain"])

    @patch("body_behavior_recommender.endpoints.db_get_user")
    def test_get_state_user_not_found(self, mock_get_user, client):
        """Test state endpoint with non-existent user."""
        mock_get_user.return_value = None

        response = client.get("/state?user_id=nonexistent")

        assert response.status_code == 404
        assert "user not found" in response.json()["detail"]


class TestRecommendEndpoint:
    """Test recommendation endpoint."""

    @patch("body_behavior_recommender.endpoints.db_get_user")
    @patch("body_behavior_recommender.endpoints.get_recent_entries")
    @patch("body_behavior_recommender.endpoints.thompson_sample_contextual")
    @patch("body_behavior_recommender.endpoints.filter_music_candidates")
    @patch("body_behavior_recommender.endpoints.rank_music")
    def test_recommend_music_success(
        self,
        mock_rank,
        mock_filter,
        mock_thompson,
        mock_get_entries,
        mock_get_user,
        client,
        mock_user_doc,
        mock_sleep_docs,
        mock_nutrition_docs,
        mock_activity_docs,
        sample_music_track,
    ):
        """Test successful music recommendation."""
        mock_get_user.return_value = mock_user_doc
        mock_get_entries.side_effect = [
            mock_sleep_docs,
            mock_nutrition_docs,
            mock_activity_docs,
        ]
        mock_thompson.return_value = "high_energy"
        mock_filter.return_value = [sample_music_track]
        mock_rank.return_value = [(sample_music_track, 0.85)]

        request_data = {"user_id": "test_user_1", "intent": "music"}

        response = client.post("/recommend", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["domain"] == "music"
        assert "state" in data
        assert "item" in data
        assert "bandit_arm" in data
        assert data["bandit_arm"] == "high_energy"
        assert data["item"]["id"] == sample_music_track.id

    @patch("body_behavior_recommender.endpoints.db_get_user")
    @patch("body_behavior_recommender.endpoints.get_recent_entries")
    @patch("body_behavior_recommender.endpoints.thompson_sample_contextual")
    @patch("body_behavior_recommender.endpoints.filter_meal_candidates")
    @patch("body_behavior_recommender.endpoints.rank_meals")
    def test_recommend_meal_success(
        self,
        mock_rank,
        mock_filter,
        mock_thompson,
        mock_get_entries,
        mock_get_user,
        client,
        mock_user_doc,
        mock_sleep_docs,
        mock_nutrition_docs,
        mock_activity_docs,
        sample_meal_template,
    ):
        """Test successful meal recommendation."""
        mock_get_user.return_value = mock_user_doc
        mock_get_entries.side_effect = [
            mock_sleep_docs,
            mock_nutrition_docs,
            mock_activity_docs,
        ]
        mock_thompson.return_value = "high_protein"
        mock_filter.return_value = [sample_meal_template]
        mock_rank.return_value = [(sample_meal_template, 0.90)]

        request_data = {"user_id": "test_user_1", "intent": "meal"}

        response = client.post("/recommend", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["domain"] == "meal"
        assert data["item"]["id"] == sample_meal_template.id

    @patch("body_behavior_recommender.endpoints.db_get_user")
    @patch("body_behavior_recommender.endpoints.get_recent_entries")
    @patch("body_behavior_recommender.endpoints.thompson_sample_contextual")
    @patch("body_behavior_recommender.endpoints.filter_workout_candidates")
    @patch("body_behavior_recommender.endpoints.rank_workouts")
    def test_recommend_workout_success(
        self,
        mock_rank,
        mock_filter,
        mock_thompson,
        mock_get_entries,
        mock_get_user,
        client,
        mock_user_doc,
        mock_sleep_docs,
        mock_nutrition_docs,
        mock_activity_docs,
        sample_workout_template,
    ):
        """Test successful workout recommendation."""
        mock_get_user.return_value = mock_user_doc
        mock_get_entries.side_effect = [
            mock_sleep_docs,
            mock_nutrition_docs,
            mock_activity_docs,
        ]
        mock_thompson.return_value = "strength_focus"
        mock_filter.return_value = [sample_workout_template]
        mock_rank.return_value = [(sample_workout_template, 0.88)]

        request_data = {"user_id": "test_user_1", "intent": "workout"}

        response = client.post("/recommend", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["domain"] == "workout"
        assert data["item"]["id"] == sample_workout_template.id

    @patch("body_behavior_recommender.endpoints.db_get_user")
    def test_recommend_user_not_found(self, mock_get_user, client):
        """Test recommendation with non-existent user."""
        mock_get_user.return_value = None

        request_data = {"user_id": "nonexistent", "intent": "music"}

        response = client.post("/recommend", json=request_data)

        assert response.status_code == 404
        assert "user not found" in response.json()["detail"]

    @patch("body_behavior_recommender.endpoints.db_get_user")
    @patch("body_behavior_recommender.endpoints.get_recent_entries")
    @patch("body_behavior_recommender.endpoints.thompson_sample_contextual")
    @patch("body_behavior_recommender.endpoints.filter_music_candidates")
    @patch("body_behavior_recommender.endpoints.rank_music")
    def test_recommend_no_candidates(
        self,
        mock_rank,
        mock_filter,
        mock_thompson,
        mock_get_entries,
        mock_get_user,
        client,
        mock_user_doc,
        mock_sleep_docs,
        mock_nutrition_docs,
        mock_activity_docs,
    ):
        """Test recommendation when no candidates are available."""
        mock_get_user.return_value = mock_user_doc
        mock_get_entries.side_effect = [
            mock_sleep_docs,
            mock_nutrition_docs,
            mock_activity_docs,
        ]
        mock_thompson.return_value = "high_energy"
        mock_filter.return_value = []
        mock_rank.return_value = []

        request_data = {"user_id": "test_user_1", "intent": "music"}

        response = client.post("/recommend", json=request_data)

        assert response.status_code == 400
        assert "no music candidates" in response.json()["detail"]

    @patch("body_behavior_recommender.endpoints.db_get_user")
    @patch("body_behavior_recommender.endpoints.get_recent_entries")
    @patch("body_behavior_recommender.endpoints.choose_domain")
    def test_recommend_auto_domain_selection(
        self,
        mock_choose,
        mock_get_entries,
        mock_get_user,
        client,
        mock_user_doc,
        mock_sleep_docs,
        mock_nutrition_docs,
        mock_activity_docs,
    ):
        """Test automatic domain selection when intent is None."""
        mock_get_user.return_value = mock_user_doc
        mock_get_entries.side_effect = [
            mock_sleep_docs,
            mock_nutrition_docs,
            mock_activity_docs,
        ]
        mock_choose.return_value = "meal"

        request_data = {
            "user_id": "test_user_1"
            # No intent specified
        }

        with (
            patch("body_behavior_recommender.endpoints.thompson_sample_contextual"),
            patch("body_behavior_recommender.endpoints.filter_meal_candidates"),
            patch(
                "body_behavior_recommender.endpoints.rank_meals",
                return_value=[(MagicMock(), 0.8)],
            ),
        ):
            response = client.post("/recommend", json=request_data)

            # Should call choose_domain to determine the domain
            mock_choose.assert_called_once()


class TestFeedbackEndpoint:
    """Test feedback submission endpoint."""

    @patch("body_behavior_recommender.endpoints.db_get_user")
    @patch("body_behavior_recommender.endpoints.get_recent_entries")
    @patch("body_behavior_recommender.endpoints.thompson_sample_contextual")
    @patch("body_behavior_recommender.endpoints.reward_from_feedback")
    @patch("body_behavior_recommender.endpoints.update_bandit")
    @patch("body_behavior_recommender.endpoints.update_preferences")
    def test_submit_feedback_success(
        self,
        mock_update_pref,
        mock_update_bandit,
        mock_reward,
        mock_thompson,
        mock_get_entries,
        mock_get_user,
        client,
        mock_user_doc,
        mock_sleep_docs,
        mock_nutrition_docs,
        mock_activity_docs,
    ):
        """Test successful feedback submission."""
        mock_get_user.return_value = mock_user_doc
        mock_get_entries.side_effect = [
            mock_sleep_docs,
            mock_nutrition_docs,
            mock_activity_docs,
        ]
        mock_thompson.return_value = "high_energy"
        mock_reward.return_value = 0.8

        feedback_data = {
            "user_id": "test_user_1",
            "domain": "music",
            "item_id": "track_1",
            "thumbs": 1,
            "completed": 1,
            "hr_zone_frac": 0.7,
            "skipped_early": 0,
        }

        response = client.post("/feedback", json=feedback_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "feedback recorded"

        # Verify the reward calculation and bandit update were called
        mock_reward.assert_called_once()
        mock_update_bandit.assert_called_once()
        mock_update_pref.assert_called_once()

    @patch("body_behavior_recommender.endpoints.db_get_user")
    def test_submit_feedback_user_not_found(self, mock_get_user, client):
        """Test feedback submission with non-existent user."""
        mock_get_user.return_value = None

        feedback_data = {
            "user_id": "nonexistent",
            "domain": "music",
            "item_id": "track_1",
            "thumbs": 1,
        }

        response = client.post("/feedback", json=feedback_data)

        assert response.status_code == 404
        assert "user not found" in response.json()["detail"]


class TestCatalogEndpoints:
    """Test catalog endpoints."""

    @patch("body_behavior_recommender.endpoints.MUSIC")
    def test_get_music_catalog(self, mock_music, client, sample_music_track):
        """Test music catalog endpoint."""
        mock_music.__len__.return_value = 1
        mock_music.__getitem__.return_value = [sample_music_track]

        response = client.get("/catalog/music")

        assert response.status_code == 200
        data = response.json()
        assert "count" in data

    @patch("body_behavior_recommender.endpoints.MEALS")
    def test_get_meals_catalog(self, mock_meals, client, sample_meal_template):
        """Test meals catalog endpoint."""
        mock_meals.__len__.return_value = 1
        mock_meals.__getitem__.return_value = [sample_meal_template]

        response = client.get("/catalog/meals")

        assert response.status_code == 200
        data = response.json()
        assert "count" in data

    @patch("body_behavior_recommender.endpoints.WORKOUTS")
    def test_get_workouts_catalog(self, mock_workouts, client, sample_workout_template):
        """Test workouts catalog endpoint."""
        mock_workouts.__len__.return_value = 1
        mock_workouts.__getitem__.return_value = [sample_workout_template]

        response = client.get("/catalog/workouts")

        assert response.status_code == 200
        data = response.json()
        assert "count" in data


class TestUserEndpoints:
    """Test user information endpoints."""

    @patch("body_behavior_recommender.endpoints.db_get_user")
    def test_get_user_success(self, mock_get_user, client, mock_user_doc):
        """Test successful user retrieval."""
        mock_get_user.return_value = mock_user_doc

        response = client.get("/users/test_user_1")

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test_user_1"
        assert data["age"] == 30

    @patch("body_behavior_recommender.endpoints.db_get_user")
    def test_get_user_not_found(self, mock_get_user, client):
        """Test user retrieval with non-existent user."""
        mock_get_user.return_value = None

        response = client.get("/users/nonexistent")

        assert response.status_code == 404
        assert "user not found" in response.json()["detail"]


class TestValidationErrors:
    """Test request validation errors."""

    def test_recommend_invalid_request_body(self, client):
        """Test recommendation with invalid request body."""
        invalid_data = {
            "user_id": "",  # Empty user_id should be invalid
            "intent": "invalid_intent",  # Invalid intent
        }

        response = client.post("/recommend", json=invalid_data)

        # Should return validation error
        assert response.status_code == 422

    def test_feedback_invalid_request_body(self, client):
        """Test feedback with invalid request body."""
        invalid_data = {
            "user_id": "",  # Empty user_id
            "domain": "invalid_domain",  # Invalid domain
            "item_id": "",  # Empty item_id
            "thumbs": 5,  # Invalid thumbs value (should be -1, 0, or 1)
        }

        response = client.post("/feedback", json=invalid_data)

        # Should return validation error
        assert response.status_code == 422

    def test_missing_required_fields(self, client):
        """Test requests with missing required fields."""
        # Recommend without user_id
        response = client.post("/recommend", json={})
        assert response.status_code == 422

        # Feedback without required fields
        response = client.post("/feedback", json={"user_id": "test"})
        assert response.status_code == 422
