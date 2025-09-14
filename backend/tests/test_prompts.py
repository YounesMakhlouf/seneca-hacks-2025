from body_behavior_recommender.models import UserProfile
from body_behavior_recommender.prompts import (
    SYSTEM_PROMPT_EXPLANATION,
    build_explanation_prompt,
)


def _fake_user():
    return UserProfile(
        user_id="u1",
        age=30,
        weight=70.0,
        height=175.0,
        bmi=22.8,
        fitness_level="intermediate",
        goals="endurance",
        join_date="2024-01-01",
    )


STATE = {"Readiness": 65, "Fuel": 55, "Strain": 40}

ITEM_MUSIC = {
    "title": "Flow State",
    "artist": "Synth Squad",
    "bpm": 128,
    "energy": 0.78,
}
ITEM_MEAL = {
    "name": "Quinoa Power Bowl",
    "calories": 520,
    "protein_g": 32,
    "fiber_g": 9,
}
ITEM_WORKOUT = {"name": "Tempo Intervals", "duration_min": 30, "intensity_zone": "Z2"}


def test_prompt_music_contains_core_sections():
    prompt = build_explanation_prompt(
        domain="music",
        user=_fake_user(),
        state=STATE,
        item=ITEM_MUSIC,
        sleep_context="Sleep 7.2h @ 90% efficiency",
        activity_context="Activity 8000 steps / 45 active min",
    )
    assert "Track:" in prompt
    assert "User Context:" in prompt
    assert "Rules:" in prompt
    assert "R 65/100" in prompt


def test_prompt_meal_contains_nutrition():
    prompt = build_explanation_prompt(
        domain="meal",
        user=_fake_user(),
        state=STATE,
        item=ITEM_MEAL,
        nutrition_context="Intake 1500 kcal / 80g protein",
    )
    assert "Meal:" in prompt
    assert "Protein:" in prompt
    assert "User Context:" in prompt


def test_prompt_workout_contains_intensity():
    prompt = build_explanation_prompt(
        domain="workout",
        user=_fake_user(),
        state=STATE,
        item=ITEM_WORKOUT,
        sleep_context="Sleep 6.8h @ 85% efficiency",
    )
    assert "Workout:" in prompt
    assert "Intensity:" in prompt
    assert "Goal:" in prompt


def test_system_prompt_style_keywords():
    # Sanity check some coaching tone aspects are present
    for kw in ["supportive", "empowering", "concise"]:
        assert kw in SYSTEM_PROMPT_EXPLANATION.lower()
