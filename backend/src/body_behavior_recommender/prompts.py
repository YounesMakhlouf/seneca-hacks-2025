"""Prompt templates and builders for LLM interactions.

Separation keeps services logic focused on data & orchestration while prompts
remain centralized and easy to iterate during hackathon.
"""

from __future__ import annotations

from typing import Dict

from .models import UserProfile

SYSTEM_PROMPT_EXPLANATION = (
    "You are a supportive fitness + wellness coach. Generate concise (<=40 words), "
    "empowering, trustworthy 1–2 sentence explanations that reference the user's current "
    "state (Readiness/Fuel/Strain) and recent data. Tone: positive, specific, encouraging, "
    "never judgmental. Avoid exaggeration and avoid repeating raw numbers more than once."
)


def _line_if(content: str) -> str:
    return f"- {content}\n" if content else ""


def build_explanation_prompt(
    *,
    domain: str,
    user: UserProfile,
    state: Dict[str, int],
    item: Dict,
    sleep_context: str = "",
    nutrition_context: str = "",
    activity_context: str = "",
) -> str:
    """Construct a domain‑specific user prompt for the explanation LLM call.

    Parameters
    ----------
    domain : str
        One of music|meal|workout.
    user : UserProfile
        The user profile (for goals & personalization).
    state : dict
        Computed state with Readiness/Fuel/Strain.
    item : dict
        The recommended catalog item serialized via model_dump().
    *_context : str
        Pre-formatted short context blurbs (may be empty strings).
    """
    base_header = (
        "Create a brief empowering 1–2 sentence explanation for why this {} is recommended. "
        "Use <=40 words. Reference 1–2 relevant recent signals (sleep, activity, nutrition) and the user's goal. "
        "Make it motivating, specific, and confidence-building."
    )

    if domain == "music":
        body = (
            f'Track: "{item.get("title", "Unknown")}" by {item.get("artist", "Unknown")}\n'
            f"BPM: {item.get('bpm', '?')}  Energy: {item.get('energy', 0):.2f}\n"
        )
    elif domain == "meal":
        body = (
            f"Meal: {item.get('name', 'Unknown')}  Calories: {item.get('calories', '?')}  "
            f"Protein: {item.get('protein_g', '?')}g  Fiber: {item.get('fiber_g', '?')}g\n"
        )
    else:  # workout
        body = (
            f"Workout: {item.get('name', 'Unknown')}  Duration: {item.get('duration_min', '?')} min  "
            f"Intensity: {item.get('intensity_zone', '?')}\n"
        )

    ctx = (
        "User Context:\n"
        f"- Goal: {user.goals}\n"
        f"- State: R {state['Readiness']}/100 | F {state['Fuel']}/100 | S {state['Strain']}/100\n"
        f"{_line_if(sleep_context)}{_line_if(nutrition_context)}{_line_if(activity_context)}"
    )

    guidance = (
        """Rules:
        - Do NOT exceed 40 words.
        - Use second person ("you").
        - Include exactly one motivational verb (e.g., boost, sustain, support, enhance).
        - Avoid filler like 'This recommendation is'. Start directly with value.
        - If numbers already listed above, reference them qualitatively (e.g., 'solid sleep', 'moderate strain').
        """.strip()
        + "\n"
    )

    return f"{base_header.format(domain)}\n\n{body}\n{ctx}\n{guidance}"
