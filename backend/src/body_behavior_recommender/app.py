"""Main FastAPI application for the Body-to-Behavior Recommender."""

import asyncio
from typing import List

from fastapi import FastAPI

from .data_loader import data_loader
from .db import collection_count, insert_many
from .models import (
    MealTemplate,
    MusicTrack,
    WorkoutTemplate,
)

app = FastAPI(title="Body-to-Behavior Recommender", version="0.1.0")

# -----------------------------
# Static catalogs (in-memory for fast access)
# -----------------------------
MUSIC: List[MusicTrack] = []
MEALS: List[MealTemplate] = []
WORKOUTS: List[WorkoutTemplate] = []

ARMS = {
    "music": {
        "lofi_low": {"genres": ["lofi", "chillhop"], "energy_cap": 0.55},
        "synth_mid": {"genres": ["synthwave", "edm"], "energy_cap": 0.75},
        "pop_up": {"genres": ["pop"], "energy_cap": 0.85},
    },
    "meal": {
        "shake": {"tags": ["quick-high-protein"]},
        "bowl": {"tags": ["protein-fiber-bowl"]},
        "wrap": {"tags": ["handheld", "high-protein"]},
    },
    "workout": {
        "z2_walk": {"zone": "Z2_low"},
        "z2_cycle": {"zone": "Z2"},
        "tempo_intervals": {"zone": "Tempo"},
        "mobility": {"zone": "Z2_low"},
    },
}


def seed_data():
    """Initialize catalog data only - user data comes from MongoDB."""
    # Music catalog
    MUSIC.extend(
        [
            MusicTrack(
                id="m1",
                title="Late Night Study",
                artist="BeatLoop",
                bpm=105,
                energy=0.45,
                valence=0.5,
                genres=["lofi"],
            ),
            MusicTrack(
                id="m2",
                title="Window Rain",
                artist="LoKey",
                bpm=112,
                energy=0.48,
                valence=0.4,
                genres=["lofi", "chillhop"],
            ),
            MusicTrack(
                id="m3",
                title="Neon Drive",
                artist="Pulse 84",
                bpm=128,
                energy=0.70,
                valence=0.6,
                genres=["synthwave"],
            ),
            MusicTrack(
                id="m4",
                title="Sunset Run",
                artist="Dynawave",
                bpm=138,
                energy=0.78,
                valence=0.7,
                genres=["synthwave", "edm"],
            ),
            MusicTrack(
                id="m5",
                title="Top Vibes",
                artist="Nova",
                bpm=120,
                energy=0.65,
                valence=0.8,
                genres=["pop"],
            ),
        ]
    )
    # Meal templates
    MEALS.extend(
        [
            MealTemplate(
                id="meal1",
                name="Greek Yogurt + Whey + Chia",
                cuisine_tags=["mediterranean"],
                calories=350,
                protein_g=35,
                carbs_g=30,
                fat_g=10,
                fiber_g=8,
                sugar_g=12,
                sodium_mg=180,
                allergens=["dairy"],
                diet_ok=["omnivore", "vegetarian"],
            ),
            MealTemplate(
                id="meal2",
                name="Lentil-Tuna Bowl",
                cuisine_tags=["mediterranean"],
                calories=600,
                protein_g=50,
                carbs_g=55,
                fat_g=18,
                fiber_g=14,
                sugar_g=6,
                sodium_mg=520,
                allergens=["fish"],
                diet_ok=["omnivore"],
            ),
            MealTemplate(
                id="meal3",
                name="Chicken Wrap",
                cuisine_tags=["mexican"],
                calories=550,
                protein_g=42,
                carbs_g=50,
                fat_g=18,
                fiber_g=9,
                sugar_g=7,
                sodium_mg=680,
                allergens=["gluten"],
                diet_ok=["omnivore"],
            ),
        ]
    )
    # Workouts
    WORKOUTS.extend(
        [
            WorkoutTemplate(
                id="w1",
                name="Zone-2 Walk",
                intensity_zone="Z2_low",
                impact="low",
                equipment_needed=["shoes"],
                duration_min=30,
                focus_tags=["endurance"],
            ),
            WorkoutTemplate(
                id="w2",
                name="Zone-2 Bike",
                intensity_zone="Z2",
                impact="low",
                equipment_needed=["stationary_bike"],
                duration_min=30,
                focus_tags=["endurance"],
            ),
            WorkoutTemplate(
                id="w3",
                name="Tempo Intervals 4x4",
                intensity_zone="Tempo",
                impact="moderate",
                equipment_needed=["shoes"],
                duration_min=28,
                focus_tags=["endurance"],
            ),
            WorkoutTemplate(
                id="w4",
                name="Mobility Flow 15",
                intensity_zone="Z2_low",
                impact="low",
                equipment_needed=["yoga_mat"],
                duration_min=15,
                focus_tags=["mobility"],
            ),
        ]
    )


async def _maybe_seed_mongo():
    """Seed MongoDB with JSON data if empty."""
    if collection_count("users") == 0:
        # Attempt one-time JSON ingestion for seeding only when empty
        print("📦 Mongo empty → ingesting JSON once for seed...")
        # Load data from JSON files for seeding
        if data_loader.load_all_data():
            user_docs = [u.model_dump() for u in data_loader.users.values()]
            sleep_docs = [
                s.model_dump() for arr in data_loader.sleep.values() for s in arr
            ]
            nutrition_docs = [
                n.model_dump() for arr in data_loader.nutrition.values() for n in arr
            ]
            activity_docs = [
                a.model_dump() for arr in data_loader.activity.values() for a in arr
            ]
            measurement_docs = [
                m for arr in data_loader.measurements.values() for m in arr
            ]
            insert_many("users", user_docs)
            insert_many("sleep", sleep_docs)
            insert_many("nutrition", nutrition_docs)
            insert_many("activity", activity_docs)
            insert_many("measurements", measurement_docs)
            print("✅ Mongo seed complete")
        else:
            print("⚠️ Seed skipped: JSON ingestion failed")


# Initialize data on startup (sync part)
seed_data()

# Trigger async seeding task for MongoDB
asyncio.get_event_loop().create_task(_maybe_seed_mongo())

from . import endpoints