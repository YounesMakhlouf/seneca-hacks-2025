"""Business logic and services for the Body-to-Behavior Recommender."""

import os
import random
from typing import Dict, List, Optional, Tuple

import numpy as np
from mabwiser.mab import MAB, LearningPolicy, NeighborhoodPolicy
from openai import OpenAI

# Static catalogs for recommendations
from .app import ARMS, MEALS, MUSIC, WORKOUTS
from .models import (
    ActivityEntry,
    Feedback,
    MealTemplate,
    MusicTrack,
    NutritionEntry,
    SleepEntry,
    UserProfile,
    WorkoutTemplate,
)
from .prompts import SYSTEM_PROMPT_EXPLANATION, build_explanation_prompt
from .utils import (
    clamp01,
    cosine_pref_fit,
    energy_cap_from_state,
    get_today_iso,
    mean_std,
    novelty_bonus,
    risk_penalties_meal,
    risk_penalties_workout,
    target_bpm_from_state,
    zone_from_state,
)


def compute_state_entries(
    user: UserProfile,
    sleep_entries: List[SleepEntry],
    todays_nutrition: Optional[NutritionEntry],
    activity_entries: List[ActivityEntry],
) -> Dict[str, int]:
    """Pure state computation from supplied entries (Mongo-friendly).

    Falls back to default baselines when data slices are empty.
    """
    # Readiness
    recent_sleep = sleep_entries[-2:]
    if recent_sleep:
        durations_h = [s.sleep_duration_minutes / 60 for s in recent_sleep]
        avg_sleep = np.mean(durations_h)
        sleep_debt = max(0.0, 8.0 - avg_sleep)
        duration_score = clamp01(1 - sleep_debt / 2.0)
        avg_efficiency = np.mean([s.sleep_efficiency for s in recent_sleep]) / 100.0
        efficiency_score = clamp01(avg_efficiency)
        # Bedtime consistency (use up to 7 entries)
        bedtime_minutes = []
        for s in sleep_entries[-7:]:
            try:
                hour, minute = map(int, s.bedtime.split(":"))
                bedtime_minutes.append(hour * 60 + minute)
            except Exception:
                continue
        if len(bedtime_minutes) >= 2:
            bedtime_variance = np.std(bedtime_minutes)
            bedtime_consistency = clamp01(1 - bedtime_variance / 120.0)
        else:
            bedtime_consistency = 0.5
        # Recovery factor from last 7 activities
        if len(activity_entries) >= 2:
            today_steps = activity_entries[-1].steps
            recent_steps = [a.steps for a in activity_entries[-7:]]
            mean_s, std_s = mean_std(recent_steps)
            if std_s > 0:
                strain_z = (today_steps - mean_s) / std_s
                recovery_factor = clamp01(1 - strain_z / 2.0)
            else:
                recovery_factor = 0.5
        else:
            recovery_factor = 0.5
        sleep_component = 0.7 * duration_score + 0.3 * efficiency_score
        readiness = round(
            100
            * (
                0.50 * sleep_component
                + 0.25 * bedtime_consistency
                + 0.25 * recovery_factor
            )
        )
    else:
        readiness = 55

    # Fuel
    if todays_nutrition:
        protein_target = (1.4 if user.goals == "endurance" else 1.2) * user.weight
        fiber_target = 30.0
        sugar_limit = 75.0
        sodium_limit = 2300.0
        protein_score = clamp01(todays_nutrition.protein_g / max(1.0, protein_target))
        fiber_score = clamp01(todays_nutrition.fiber_g / fiber_target)
        sugar_penalty = clamp01(todays_nutrition.sugar_g / sugar_limit)
        sodium_penalty = clamp01(todays_nutrition.sodium_mg / sodium_limit)
        fuel = round(
            100
            * (
                0.45 * protein_score
                + 0.25 * fiber_score
                + 0.15 * (1 - sugar_penalty)
                + 0.15 * (1 - sodium_penalty)
            )
        )
    else:
        fuel = 50

    # Strain
    if activity_entries:
        today_activity = activity_entries[-1]
        steps_7d = [a.steps for a in activity_entries[-7:]]
        steps_mean, steps_std = mean_std(
            steps_7d if steps_7d else [today_activity.steps]
        )
        steps_z_score = (today_activity.steps - steps_mean) / (
            steps_std if steps_std else 1.0
        )
        steps_norm = 0.6 * clamp01((steps_z_score / 2.0) + 0.5)
        hr_norm = 0.4 * clamp01((today_activity.heart_rate_avg - 90) / (170 - 90))
        activity_norm = 0.2 * clamp01(today_activity.active_minutes / 120)
        strain = round(100 * clamp01(steps_norm + hr_norm + activity_norm))
    else:
        strain = 40

    return {
        "Readiness": int(min(100, max(0, readiness))),
        "Fuel": int(min(100, max(0, fuel))),
        "Strain": int(min(100, max(0, strain))),
    }


def compute_state(user: UserProfile, user_id: str, today_iso: str) -> Dict[str, int]:
    """
    Compute user's current physiological state based on sleep, nutrition, and activity data.

    Returns:
        Dict with three scores (0-100):
        - Readiness: Sleep-based recovery and circadian health
        - Fuel: Nutritional adequacy for today's needs
        - Strain: Current activity load and stress
    """

    # === READINESS SCORE (Sleep-based recovery) ===
    readiness = _compute_readiness_score(user_id)

    # === FUEL SCORE (Nutritional status) ===
    fuel = _compute_fuel_score(user, user_id, today_iso)

    # === STRAIN SCORE (Activity load) ===
    strain = _compute_strain_score(user_id)

    return {"Readiness": readiness, "Fuel": fuel, "Strain": strain}


def _compute_readiness_score(user_id: str) -> int:
    """Calculate readiness score based on sleep quality and consistency."""
    recent_sleep = SLEEP.get(user_id, [])[-2:]  # Last 2 nights

    if not recent_sleep:
        return 55  # Default baseline score

    # 1. Sleep Duration Component (compare to 8h target)
    durations_h = [s.sleep_duration_minutes / 60 for s in recent_sleep]
    avg_sleep = np.mean(durations_h)
    sleep_debt = max(0.0, 8.0 - avg_sleep)
    duration_score = clamp01(1 - sleep_debt / 2.0)  # Penalize sleep debt

    # 2. Sleep Efficiency Component
    avg_efficiency = np.mean([s.sleep_efficiency for s in recent_sleep]) / 100.0
    efficiency_score = clamp01(avg_efficiency)

    # 3. Chronotype Consistency (bedtime variability over 7 days)
    bedtime_consistency = _calculate_bedtime_consistency(user_id)

    # 4. Recovery Factor (based on recent activity strain)
    recovery_factor = _calculate_recovery_factor(user_id)

    # Weighted combination of sleep components
    sleep_component = 0.7 * duration_score + 0.3 * efficiency_score

    # Final readiness score (0-100)
    readiness = round(
        100
        * (
            0.50 * sleep_component  # Primary: sleep quality
            + 0.25 * bedtime_consistency  # Circadian stability
            + 0.25 * recovery_factor  # Activity recovery
        )
    )

    return min(100, max(0, readiness))


def _compute_fuel_score(user: UserProfile, user_id: str, today_iso: str) -> int:
    """Calculate fuel score based on today's nutritional intake."""
    # Find today's nutrition data
    today_nutrition = None
    for entry in reversed(NUTRITION.get(user_id, [])):
        if entry.date <= today_iso:
            today_nutrition = entry
            break

    if not today_nutrition:
        return 50  # Default baseline without data

    # Nutritional targets based on user goals
    protein_target = (1.4 if user.goals == "endurance" else 1.2) * user.weight
    fiber_target = 30.0
    sugar_limit = 75.0
    sodium_limit = 2300.0

    # Calculate component scores
    protein_score = clamp01(today_nutrition.protein_g / max(1.0, protein_target))
    fiber_score = clamp01(today_nutrition.fiber_g / fiber_target)
    sugar_penalty = clamp01(today_nutrition.sugar_g / sugar_limit)
    sodium_penalty = clamp01(today_nutrition.sodium_mg / sodium_limit)

    # Weighted fuel score (0-100)
    fuel = round(
        100
        * (
            0.45 * protein_score  # Most important: protein adequacy
            + 0.25 * fiber_score  # Digestive health
            + 0.15 * (1 - sugar_penalty)  # Avoid excess sugar
            + 0.15 * (1 - sodium_penalty)  # Avoid excess sodium
        )
    )

    return min(100, max(0, fuel))


def _compute_strain_score(user_id: str) -> int:
    """Calculate strain score based on today's activity load."""
    activity_data = ACTIVITY.get(user_id, [])

    if not activity_data:
        return 40  # Low baseline strain without data

    today_activity = activity_data[-1]

    # Normalize today's metrics against weekly baselines
    steps_7d = [a.steps for a in activity_data[-7:]]
    steps_mean, steps_std = mean_std(steps_7d if steps_7d else [today_activity.steps])

    # Calculate normalized components
    steps_z_score = (today_activity.steps - steps_mean) / (
        steps_std if steps_std else 1.0
    )
    steps_norm = 0.6 * clamp01((steps_z_score / 2.0) + 0.5)  # Z-score to 0-1

    hr_norm = 0.4 * clamp01((today_activity.heart_rate_avg - 90) / (170 - 90))
    activity_norm = 0.2 * clamp01(today_activity.active_minutes / 120)

    # Combined strain score (0-100)
    strain = round(100 * clamp01(steps_norm + hr_norm + activity_norm))

    return min(100, max(0, strain))


def _calculate_bedtime_consistency(user_id: str) -> float:
    """Calculate bedtime consistency score based on 7-day variance."""
    recent_sleep = SLEEP.get(user_id, [])[-7:]  # Last week

    bedtime_minutes = []
    for sleep_entry in recent_sleep:
        try:
            hour, minute = map(int, sleep_entry.bedtime.split(":"))
            bedtime_minutes.append(hour * 60 + minute)
        except (ValueError, AttributeError):
            continue  # Skip invalid bedtime formats

    if len(bedtime_minutes) < 2:
        return 0.5  # Neutral score with insufficient data

    # Lower variance = better consistency
    bedtime_variance = np.std(bedtime_minutes)
    consistency_score = clamp01(1 - bedtime_variance / 120.0)  # 2-hour threshold

    return consistency_score


def _calculate_recovery_factor(user_id: str) -> float:
    """Calculate recovery factor based on recent activity vs. today's steps."""
    activity_data = ACTIVITY.get(user_id, [])

    if len(activity_data) < 2:
        return 0.5  # Neutral recovery factor

    today_steps = activity_data[-1].steps
    recent_steps = [a.steps for a in activity_data[-7:]]  # Last week

    steps_mean, steps_std = mean_std(recent_steps)

    # Calculate how much above/below average today is
    if steps_std > 0:
        strain_z_score = (today_steps - steps_mean) / steps_std
        recovery_factor = clamp01(
            1 - strain_z_score / 2.0
        )  # Higher strain = lower recovery
    else:
        recovery_factor = 0.5  # Neutral if no variance

    return recovery_factor


# Global contextual bandit instances
BANDITS: Dict[Tuple[str, str], MAB] = {}


def _get_state_context(state: Dict[str, int]) -> List[float]:
    """Convert state dict to context vector for bandit."""
    return [
        state["Readiness"] / 100.0,  # Normalize to 0-1
        state["Fuel"] / 100.0,
        state["Strain"] / 100.0,
    ]


def _get_or_create_bandit(user_id: str, domain: str) -> MAB:
    """Get or create a contextual bandit for user and domain."""
    key = (user_id, domain)
    if key not in BANDITS:
        arms = list(ARMS[domain].keys())
        # Use Thompson Sampling with contextual features
        BANDITS[key] = MAB(
            arms=arms,
            learning_policy=LearningPolicy.ThompsonSampling(),
            neighborhood_policy=NeighborhoodPolicy.KNearest(k=3),
        )
    return BANDITS[key]


def thompson_sample_contextual(user_id: str, domain: str, state: Dict[str, int]) -> str:
    """Thompson sampling with state context using MABWiser."""
    bandit = _get_or_create_bandit(user_id, domain)
    context = _get_state_context(state)

    try:
        # If bandit has been trained, predict with context
        arm = bandit.predict([context])[0]
    except:
        # If not trained yet, randomly select an arm
        arms = list(ARMS[domain].keys())
        arm = random.choice(arms)

    return arm


# Candidate filtering and ranking
def filter_music_candidates(
    user: UserProfile, state: Dict[str, int], arm_id: str
) -> List[MusicTrack]:
    """Filter music candidates based on user state and arm."""
    cap = energy_cap_from_state(state)
    bpm_tgt = target_bpm_from_state(user, state)
    pool = [
        m
        for m in MUSIC
        if m.energy <= min(cap, ARMS["music"][arm_id]["energy_cap"])
        and any(g in m.genres for g in ARMS["music"][arm_id]["genres"])
        and abs(m.bpm - bpm_tgt) <= 15
    ]
    if not pool:
        pool = [m for m in MUSIC if m.energy <= cap and abs(m.bpm - bpm_tgt) <= 20]
    return pool or MUSIC  # fallback


def filter_meal_candidates(
    user: UserProfile, state: Dict[str, int], arm_id: str
) -> List[MealTemplate]:
    """Filter meal candidates based on user constraints."""
    cands = []
    for meal in MEALS:
        if risk_penalties_meal(meal, user) >= 1.0:  # skip hard violations
            continue
        cands.append(meal)
    return cands


def filter_workout_candidates(
    user: UserProfile, state: Dict[str, int], arm_id: str
) -> List[WorkoutTemplate]:
    """Filter workout candidates based on user state and equipment."""
    cap_zone = zone_from_state(state)
    allowed = []
    for w in WORKOUTS:
        # zone ordering
        order = {"Z2_low": 0, "Z2": 1, "Tempo": 2}
        if order[w.intensity_zone] > order[cap_zone]:
            continue
        if any(eq not in user.equipment for eq in w.equipment_needed):
            continue
        allowed.append(w)
    if not allowed:
        # fallback ignore equipment
        allowed = [
            w
            for w in WORKOUTS
            if (
                {"Z2_low": 0, "Z2": 1, "Tempo": 2}[w.intensity_zone]
                <= {"Z2_low": 0, "Z2": 1, "Tempo": 2}[cap_zone]
            )
        ]
    return allowed


def rank_music(
    cands: List[MusicTrack], user: UserProfile, state: Dict[str, int]
) -> List[Tuple[MusicTrack, float]]:
    """Rank music candidates by preference and state fit."""
    results = []
    for m in cands:
        PrefFit = cosine_pref_fit(user.pref_music_genres, m.genres)
        # StateFit: BPM closeness + energy within cap
        bpm_tgt = target_bpm_from_state(user, state)
        bpm_fit = 1.0 - min(1.0, abs(m.bpm - bpm_tgt) / 30.0)
        energy_fit = 1.0 - max(0.0, m.energy - energy_cap_from_state(state)) * 2.0
        StateFit = clamp01(0.7 * bpm_fit + 0.3 * energy_fit)
        GoalFit = 1.0  # music's goal is to support session; we encode via StateFit
        score = (
            0.35 * GoalFit
            + 0.30 * StateFit
            + 0.25 * PrefFit
            + 0.10 * novelty_bonus(m.id, "music")
        )
        results.append((m, score))
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def rank_meals(
    cands: List[MealTemplate], user: UserProfile, state: Dict[str, int]
) -> List[Tuple[MealTemplate, float]]:
    """Rank meal candidates by nutritional needs and preferences."""
    # Compute macro gaps from today's totals
    today = get_today_iso(None)
    todays = next(
        (n for n in reversed(NUTRITION.get(user.user_id, [])) if n.date <= today), None
    )
    P_now, fiber_now, sugar_now, sodium_now = (
        (todays.protein_g, todays.fiber_g, todays.sugar_g, todays.sodium_mg)
        if todays
        else (0, 0, 0, 0)
    )
    P_target = (1.4 if user.goals == "endurance" else 1.2) * user.weight
    gaps = {
        "protein": max(0.0, P_target - P_now),
        "fiber": max(0.0, 30.0 - fiber_now),
        "sugar_room": max(0.0, 75.0 - sugar_now),
        "sodium_room": max(0.0, 2300.0 - sodium_now),
    }
    results = []
    for meal in cands:
        Risk = risk_penalties_meal(meal, user)
        if Risk >= 1.0:
            continue
        PrefFit = cosine_pref_fit(user.pref_meal_cuisines, meal.cuisine_tags)
        protein_fill = (
            min(1.0, meal.protein_g / (gaps["protein"] + 1e-6))
            if gaps["protein"] > 0
            else 0.5
        )
        fiber_fill = (
            min(1.0, meal.fiber_g / (gaps["fiber"] + 1e-6))
            if gaps["fiber"] > 0
            else 0.4
        )
        sugar_ok = 1.0 if meal.sugar_g <= gaps["sugar_room"] else 0.2
        sodium_ok = 1.0 if meal.sodium_mg <= gaps["sodium_room"] else 0.3
        GoalFit = clamp01(
            0.6 * protein_fill + 0.2 * fiber_fill + 0.1 * sugar_ok + 0.1 * sodium_ok
        )
        StateFit = 1.0 if state["Fuel"] < 60 else 0.7
        score = (
            0.35 * GoalFit
            + 0.30 * StateFit
            + 0.25 * PrefFit
            + 0.10 * novelty_bonus(meal.id, "meal")
        )
        results.append((meal, score))
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def rank_workouts(
    cands: List[WorkoutTemplate], user: UserProfile, state: Dict[str, int]
) -> List[Tuple[WorkoutTemplate, float]]:
    """Rank workout candidates by user goals and current state."""
    results = []
    for w in cands:
        Risk = risk_penalties_workout(w, user, state)
        if Risk >= 1.0:
            continue
        PrefFit = cosine_pref_fit(user.pref_workout_focus, w.focus_tags)
        StateFit = 1.0 if zone_from_state(state) >= w.intensity_zone else 0.7
        GoalFit = (
            1.0 if ("endurance" in w.focus_tags and user.goals == "endurance") else 0.7
        )
        score = (
            0.35 * GoalFit
            + 0.30 * StateFit
            + 0.25 * PrefFit
            + 0.10 * novelty_bonus(w.id, "workout")
            - 0.25 * Risk
        )
        results.append((w, score))
    results.sort(key=lambda x: x[1], reverse=True)
    return results


def choose_domain(
    intent: Optional[str], state: Dict[str, int], hours_since_last_meal: Optional[float]
) -> str:
    """Choose recommendation domain based on intent and state."""
    if intent in {"music", "meal", "workout"}:
        return intent
    if state["Fuel"] < 50 and (hours_since_last_meal or 0) >= 3:
        return "meal"
    if state["Readiness"] >= 50 and state["Strain"] < 70:
        return "workout"
    return "music"


def reward_from_feedback(domain: str, fb: Feedback) -> float:
    """Calculate reward from user feedback."""
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


def update_bandit(
    user_id: str,
    domain: str,
    arm_id: str,
    r: float,
    state: Optional[Dict[str, int]] = None,
):
    """Update bandit arm based on reward with optional state context."""
    bandit = _get_or_create_bandit(user_id, domain)

    if state is not None:
        context = _get_state_context(state)
        # Train the bandit with context, chosen arm, and reward
        bandit.partial_fit(decisions=[arm_id], rewards=[r], contexts=[context])
    else:
        # Fallback: train without context (less effective)
        bandit.partial_fit(decisions=[arm_id], rewards=[r])


def update_preferences(
    user: UserProfile, domain: str, item_tags: List[str], thumbs: int
):
    """Update user preferences based on feedback."""
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


def generate_recommendation_explanation(
    user: UserProfile,
    domain: str,
    recommendation_item: Dict,
    state: Dict[str, int],
    sleep_entries: List[SleepEntry],
    todays_nutrition: Optional[NutritionEntry],
    activity_entries: List[ActivityEntry],
) -> str:
    """Generate a personalized explanation for the recommendation using OpenAI.

    Prompt construction delegated to prompts.build_explanation_prompt for maintainability.
    Falls back gracefully if API unavailable or errors occur.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return (
            f"This {domain} aligns with your current state and {user.goals} goal focus."
        )

    # Prepare lightweight context strings
    sleep_context = ""
    if sleep_entries:
        last = sleep_entries[-1]
        sleep_hours = last.sleep_duration_minutes / 60
        sleep_context = (
            f"Sleep {sleep_hours:.1f}h @ {last.sleep_efficiency:.0f}% efficiency"
        )

    nutrition_context = ""
    if todays_nutrition:
        nutrition_context = f"Intake {todays_nutrition.calories_consumed} kcal / {todays_nutrition.protein_g:.0f}g protein"

    activity_context = ""
    if activity_entries:
        last_a = activity_entries[-1]
        activity_context = (
            f"Activity {last_a.steps} steps / {last_a.active_minutes} active min"
        )

    user_prompt = build_explanation_prompt(
        domain=domain,
        user=user,
        state=state,
        item=recommendation_item,
        sleep_context=sleep_context,
        nutrition_context=nutrition_context,
        activity_context=activity_context,
    )

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_EXPLANATION},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=80,
            temperature=0.7,
        )
        msg = response.choices[0].message.content.strip()
        # Safety: enforce word & length cap client-side as backup
        words = msg.split()
        if len(words) > 45:
            msg = " ".join(words[:45])
        return msg
    except Exception as e:  # Broad catch acceptable for outer fallback layer
        print(f"❌ LLM explanation error: {e}")
        return (
            f"Optimized for your current Readiness/Fuel/Strain to support {user.goals}."
        )
