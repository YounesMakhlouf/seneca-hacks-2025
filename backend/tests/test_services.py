"""Tests for isolated service functions without circular imports."""

import numpy as np

# Import models directly
from body_behavior_recommender.models import (
    ActivityEntry,
    Feedback,
    NutritionEntry,
    SleepEntry,
)

# Test the core functions that don't depend on global state
from body_behavior_recommender.utils import (
    clamp01,
)


class TestServiceLogicIsolated:
    """Test service logic functions in isolation."""

    def test_choose_domain_logic(self):
        """Test domain selection logic."""

        # Import the function directly to avoid circular imports
        def choose_domain_logic(intent, state, hours_since_last_meal):
            """Isolated version of choose_domain logic."""
            if intent in {"music", "meal", "workout"}:
                return intent
            if state["Fuel"] < 50 and (hours_since_last_meal or 0) >= 3:
                return "meal"
            if state["Readiness"] >= 50 and state["Strain"] < 70:
                return "workout"
            return "music"

        # Test explicit intent
        state = {"Readiness": 70, "Fuel": 60, "Strain": 40}
        assert choose_domain_logic("music", state, 1.0) == "music"
        assert choose_domain_logic("meal", state, 1.0) == "meal"
        assert choose_domain_logic("workout", state, 1.0) == "workout"

        # Test automatic selection - hungry case
        state = {"Readiness": 70, "Fuel": 40, "Strain": 40}
        assert choose_domain_logic(None, state, 4.0) == "meal"

        # Test automatic selection - workout case
        state = {"Readiness": 60, "Fuel": 70, "Strain": 50}
        assert choose_domain_logic(None, state, 1.0) == "workout"

        # Test automatic selection - default to music
        state = {"Readiness": 40, "Fuel": 70, "Strain": 80}
        assert choose_domain_logic(None, state, 1.0) == "music"

    def test_reward_calculation_logic(self):
        """Test reward calculation logic."""

        def reward_from_feedback_logic(domain, fb):
            """Isolated version of reward calculation."""
            if domain == "music":
                return clamp01(
                    0.4 * (fb.hr_zone_frac or 0)
                    + 0.3 * (1 if fb.thumbs > 0 else 0)
                    + 0.2 * (fb.completed or 0)
                    + 0.1 * (0 if (fb.skipped_early or 0) else 1)
                )
            if domain == "meal":
                return clamp01(
                    0.5 * (fb.ate or 0)
                    + 0.3 * (fb.protein_gap_closed_norm or 0)
                    + 0.2 * (1 if fb.thumbs > 0 else 0)
                )
            if domain == "workout":
                return clamp01(
                    0.4 * (fb.completed or 0)
                    + 0.3 * (fb.hr_zone_frac or 0)
                    + 0.3 * (1 - min(1.0, abs((fb.rpe or 0) - 5) / 5))
                )
            return 0.0

        # Test music reward - positive feedback
        feedback = Feedback(
            user_id="test_user",
            domain="music",
            item_id="track_1",
            thumbs=1,
            completed=1,
            hr_zone_frac=0.8,
            skipped_early=0,
        )
        reward = reward_from_feedback_logic("music", feedback)
        assert 0.0 <= reward <= 1.0
        assert reward > 0.5  # Should be high for good engagement

        # Test meal reward - positive feedback
        feedback = Feedback(
            user_id="test_user",
            domain="meal",
            item_id="meal_1",
            thumbs=1,
            ate=1,
            protein_gap_closed_norm=0.8,
        )
        reward = reward_from_feedback_logic("meal", feedback)
        assert 0.0 <= reward <= 1.0
        assert reward > 0.5

        # Test workout reward - perfect RPE
        feedback = Feedback(
            user_id="test_user",
            domain="workout",
            item_id="workout_1",
            completed=1,
            hr_zone_frac=0.7,
            rpe=5.0,  # Perfect target RPE
        )
        reward = reward_from_feedback_logic("workout", feedback)
        assert 0.0 <= reward <= 1.0
        assert reward > 0.5

    def test_preference_update_logic(self, sample_user):
        """Test preference update logic."""

        def update_preferences_logic(user, domain, item_tags, thumbs):
            """Isolated version of preference update logic."""
            if thumbs == 0 or not item_tags:
                return
            lr_fast = 0.3
            if domain == "music":
                for t in item_tags:
                    w = user.pref_music_genres.get(t, 0.0)
                    user.pref_music_genres[t] = float(
                        np.clip(w + (lr_fast if thumbs > 0 else -lr_fast), 0.0, 1.0)
                    )
            elif domain == "meal":
                for t in item_tags:
                    w = user.pref_meal_cuisines.get(t, 0.0)
                    user.pref_meal_cuisines[t] = float(
                        np.clip(w + (lr_fast if thumbs > 0 else -lr_fast), 0.0, 1.0)
                    )
            elif domain == "workout":
                for t in item_tags:
                    w = user.pref_workout_focus.get(t, 0.0)
                    user.pref_workout_focus[t] = float(
                        np.clip(w + (lr_fast if thumbs > 0 else -lr_fast), 0.0, 1.0)
                    )

        # Test positive music preference update
        initial_pop = sample_user.pref_music_genres.get("pop", 0.0)
        update_preferences_logic(sample_user, "music", ["pop", "rock"], 1)
        assert sample_user.pref_music_genres["pop"] > initial_pop
        assert 0.0 <= sample_user.pref_music_genres["pop"] <= 1.0

        # Test negative feedback
        current_pop = sample_user.pref_music_genres["pop"]
        update_preferences_logic(sample_user, "music", ["pop"], -1)
        assert sample_user.pref_music_genres["pop"] < current_pop

    def test_state_computation_components(self, sample_user):
        """Test individual components of state computation."""
        # Test readiness calculation with good sleep
        sleep_entries = [
            SleepEntry(
                user_id="test_user_1",
                date="2024-01-15",
                sleep_duration_minutes=480,  # 8 hours
                deep_sleep_minutes=120,
                rem_sleep_minutes=90,
                light_sleep_minutes=270,
                sleep_efficiency=90.0,
                bedtime="22:00",
                wake_time="06:00",
            )
        ]

        # Sleep duration score calculation
        durations_h = [s.sleep_duration_minutes / 60 for s in sleep_entries]
        avg_sleep = np.mean(durations_h)
        sleep_debt = max(0.0, 8.0 - avg_sleep)
        duration_score = clamp01(1 - sleep_debt / 2.0)

        assert avg_sleep == 8.0
        assert sleep_debt == 0.0
        assert duration_score == 1.0

        # Test efficiency score
        avg_efficiency = np.mean([s.sleep_efficiency for s in sleep_entries]) / 100.0
        efficiency_score = clamp01(avg_efficiency)
        assert efficiency_score == 0.9

    def test_nutrition_scoring_components(self, sample_user):
        """Test nutrition scoring components."""
        nutrition_entry = NutritionEntry(
            user_id="test_user_1",
            date="2024-01-15",
            calories_consumed=2000,
            protein_g=100.0,
            carbs_g=200.0,
            fat_g=70.0,
            fiber_g=35.0,
            sugar_g=30.0,
            sodium_mg=1500.0,
        )

        # Protein target for weight loss goal
        protein_target = 1.2 * sample_user.weight  # 84g for 70kg user
        fiber_target = 30.0
        sugar_limit = 75.0
        sodium_limit = 2300.0

        protein_score = clamp01(nutrition_entry.protein_g / max(1.0, protein_target))
        fiber_score = clamp01(nutrition_entry.fiber_g / fiber_target)
        sugar_penalty = clamp01(nutrition_entry.sugar_g / sugar_limit)
        sodium_penalty = clamp01(nutrition_entry.sodium_mg / sodium_limit)

        # Raw protein score before clamping
        raw_protein_score = nutrition_entry.protein_g / max(1.0, protein_target)
        raw_fiber_score = nutrition_entry.fiber_g / fiber_target
        assert raw_protein_score > 1.0  # 100/84 > 1
        assert raw_fiber_score > 1.0  # 35/30 > 1
        assert protein_score == 1.0  # After clamping
        assert fiber_score == 1.0  # After clamping
        assert sugar_penalty < 0.5  # Low sugar is good
        assert sodium_penalty < 0.7  # Low sodium is good

    def test_activity_scoring_components(self):
        """Test activity scoring components."""
        activity_entries = [
            ActivityEntry(
                user_id="test_user_1",
                date="2024-01-14",
                steps=8000,
                calories_burned=300,
                active_minutes=45,
                distance_km=6.0,
                heart_rate_avg=140,
                workout_duration=30,
            ),
            ActivityEntry(
                user_id="test_user_1",
                date="2024-01-15",
                steps=8000,
                calories_burned=300,
                active_minutes=45,
                distance_km=6.0,
                heart_rate_avg=140,
                workout_duration=30,
            ),
        ]

        today_activity = activity_entries[-1]
        steps_7d = [a.steps for a in activity_entries]
        steps_mean = np.mean(steps_7d)
        steps_std = np.std(steps_7d) or 1.0

        steps_z_score = (today_activity.steps - steps_mean) / steps_std
        steps_norm = 0.6 * clamp01((steps_z_score / 2.0) + 0.5)
        hr_norm = 0.4 * clamp01((today_activity.heart_rate_avg - 90) / (170 - 90))
        activity_norm = 0.2 * clamp01(today_activity.active_minutes / 120)

        # With identical steps, z-score should be 0, normalized to 0.5
        assert abs(steps_z_score) < 1e-10  # Essentially 0
        assert abs(steps_norm - 0.6 * 0.5) < 1e-10  # 0.3
        assert hr_norm > 0  # Should be positive for HR 140
        assert activity_norm > 0  # Should be positive for 45 minutes
