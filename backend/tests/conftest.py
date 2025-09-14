"""Test configuration and fixtures."""

import pytest
from datetime import datetime
from body_behavior_recommender.models import (
    UserProfile, SleepEntry, NutritionEntry, ActivityEntry, 
    MusicTrack, MealTemplate, WorkoutTemplate
)

@pytest.fixture
def sample_user():
    """Sample user profile for testing."""
    return UserProfile(
        user_id="test_user_1",
        age=30,
        weight=70.0,
        height=175.0,
        bmi=22.9,
        fitness_level="intermediate",
        goals="weight_loss",
        join_date="2024-01-01",
        pref_music_genres={"pop": 0.8, "rock": 0.6, "electronic": 0.7},
        pref_meal_cuisines={"italian": 0.9, "asian": 0.7},
        pref_workout_focus={"strength": 0.8, "cardio": 0.6},
        allergens=["nuts"],
        diet_flags=["vegetarian"],
        equipment=["dumbbells", "resistance_bands"]
    )

@pytest.fixture
def sample_sleep_entry():
    """Sample sleep entry for testing."""
    return SleepEntry(
        user_id="test_user_1",
        date="2024-01-15",
        sleep_duration_minutes=480,
        deep_sleep_minutes=120,
        rem_sleep_minutes=90,
        light_sleep_minutes=270,
        sleep_efficiency=85.0,
        bedtime="22:30",
        wake_time="06:30"
    )

@pytest.fixture
def sample_nutrition_entry():
    """Sample nutrition entry for testing."""
    return NutritionEntry(
        user_id="test_user_1",
        date="2024-01-15",
        calories_consumed=2000,
        protein_g=120.0,
        carbs_g=250.0,
        fat_g=80.0,
        fiber_g=25.0,
        sugar_g=50.0,
        sodium_mg=2000.0
    )

@pytest.fixture
def sample_activity_entry():
    """Sample activity entry for testing."""
    return ActivityEntry(
        user_id="test_user_1",
        date="2024-01-15",
        steps=8000,
        calories_burned=300,
        active_minutes=45,
        distance_km=6.0,
        heart_rate_avg=140,
        workout_duration=30
    )

@pytest.fixture
def sample_music_track():
    """Sample music track for testing."""
    return MusicTrack(
        id="track_1",
        title="Test Song",
        artist="Test Artist",
        bpm=120,
        energy=0.7,
        valence=0.8,
        genres=["pop", "electronic"]
    )

@pytest.fixture
def sample_meal_template():
    """Sample meal template for testing."""
    return MealTemplate(
        id="meal_1",
        name="Vegetarian Pasta",
        cuisine_tags=["italian", "vegetarian"],
        calories=450,
        protein_g=15.0,
        carbs_g=65.0,
        fat_g=12.0,
        fiber_g=8.0,
        sugar_g=5.0,
        sodium_mg=600.0,
        allergens=[],
        diet_ok=["vegetarian", "omnivore"]
    )

@pytest.fixture
def sample_workout_template():
    """Sample workout template for testing."""
    return WorkoutTemplate(
        id="workout_1",
        name="Beginner Strength Training",
        intensity_zone="Z2",
        impact="moderate",
        equipment_needed=["dumbbells"],
        duration_min=30,
        focus_tags=["strength", "beginner"]
    )

@pytest.fixture
def sample_state():
    """Sample user state for testing."""
    return {
        "Readiness": 75,
        "Fuel": 60,
        "Strain": 45
    }