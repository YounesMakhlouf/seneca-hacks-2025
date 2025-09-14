"""Data models for the Body-to-Behavior Recommender API."""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class SleepEntry(BaseModel):
    user_id: str
    date: str  # YYYY-MM-DD
    sleep_duration_minutes: int
    deep_sleep_minutes: int
    rem_sleep_minutes: int
    light_sleep_minutes: int
    sleep_efficiency: float
    bedtime: str
    wake_time: str


class NutritionEntry(BaseModel):
    user_id: str
    date: str
    calories_consumed: int
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    sugar_g: float
    sodium_mg: float


class ActivityEntry(BaseModel):
    user_id: str
    date: str
    steps: int
    calories_burned: int
    active_minutes: int
    distance_km: float
    heart_rate_avg: int
    workout_duration: int  # minutes


class MeasurementEntry(BaseModel):
    measurement_id: str
    user_id: str
    date: str
    weight: float
    body_fat: float
    muscle_mass: float
    bmi: float
    waist: float
    chest: float
    bicep: float
    thigh: float
    body_water: float
    bone_mass: float
    notes: Optional[str] = None


class UserProfile(BaseModel):
    user_id: str
    age: int
    weight: float
    height: float
    bmi: float
    fitness_level: str
    goals: str
    join_date: str
    # Preferences (very lightweight)
    pref_music_genres: Dict[str, float] = Field(default_factory=dict)  # genre -> weight
    pref_meal_cuisines: Dict[str, float] = Field(default_factory=dict)
    pref_workout_focus: Dict[str, float] = Field(default_factory=dict)
    hr_max_override: Optional[int] = None
    allergens: List[str] = Field(default_factory=list)
    diet_flags: List[str] = Field(default_factory=list)
    equipment: List[str] = Field(default_factory=list)


# Catalog items
class MusicTrack(BaseModel):
    id: str
    title: str
    artist: str
    bpm: int
    energy: float  # 0..1
    valence: float # 0..1
    genres: List[str]


class MealTemplate(BaseModel):
    id: str
    name: str
    cuisine_tags: List[str]
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    sugar_g: float
    sodium_mg: float
    allergens: List[str] = Field(default_factory=list)
    diet_ok: List[str] = Field(default_factory=list)  # e.g., ["omnivore","vegetarian","low-carb"]


class WorkoutTemplate(BaseModel):
    id: str
    name: str
    intensity_zone: str  # "Z2_low","Z2","Tempo"
    impact: str          # "low","moderate","high"
    equipment_needed: List[str]
    duration_min: int
    focus_tags: List[str]  # ["endurance","mobility","strength"]


# Request/response DTOs
class RecommendRequest(BaseModel):
    user_id: str
    intent: Optional[str] = Field(default=None, description="music|meal|workout|auto")
    now: Optional[str] = None  # ISO; defaults to now()
    current_hr: Optional[int] = None
    rpe: Optional[float] = None
    hours_since_last_meal: Optional[float] = None


class RecommendResponse(BaseModel):
    domain: str
    state: Dict[str, int]
    item: Dict
    bandit_arm: str


class Feedback(BaseModel):
    user_id: str
    domain: str  # music|meal|workout
    item_id: str
    thumbs: int = 0            # -1,0,1
    completed: Optional[int] = None  # 0/1
    hr_zone_frac: Optional[float] = None  # 0..1
    rpe: Optional[float] = None
    ate: Optional[int] = None      # 0/1
    protein_gap_closed_norm: Optional[float] = None  # 0..1
    skipped_early: Optional[int] = None  # 0/1