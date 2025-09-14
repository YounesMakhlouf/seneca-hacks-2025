"""Tests for utility functions."""

import pytest
import numpy as np
from unittest.mock import patch
from datetime import datetime

from body_behavior_recommender.utils import (
    clamp01, normalize01, mean_std, get_today_iso, compute_hr_max,
    energy_cap_from_state, target_bpm_from_state, cosine_pref_fit,
    novelty_bonus, repetition_penalty, risk_penalties_meal,
    risk_penalties_workout, zone_from_state
)
from body_behavior_recommender.models import UserProfile, MealTemplate, WorkoutTemplate


class TestMathHelpers:
    """Test mathematical utility functions."""

    def test_clamp01_normal_values(self):
        """Test clamp01 with normal values."""
        assert clamp01(0.5) == 0.5
        assert clamp01(0.0) == 0.0
        assert clamp01(1.0) == 1.0

    def test_clamp01_out_of_bounds(self):
        """Test clamp01 with out-of-bounds values."""
        assert clamp01(-0.5) == 0.0
        assert clamp01(1.5) == 1.0
        assert clamp01(-10) == 0.0
        assert clamp01(100) == 1.0

    def test_normalize01_normal_range(self):
        """Test normalize01 with normal range."""
        assert normalize01(5, 0, 10) == 0.5
        assert normalize01(0, 0, 10) == 0.0
        assert normalize01(10, 0, 10) == 1.0
        assert normalize01(2.5, 0, 5) == 0.5

    def test_normalize01_invalid_range(self):
        """Test normalize01 with invalid range (hi <= lo)."""
        assert normalize01(5, 10, 10) == 0.0
        assert normalize01(5, 10, 5) == 0.0

    def test_normalize01_out_of_bounds(self):
        """Test normalize01 with values outside range."""
        assert normalize01(-5, 0, 10) == 0.0
        assert normalize01(15, 0, 10) == 1.0

    def test_mean_std_normal_values(self):
        """Test mean_std with normal values."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        mean, std = mean_std(values)
        assert abs(mean - 3.0) < 1e-6
        assert abs(std - np.std(values)) < 1e-6

    def test_mean_std_empty_list(self):
        """Test mean_std with empty list."""
        mean, std = mean_std([])
        assert mean == 0.0
        assert std == 1.0

    def test_mean_std_single_value(self):
        """Test mean_std with single value."""
        mean, std = mean_std([5.0])
        assert mean == 5.0
        assert std == 1.0  # Default when std is 0


class TestTimeHelpers:
    """Test time-related utility functions."""

    def test_get_today_iso_with_provided_date(self):
        """Test get_today_iso with provided ISO date."""
        result = get_today_iso("2024-01-15T10:30:00Z")
        assert result == "2024-01-15"

    def test_get_today_iso_with_none(self):
        """Test get_today_iso with None (should use current date)."""
        with patch('body_behavior_recommender.utils.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2024, 1, 15, 10, 30, 0)
            result = get_today_iso(None)
            assert result == "2024-01-15"


class TestHeartRateCalculations:
    """Test heart rate-related calculations."""

    def test_compute_hr_max_with_override(self, sample_user):
        """Test compute_hr_max with hr_max_override."""
        sample_user.hr_max_override = 190
        result = compute_hr_max(sample_user)
        assert result == 190

    def test_compute_hr_max_without_override(self, sample_user):
        """Test compute_hr_max without override (using age formula)."""
        sample_user.hr_max_override = None
        result = compute_hr_max(sample_user)
        # Formula: 208 - 0.7 * age
        expected = int(208 - 0.7 * sample_user.age)
        assert result == expected

    def test_target_bpm_from_state_high_readiness_low_strain(self, sample_user):
        """Test target_bpm_from_state with high readiness and low strain."""
        state = {"Readiness": 70, "Strain": 50}
        result = target_bpm_from_state(sample_user, state)

        # Should use 0.65 * hrmax for high readiness and low strain
        hrmax = compute_hr_max(sample_user)
        target_hr = 0.65 * hrmax
        expected_bpm = int(np.clip((target_hr / hrmax) * 180.0, 90, 180))
        assert result == expected_bpm

    def test_target_bpm_from_state_low_readiness(self, sample_user):
        """Test target_bpm_from_state with low readiness."""
        state = {"Readiness": 50, "Strain": 40}
        result = target_bpm_from_state(sample_user, state)

        # Should use 0.55 * hrmax for low readiness
        hrmax = compute_hr_max(sample_user)
        target_hr = 0.55 * hrmax
        expected_bpm = int(np.clip((target_hr / hrmax) * 180.0, 90, 180))
        assert result == expected_bpm


class TestStateBasedHelpers:
    """Test state-based utility functions."""

    def test_energy_cap_from_state_low_readiness(self):
        """Test energy_cap_from_state with low readiness."""
        state = {"Readiness": 30, "Strain": 50}
        result = energy_cap_from_state(state)
        assert result == 0.6

    def test_energy_cap_from_state_high_strain(self):
        """Test energy_cap_from_state with high strain."""
        state = {"Readiness": 60, "Strain": 80}
        result = energy_cap_from_state(state)
        assert result == 0.6

    def test_energy_cap_from_state_moderate_readiness(self):
        """Test energy_cap_from_state with moderate readiness."""
        state = {"Readiness": 50, "Strain": 40}
        result = energy_cap_from_state(state)
        assert result == 0.75

    def test_energy_cap_from_state_high_readiness_low_strain(self):
        """Test energy_cap_from_state with high readiness and low strain."""
        state = {"Readiness": 70, "Strain": 30}
        result = energy_cap_from_state(state)
        assert result == 0.85

    def test_zone_from_state_low_readiness(self):
        """Test zone_from_state with low readiness."""
        state = {"Readiness": 30, "Strain": 50}
        result = zone_from_state(state)
        assert result == "Z2_low"

    def test_zone_from_state_high_strain(self):
        """Test zone_from_state with high strain."""
        state = {"Readiness": 60, "Strain": 80}
        result = zone_from_state(state)
        assert result == "Z2_low"

    def test_zone_from_state_moderate_readiness(self):
        """Test zone_from_state with moderate readiness."""
        state = {"Readiness": 50, "Strain": 40}
        result = zone_from_state(state)
        assert result == "Z2"

    def test_zone_from_state_high_readiness(self):
        """Test zone_from_state with high readiness."""
        state = {"Readiness": 70, "Strain": 30}
        result = zone_from_state(state)
        assert result == "Tempo"


class TestPreferenceHelpers:
    """Test preference-related utility functions."""

    def test_cosine_pref_fit_with_matching_tags(self):
        """Test cosine_pref_fit with matching tags."""
        tag_weights = {"pop": 0.8, "rock": 0.6, "electronic": 0.9}
        item_tags = ["pop", "electronic"]
        result = cosine_pref_fit(tag_weights, item_tags)

        # Should be average of 0.8 and 0.9 = 0.85
        expected = (0.8 + 0.9) / 2
        assert abs(result - expected) < 1e-6

    def test_cosine_pref_fit_with_partial_match(self):
        """Test cosine_pref_fit with partially matching tags."""
        tag_weights = {"pop": 0.8, "rock": 0.6}
        item_tags = ["pop", "electronic", "jazz"]
        result = cosine_pref_fit(tag_weights, item_tags)

        # Should be average of 0.8, 0.0, 0.0 = 0.8/3
        expected = 0.8 / 3
        assert abs(result - expected) < 1e-6

    def test_cosine_pref_fit_empty_tags(self):
        """Test cosine_pref_fit with empty item tags."""
        tag_weights = {"pop": 0.8, "rock": 0.6}
        item_tags = []
        result = cosine_pref_fit(tag_weights, item_tags)
        assert result == 0.0

    def test_cosine_pref_fit_empty_weights(self):
        """Test cosine_pref_fit with empty tag weights."""
        tag_weights = {}
        item_tags = ["pop", "rock"]
        result = cosine_pref_fit(tag_weights, item_tags)
        assert result == 0.0


class TestNoveltyAndPenalties:
    """Test novelty and penalty functions."""

    def test_novelty_bonus_returns_float(self):
        """Test novelty_bonus returns a float in valid range."""
        result = novelty_bonus("item_1", "music")
        assert isinstance(result, float)
        assert 0.0 <= result <= 0.1

    def test_repetition_penalty(self):
        """Test repetition_penalty (currently returns 0.0)."""
        result = repetition_penalty("item_1", "music")
        assert result == 0.0

    def test_risk_penalties_meal_with_allergens(self, sample_user):
        """Test risk_penalties_meal with allergen conflict."""
        meal = MealTemplate(
            id="meal_1",
            name="Peanut Dish",
            cuisine_tags=["asian"],
            calories=400,
            protein_g=20.0,
            carbs_g=50.0,
            fat_g=15.0,
            fiber_g=5.0,
            sugar_g=10.0,
            sodium_mg=800.0,
            allergens=["nuts"],  # User has nuts allergy
            diet_ok=["omnivore", "vegetarian"]
        )
        result = risk_penalties_meal(meal, sample_user)
        assert result == 1.0  # Hard violation

    def test_risk_penalties_meal_diet_conflict(self, sample_user):
        """Test risk_penalties_meal with diet conflict."""
        meal = MealTemplate(
            id="meal_1",
            name="Beef Steak",
            cuisine_tags=["american"],
            calories=500,
            protein_g=40.0,
            carbs_g=0.0,
            fat_g=30.0,
            fiber_g=0.0,
            sugar_g=0.0,
            sodium_mg=600.0,
            allergens=[],
            diet_ok=["omnivore"]  # User is vegetarian
        )
        result = risk_penalties_meal(meal, sample_user)
        assert result == 1.0  # Hard violation

    def test_risk_penalties_meal_safe(self, sample_user):
        """Test risk_penalties_meal with safe meal."""
        meal = MealTemplate(
            id="meal_1",
            name="Vegetable Pasta",
            cuisine_tags=["italian"],
            calories=400,
            protein_g=15.0,
            carbs_g=60.0,
            fat_g=10.0,
            fiber_g=8.0,
            sugar_g=5.0,
            sodium_mg=500.0,
            allergens=[],
            diet_ok=["vegetarian", "omnivore"]
        )
        result = risk_penalties_meal(meal, sample_user)
        assert result == 0.0  # No violations

    def test_risk_penalties_workout_high_intensity_low_readiness(self, sample_user):
        """Test risk_penalties_workout with high intensity and low readiness."""
        workout = WorkoutTemplate(
            id="workout_1",
            name="High Intensity Training",
            intensity_zone="Tempo",
            impact="high",
            equipment_needed=[],
            duration_min=45,
            focus_tags=["cardio", "intense"]
        )
        state = {"Readiness": 30, "Strain": 50}
        result = risk_penalties_workout(workout, sample_user, state)
        assert result == 0.8  # Penalty for high intensity on low readiness

    def test_risk_penalties_workout_safe(self, sample_user):
        """Test risk_penalties_workout with safe workout."""
        workout = WorkoutTemplate(
            id="workout_1",
            name="Light Training",
            intensity_zone="Z2",
            impact="low",
            equipment_needed=["dumbbells"],
            duration_min=30,
            focus_tags=["strength"]
        )
        state = {"Readiness": 70, "Strain": 30}
        result = risk_penalties_workout(workout, sample_user, state)
        assert result == 0.0  # No penalties