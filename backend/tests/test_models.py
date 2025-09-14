"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError
from body_behavior_recommender.models import (
    UserProfile, SleepEntry, NutritionEntry, ActivityEntry, MeasurementEntry,
    MusicTrack, MealTemplate, WorkoutTemplate, RecommendRequest, RecommendResponse, Feedback
)


class TestUserProfile:
    """Test UserProfile model validation and functionality."""

    def test_valid_user_profile(self, sample_user):
        """Test creating a valid user profile."""
        assert sample_user.user_id == "test_user_1"
        assert sample_user.age == 30
        assert sample_user.bmi == 22.9
        assert "pop" in sample_user.pref_music_genres
        assert sample_user.pref_music_genres["pop"] == 0.8

    def test_user_profile_defaults(self):
        """Test UserProfile with minimal required fields."""
        user = UserProfile(
            user_id="minimal_user",
            age=25,
            weight=65.0,
            height=170.0,
            bmi=22.5,
            fitness_level="beginner",
            goals="maintain",
            join_date="2024-01-01"
        )
        assert user.pref_music_genres == {}
        assert user.pref_meal_cuisines == {}
        assert user.pref_workout_focus == {}
        assert user.allergens == []
        assert user.diet_flags == []
        assert user.equipment == []
        assert user.hr_max_override is None

    def test_user_profile_invalid_age(self):
        """Test UserProfile with invalid age."""
        with pytest.raises(ValidationError):
            UserProfile(
                user_id="test",
                age="thirty",  # Should be int
                weight=70.0,
                height=175.0,
                bmi=22.9,
                fitness_level="intermediate",
                goals="weight_loss",
                join_date="2024-01-01"
            )


class TestSleepEntry:
    """Test SleepEntry model validation."""

    def test_valid_sleep_entry(self, sample_sleep_entry):
        """Test creating a valid sleep entry."""
        assert sample_sleep_entry.user_id == "test_user_1"
        assert sample_sleep_entry.sleep_duration_minutes == 480
        assert sample_sleep_entry.sleep_efficiency == 85.0
        assert sample_sleep_entry.bedtime == "22:30"

    def test_sleep_entry_invalid_bedtime_format(self):
        """Test SleepEntry with invalid bedtime format."""
        # This tests the model creation, but actual time parsing would be done in business logic
        sleep_entry = SleepEntry(
            user_id="test_user",
            date="2024-01-15",
            sleep_duration_minutes=480,
            deep_sleep_minutes=120,
            rem_sleep_minutes=90,
            light_sleep_minutes=270,
            sleep_efficiency=85.0,
            bedtime="invalid_time",  # Invalid format, but model accepts strings
            wake_time="06:30"
        )
        # Model creation succeeds, validation would happen in business logic
        assert sleep_entry.bedtime == "invalid_time"

    def test_sleep_entry_invalid_efficiency(self):
        """Test SleepEntry with invalid efficiency."""
        with pytest.raises(ValidationError):
            SleepEntry(
                user_id="test_user",
                date="2024-01-15",
                sleep_duration_minutes=480,
                deep_sleep_minutes=120,
                rem_sleep_minutes=90,
                light_sleep_minutes=270,
                sleep_efficiency="high",  # Should be float
                bedtime="22:30",
                wake_time="06:30"
            )


class TestNutritionEntry:
    """Test NutritionEntry model validation."""

    def test_valid_nutrition_entry(self, sample_nutrition_entry):
        """Test creating a valid nutrition entry."""
        assert sample_nutrition_entry.user_id == "test_user_1"
        assert sample_nutrition_entry.calories_consumed == 2000
        assert sample_nutrition_entry.protein_g == 120.0
        assert sample_nutrition_entry.fiber_g == 25.0

    def test_nutrition_entry_edge_values(self):
        """Test NutritionEntry with edge case values."""
        # Test with zero values (which are valid)
        nutrition = NutritionEntry(
            user_id="test_user",
            date="2024-01-15",
            calories_consumed=0,  # Zero calories is valid for fasting day
            protein_g=0.0,
            carbs_g=0.0,
            fat_g=0.0,
            fiber_g=0.0,
            sugar_g=0.0,
            sodium_mg=0.0
        )
        assert nutrition.calories_consumed == 0
        assert nutrition.protein_g == 0.0


class TestActivityEntry:
    """Test ActivityEntry model validation."""

    def test_valid_activity_entry(self, sample_activity_entry):
        """Test creating a valid activity entry."""
        assert sample_activity_entry.user_id == "test_user_1"
        assert sample_activity_entry.steps == 8000
        assert sample_activity_entry.heart_rate_avg == 140
        assert sample_activity_entry.distance_km == 6.0

    def test_activity_entry_invalid_heart_rate(self):
        """Test ActivityEntry with invalid heart rate."""
        with pytest.raises(ValidationError):
            ActivityEntry(
                user_id="test_user",
                date="2024-01-15",
                steps=8000,
                calories_burned=300,
                active_minutes=45,
                distance_km=6.0,
                heart_rate_avg="normal",  # Should be int
                workout_duration=30
            )


class TestMeasurementEntry:
    """Test MeasurementEntry model validation."""

    def test_valid_measurement_entry(self):
        """Test creating a valid measurement entry."""
        measurement = MeasurementEntry(
            measurement_id="meas_1",
            user_id="test_user_1",
            date="2024-01-15",
            weight=70.0,
            body_fat=15.0,
            muscle_mass=55.0,
            bmi=22.9,
            waist=80.0,
            chest=95.0,
            bicep=30.0,
            thigh=50.0,
            body_water=60.0,
            bone_mass=3.0
        )
        assert measurement.measurement_id == "meas_1"
        assert measurement.weight == 70.0
        assert measurement.notes is None

    def test_measurement_entry_with_notes(self):
        """Test MeasurementEntry with optional notes."""
        measurement = MeasurementEntry(
            measurement_id="meas_1",
            user_id="test_user_1",
            date="2024-01-15",
            weight=70.0,
            body_fat=15.0,
            muscle_mass=55.0,
            bmi=22.9,
            waist=80.0,
            chest=95.0,
            bicep=30.0,
            thigh=50.0,
            body_water=60.0,
            bone_mass=3.0,
            notes="Post-workout measurement"
        )
        assert measurement.notes == "Post-workout measurement"


class TestCatalogModels:
    """Test catalog item models (MusicTrack, MealTemplate, WorkoutTemplate)."""

    def test_valid_music_track(self, sample_music_track):
        """Test creating a valid music track."""
        assert sample_music_track.id == "track_1"
        assert sample_music_track.bpm == 120
        assert sample_music_track.energy == 0.7
        assert "pop" in sample_music_track.genres

    def test_music_track_invalid_energy(self):
        """Test MusicTrack with invalid energy value."""
        with pytest.raises(ValidationError):
            MusicTrack(
                id="track_1",
                title="Test Song",
                artist="Test Artist",
                bpm=120,
                energy="high",  # Should be float
                valence=0.8,
                genres=["pop"]
            )

    def test_valid_meal_template(self, sample_meal_template):
        """Test creating a valid meal template."""
        assert sample_meal_template.id == "meal_1"
        assert sample_meal_template.calories == 450
        assert "italian" in sample_meal_template.cuisine_tags
        assert sample_meal_template.allergens == []

    def test_meal_template_with_allergens(self):
        """Test MealTemplate with allergens."""
        meal = MealTemplate(
            id="meal_2",
            name="Peanut Butter Toast",
            cuisine_tags=["american"],
            calories=300,
            protein_g=12.0,
            carbs_g=30.0,
            fat_g=16.0,
            fiber_g=4.0,
            sugar_g=8.0,
            sodium_mg=200.0,
            allergens=["nuts", "gluten"],
            diet_ok=["omnivore"]
        )
        assert "nuts" in meal.allergens
        assert "gluten" in meal.allergens

    def test_valid_workout_template(self, sample_workout_template):
        """Test creating a valid workout template."""
        assert sample_workout_template.id == "workout_1"
        assert sample_workout_template.intensity_zone == "Z2"
        assert sample_workout_template.duration_min == 30
        assert "dumbbells" in sample_workout_template.equipment_needed


class TestRequestResponseModels:
    """Test request and response DTOs."""

    def test_recommend_request_minimal(self):
        """Test RecommendRequest with minimal fields."""
        request = RecommendRequest(user_id="test_user")
        assert request.user_id == "test_user"
        assert request.intent is None
        assert request.now is None

    def test_recommend_request_full(self):
        """Test RecommendRequest with all fields."""
        request = RecommendRequest(
            user_id="test_user",
            intent="music",
            now="2024-01-15T10:30:00Z",
            current_hr=120,
            rpe=6.5,
            hours_since_last_meal=2.5
        )
        assert request.intent == "music"
        assert request.current_hr == 120
        assert request.rpe == 6.5

    def test_recommend_response(self):
        """Test RecommendResponse creation."""
        response = RecommendResponse(
            domain="music",
            state={"Readiness": 75, "Fuel": 60, "Strain": 45},
            item={"id": "track_1", "title": "Test Song"},
            bandit_arm="high_energy"
        )
        assert response.domain == "music"
        assert response.state["Readiness"] == 75
        assert response.bandit_arm == "high_energy"

    def test_feedback_minimal(self):
        """Test Feedback with minimal fields."""
        feedback = Feedback(
            user_id="test_user",
            domain="music",
            item_id="track_1"
        )
        assert feedback.user_id == "test_user"
        assert feedback.thumbs == 0
        assert feedback.completed is None

    def test_feedback_full(self):
        """Test Feedback with all fields."""
        feedback = Feedback(
            user_id="test_user",
            domain="workout",
            item_id="workout_1",
            thumbs=1,
            completed=1,
            hr_zone_frac=0.8,
            rpe=7.0,
            ate=None,
            protein_gap_closed_norm=None,
            skipped_early=0
        )
        assert feedback.thumbs == 1
        assert feedback.completed == 1
        assert feedback.hr_zone_frac == 0.8
        assert feedback.skipped_early == 0