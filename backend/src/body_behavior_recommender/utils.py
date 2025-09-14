"""Utility functions for the Body-to-Behavior Recommender."""

import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import numpy as np

from .models import (
    MealTemplate,
    UserProfile,
    WorkoutTemplate,
)


def clamp01(x: float) -> float:
    """Clamp a value between 0 and 1."""
    return max(0.0, min(1.0, x))


def normalize01(x: float, lo: float, hi: float) -> float:
    """Normalize a value to 0-1 range."""
    if hi <= lo:
        return 0.0
    return clamp01((x - lo) / (hi - lo))


def mean_std(values: List[float]) -> Tuple[float, float]:
    """Calculate mean and standard deviation of values."""
    if not values:
        return 0.0, 1.0
    mu = float(np.mean(values))
    sigma = float(np.std(values)) or 1.0
    return mu, sigma


def get_today_iso(now_iso: Optional[str]) -> str:
    """Get today's date in ISO format."""
    if now_iso:
        return now_iso[:10]
    return datetime.utcnow().strftime("%Y-%m-%d")


def compute_hr_max(user: UserProfile) -> int:
    """Calculate maximum heart rate for a user."""
    return user.hr_max_override or int(208 - 0.7 * user.age)


def energy_cap_from_state(state: Dict[str, int]) -> float:
    """Determine energy cap based on user state."""
    if state["Readiness"] < 40 or state["Strain"] > 70:
        return 0.6
    if state["Readiness"] < 60:
        return 0.75
    return 0.85


def target_bpm_from_state(user: UserProfile, state: Dict[str, int]) -> int:
    """Calculate target BPM based on user state."""
    hrmax = compute_hr_max(user)
    if state["Readiness"] >= 60 and state["Strain"] < 60:
        target_hr = 0.65 * hrmax
    else:
        target_hr = 0.55 * hrmax
    bpm = int(np.clip((target_hr / hrmax) * 180.0, 90, 180))
    return bpm


def cosine_pref_fit(tag_weights: Dict[str, float], item_tags: List[str]) -> float:
    """Calculate preference fit using cosine similarity."""
    if not item_tags:
        return 0.0
    # simple average of normalized tag weights
    if not tag_weights:
        return 0.0
    vals = [tag_weights.get(t, 0.0) for t in item_tags]
    return clamp01(float(np.mean(vals)))


def novelty_bonus(item_id: str, domain: str) -> float:
    """Calculate novelty bonus for an item."""
    # Placeholder: random small bonus. You can track exposures in EVENTS for real novelty.
    return random.uniform(0.0, 0.1)


def repetition_penalty(item_id: str, domain: str) -> float:
    """Calculate repetition penalty for an item."""
    return 0.0


def risk_penalties_meal(meal: MealTemplate, user: UserProfile) -> float:
    """Calculate risk penalties for a meal."""
    # 1.0 if hard violation (block later), smaller otherwise
    if any(a in user.allergens for a in meal.allergens):
        return 1.0
    if user.diet_flags and not any(flag in meal.diet_ok for flag in user.diet_flags):
        return 1.0
    return 0.0


def risk_penalties_workout(
    w: WorkoutTemplate, user: UserProfile, state: Dict[str, int]
) -> float:
    """Calculate risk penalties for a workout."""
    # Cap high intensity on low readiness/high strain
    if state["Readiness"] < 40 and w.intensity_zone == "Tempo":
        return 0.8
    return 0.0


def zone_from_state(state: Dict[str, int]) -> str:
    """Determine appropriate workout zone from user state."""
    if state["Readiness"] < 40 or state["Strain"] >= 70:
        return "Z2_low"
    if state["Readiness"] < 60:
        return "Z2"
    return "Tempo"
