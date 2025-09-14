"""API endpoints for the Body-to-Behavior Recommender."""

from fastapi import HTTPException
from .db import get_user as db_get_user, get_recent_entries

from .models import RecommendRequest, RecommendResponse, Feedback
from .services import (
    compute_state, compute_state_entries, choose_domain, thompson_sample_contextual,
    filter_music_candidates, filter_meal_candidates, filter_workout_candidates,
    rank_music, rank_meals, rank_workouts,
    reward_from_feedback, update_bandit, update_preferences
)
from .utils import get_today_iso
from .app import app, MUSIC, MEALS, WORKOUTS
from .data_loader import data_loader


@app.get("/")
def read_root():
    """Root endpoint with API information."""
    return {
        "name": "Body-to-Behavior Recommender API",
        "version": "0.1.0",
        "description": "AI-powered contextual recommendations for music, meals, and workouts"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/state")
def get_state(user_id: str):
    """Get user's current state (Readiness, Fuel, Strain)."""
    doc = db_get_user(user_id)
    if not doc:
        raise HTTPException(404, "user not found")
    from .models import UserProfile
    user = UserProfile(**doc)

    today = get_today_iso(None)
    sleep_docs = get_recent_entries("sleep", user_id, limit=7)
    nut_docs = get_recent_entries("nutrition", user_id, limit=3)
    act_docs = get_recent_entries("activity", user_id, limit=7)
    from .models import SleepEntry, NutritionEntry, ActivityEntry
    sleep_entries = [SleepEntry(**d) for d in sleep_docs]
    todays_nutrition = None
    if nut_docs:
        for d in reversed(nut_docs):
            if d["date"] <= today:
                todays_nutrition = NutritionEntry(**d)
                break
    activity_entries = [ActivityEntry(**d) for d in act_docs]
    state = compute_state_entries(user, sleep_entries, todays_nutrition, activity_entries)
    return {"user_id": user_id, "date": today, "state": state}


@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    """Get personalized recommendations for music, meals, or workouts."""
    doc = db_get_user(req.user_id)
    if not doc:
        raise HTTPException(404, "user not found")
    from .models import UserProfile
    user = UserProfile(**doc)

    today = get_today_iso(req.now)
    sleep_docs = get_recent_entries("sleep", req.user_id, limit=7)
    nut_docs = get_recent_entries("nutrition", req.user_id, limit=3)
    act_docs = get_recent_entries("activity", req.user_id, limit=7)
    from .models import SleepEntry, NutritionEntry, ActivityEntry
    sleep_entries = [SleepEntry(**d) for d in sleep_docs]
    todays_nutrition = None
    if nut_docs:
        for d in reversed(nut_docs):
            if d["date"] <= today:
                todays_nutrition = NutritionEntry(**d)
                break
    activity_entries = [ActivityEntry(**d) for d in act_docs]
    state = compute_state_entries(user, sleep_entries, todays_nutrition, activity_entries)
    domain = choose_domain(req.intent, state, req.hours_since_last_meal)
    arm = thompson_sample_contextual(req.user_id, domain, state)

    if domain == "music":
        candidates = filter_music_candidates(user, state, arm)
        ranked = rank_music(candidates, user, state)
        if not ranked:
            raise HTTPException(400, "no music candidates")
        item = ranked[0][0]
        payload = item.model_dump()
    elif domain == "meal":
        candidates = filter_meal_candidates(user, state, arm)
        ranked = rank_meals(candidates, user, state)
        if not ranked:
            raise HTTPException(400, "no meal candidates")
        item = ranked[0][0]
        payload = item.model_dump()
    else:  # workout
        candidates = filter_workout_candidates(user, state, arm)
        ranked = rank_workouts(candidates, user, state)
        if not ranked:
            raise HTTPException(400, "no workout candidates")
        item = ranked[0][0]
        payload = item.model_dump()

    return RecommendResponse(domain=domain, state=state, item=payload, bandit_arm=arm)


@app.post("/feedback")
def submit_feedback(fb: Feedback):
    """Submit feedback on a recommendation."""
    doc = db_get_user(fb.user_id)
    if not doc:
        raise HTTPException(404, "user not found")
    from .models import UserProfile
    user = UserProfile(**doc)

    # Infer arm by a simple mapping: pick the arm whose filter would have included the item
    # For hackathon speed, assume last chosen arm per domain is the one to update (not tracked here).
    # Better: return arm from /recommend and send it back in feedback. For now, do this:
    # Get current state to make contextual decision
    today = get_today_iso(None)
    sleep_docs = get_recent_entries("sleep", fb.user_id, limit=7)
    nut_docs = get_recent_entries("nutrition", fb.user_id, limit=3)
    act_docs = get_recent_entries("activity", fb.user_id, limit=7)
    from .models import SleepEntry, NutritionEntry, ActivityEntry
    sleep_entries = [SleepEntry(**d) for d in sleep_docs]
    todays_nutrition = None
    if nut_docs:
        for d in reversed(nut_docs):
            if d["date"] <= today:
                todays_nutrition = NutritionEntry(**d)
                break
    activity_entries = [ActivityEntry(**d) for d in act_docs]
    state = compute_state_entries(user, sleep_entries, todays_nutrition, activity_entries)
    arm_to_update = thompson_sample_contextual(fb.user_id, fb.domain, state)
    r = reward_from_feedback(fb.domain, fb)
    update_bandit(fb.user_id, fb.domain, arm_to_update, r, state)

    # Update prefs
    item_tags = []
    if fb.domain == "music":
        track = next((m for m in MUSIC if m.id == fb.item_id), None)
        item_tags = (track.genres if track else [])
    elif fb.domain == "meal":
        meal = next((m for m in MEALS if m.id == fb.item_id), None)
        item_tags = (meal.cuisine_tags if meal else [])
    else:
        workout = next((w for w in WORKOUTS if w.id == fb.item_id), None)
        item_tags = (workout.focus_tags if workout else [])

    update_preferences(user, fb.domain, item_tags, fb.thumbs)
    return {"ok": True, "reward": r, "arm_updated": arm_to_update}


@app.get("/users/{user_id}")
def get_user(user_id: str):
    """Get user profile information."""
    doc = db_get_user(user_id)
    if not doc:
        raise HTTPException(404, "user not found")
    return doc


@app.get("/catalog/music")
def get_music_catalog():
    """Get the music catalog."""
    return {"tracks": MUSIC}


@app.get("/catalog/meals")
def get_meal_catalog():
    """Get the meal catalog."""
    return {"meals": MEALS}


@app.get("/catalog/workouts")
def get_workout_catalog():
    """Get the workout catalog."""
    return {"workouts": WORKOUTS}


@app.get("/data-summary")
def get_data_summary():
    """Get a summary of loaded data."""
    from .db import collection_count
    return {
        "users": collection_count("users"),
        "sleep_datasets": collection_count("sleep"),
        "nutrition_datasets": collection_count("nutrition"),
        "activity_datasets": collection_count("activity"),
        "measurement_datasets": collection_count("measurements"),
        "total_sleep_entries": collection_count("sleep"),
        "total_nutrition_entries": collection_count("nutrition"),
        "total_activity_entries": collection_count("activity"),
        "total_measurement_entries": collection_count("measurements"),
        "music_tracks": len(MUSIC),
        "meal_templates": len(MEALS),
        "workout_templates": len(WORKOUTS),
        "sample_user_ids": [],  # Would need separate query to get sample IDs from MongoDB
        "data_sources": {
            "enhanced": True,
            "available_datasets": ["users", "sleep", "nutrition", "activities", "measurements"],
            "storage": "mongodb"
        }
    }


@app.get("/users/{user_id}/summary")
def get_user_summary(user_id: str):
    """Get detailed summary for a specific user."""
    summary = data_loader.get_user_summary(user_id)
    if "error" in summary:
        raise HTTPException(status_code=404, detail=summary["error"])
    return summary


@app.get("/users/{user_id}/recent")
def get_user_recent_data(user_id: str, days: int = 7):
    """Get recent data for a user."""
    recent_data = data_loader.get_recent_data(user_id, days)
    if "error" in recent_data:
        raise HTTPException(status_code=404, detail=recent_data["error"])
    return recent_data


@app.get("/users/{user_id}/measurements")
def get_user_measurements_endpoint(user_id: str, limit: int = 10):
    """Get body measurements for a user."""
    from .db import get_user_measurements
    measurements = get_user_measurements(user_id, limit)
    if not measurements:
        raise HTTPException(status_code=404, detail="User not found or no measurements available")
    return {
        "user_id": user_id,
        "total_measurements": len(measurements),
        "recent_measurements": measurements,
        "latest_measurement": measurements[0] if measurements else None
    }