"""Feedback processing business logic."""

import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class FeedbackProcessor:
    """Processes feedback messages with the same logic as the sync endpoint."""
    
    def __init__(self):
        self.mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://bbr:bbrpass@mongo:27017/?directConnection=true')
        self.db_name = os.getenv('BBR_DB_NAME', 'bbr')
        
        # Will be initialized in initialize()
        self.db_client = None
        self.bandits = {}  # In-memory bandit storage
        
        self.MUSIC = []
        self.MEALS = []
        self.WORKOUTS = []
        
        logger.info("🔧 Feedback processor initialized")
    
    async def initialize(self):
        """Initialize database connections and load catalogs."""
        try:
            # Initialize MongoDB connection
            await self._init_database()
            
            # Load static catalogs
            await self._load_catalogs()
            
            logger.info("✅ Feedback processor ready")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize processor: {e}")
            raise
    
    async def _init_database(self):
        """Initialize MongoDB connection."""
        from pymongo import MongoClient
        
        try:
            self.db_client = MongoClient(self.mongodb_uri)
            # Test connection
            self.db_client.admin.command('ping')
            logger.info(f"✅ Connected to MongoDB: {self.db_name}")
            
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            raise
    
    async def _load_catalogs(self):
        """Load static catalogs."""
        from shared.models import MusicTrack, MealTemplate, WorkoutTemplate
        
        # Music catalog
        self.MUSIC = [
            MusicTrack(id="m1", title="Late Night Study", artist="BeatLoop", bpm=105, energy=0.45, valence=0.5, genres=["lofi"]),
            MusicTrack(id="m2", title="Window Rain", artist="LoKey", bpm=112, energy=0.48, valence=0.4, genres=["lofi","chillhop"]),
            MusicTrack(id="m3", title="Neon Drive", artist="Pulse 84", bpm=128, energy=0.70, valence=0.6, genres=["synthwave"]),
            MusicTrack(id="m4", title="Sunset Run", artist="Dynawave", bpm=138, energy=0.78, valence=0.7, genres=["synthwave","edm"]),
            MusicTrack(id="m5", title="Top Vibes", artist="Nova", bpm=120, energy=0.65, valence=0.8, genres=["pop"]),
        ]
        
        # Meal templates
        self.MEALS = [
            MealTemplate(id="meal1", name="Greek Yogurt + Whey + Chia", cuisine_tags=["mediterranean"], calories=350, protein_g=35, carbs_g=30, fat_g=10, fiber_g=8, sugar_g=12, sodium_mg=180, allergens=["dairy"], diet_ok=["omnivore","vegetarian"]),
            MealTemplate(id="meal2", name="Lentil-Tuna Bowl", cuisine_tags=["mediterranean"], calories=600, protein_g=50, carbs_g=55, fat_g=18, fiber_g=14, sugar_g=6, sodium_mg=520, allergens=["fish"], diet_ok=["omnivore"]),
            MealTemplate(id="meal3", name="Chicken Wrap", cuisine_tags=["mexican"], calories=550, protein_g=42, carbs_g=50, fat_g=18, fiber_g=9, sugar_g=7, sodium_mg=680, allergens=["gluten"], diet_ok=["omnivore"]),
        ]
        
        # Workouts
        self.WORKOUTS = [
            WorkoutTemplate(id="w1", name="Zone-2 Walk", intensity_zone="Z2_low", impact="low", equipment_needed=["shoes"], duration_min=30, focus_tags=["endurance"]),
            WorkoutTemplate(id="w2", name="Zone-2 Bike", intensity_zone="Z2", impact="low", equipment_needed=["stationary_bike"], duration_min=30, focus_tags=["endurance"]),
            WorkoutTemplate(id="w3", name="Tempo Intervals 4x4", intensity_zone="Tempo", impact="moderate", equipment_needed=["shoes"], duration_min=28, focus_tags=["endurance"]),
            WorkoutTemplate(id="w4", name="Mobility Flow 15", intensity_zone="Z2_low", impact="low", equipment_needed=["yoga_mat"], duration_min=15, focus_tags=["mobility"]),
        ]
        
        logger.info(f"📚 Loaded catalogs: {len(self.MUSIC)} music, {len(self.MEALS)} meals, {len(self.WORKOUTS)} workouts")
    
    async def process_feedback(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a feedback message."""
        try:
            # Extract feedback data
            feedback_data = message_data.get('feedback', {})
            feedback_id = message_data.get('id', 'unknown')
            timestamp = message_data.get('timestamp', datetime.now().timestamp())
            
            from shared.models import Feedback, UserProfile
            
            # Parse feedback
            fb = Feedback(**feedback_data)
            
            logger.info(f"📝 Processing feedback for user {fb.user_id}, domain {fb.domain}, item {fb.item_id}")
            
            # Get user from database
            user_doc = await self._get_user(fb.user_id)
            if not user_doc:
                raise ValueError(f"User {fb.user_id} not found")
            
            user = UserProfile(**user_doc)

            # Get current state to make contextual decision (IDENTICAL to backend)
            from shared.utils import get_today_iso
            today = get_today_iso(None)
            sleep_docs = await self._get_recent_entries("sleep", fb.user_id, limit=7)
            nut_docs = await self._get_recent_entries("nutrition", fb.user_id, limit=3)
            act_docs = await self._get_recent_entries("activity", fb.user_id, limit=7)
            from shared.models import SleepEntry, NutritionEntry, ActivityEntry
            sleep_entries = [SleepEntry(**d) for d in sleep_docs]
            todays_nutrition = None
            if nut_docs:
                for d in reversed(nut_docs):
                    if d["date"] <= today:
                        todays_nutrition = NutritionEntry(**d)
                        break
                activity_entries = [ActivityEntry(**d) for d in act_docs]
                state = self._compute_state_entries(user, sleep_entries, todays_nutrition, activity_entries)
                arm_to_update = self._thompson_sample_contextual(fb.user_id, fb.domain, state)
                r = self._reward_from_feedback(fb.domain, fb)
                self._update_bandit(fb.user_id, fb.domain, arm_to_update, r, state)

                # Update prefs
                item_tags = self._get_item_tags(fb.domain, fb.item_id)
                track = next((m for m in self.MUSIC if m.id == fb.item_id), None)
                item_tags = (track.genres if track else [])
            elif fb.domain == "meal":
                meal = next((m for m in self.MEALS if m.id == fb.item_id), None)
                item_tags = (meal.cuisine_tags if meal else [])
            else:
                workout = next((w for w in self.WORKOUTS if w.id == fb.item_id), None)
                item_tags = (workout.focus_tags if workout else [])

            self._update_preferences(user, fb.domain, item_tags, fb.thumbs)
            
            # Save updated preferences to database
            await self._save_user_preferences(user)
            
            result = {
                "feedback_id": feedback_id,
                "user_id": fb.user_id,
                "domain": fb.domain,
                "reward": r,
                "arm_updated": arm_to_update,
                "processed_at": datetime.now().isoformat(),
                "processing_time_ms": (datetime.now().timestamp() - timestamp) * 1000
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error processing feedback {message_data.get('id', 'unknown')}: {e}")
            raise
    
    async def _get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user from MongoDB."""
        try:
            db = self.db_client[self.db_name]
            collection = db['users']
            user_doc = collection.find_one({"user_id": user_id})
            return user_doc
        except Exception as e:
            logger.error(f"❌ Error getting user {user_id}: {e}")
            raise
    
    async def _get_recent_entries(self, collection_name: str, user_id: str, limit: int = 7) -> List[Dict[str, Any]]:
        """Get recent entries for a user from MongoDB."""
        try:
            from shared.db import get_recent_entries
            return get_recent_entries(self.db_client, self.db_name, collection_name, user_id, limit)
        except Exception as e:
            logger.error(f"❌ Error getting recent {collection_name} entries for {user_id}: {e}")
            raise
    
    def _compute_state_entries(self, user, sleep_entries, todays_nutrition, activity_entries) -> Dict[str, int]:
        """Pure state computation from supplied entries.
        
        Falls back to default baselines when data slices are empty.
        """
        from shared.utils import clamp01, mean_std
        import numpy as np
        
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
                    bedtime_minutes.append(hour*60+minute)
                except Exception:
                    continue
            if len(bedtime_minutes) >= 2:
                bedtime_variance = np.std(bedtime_minutes)
                bedtime_consistency = clamp01(1 - bedtime_variance/120.0)
            else:
                bedtime_consistency = 0.5
            # Recovery factor from last 7 activities
            if len(activity_entries) >= 2:
                today_steps = activity_entries[-1].steps
                recent_steps = [a.steps for a in activity_entries[-7:]]
                mean_s, std_s = mean_std(recent_steps)
                if std_s > 0:
                    strain_z = (today_steps - mean_s)/std_s
                    recovery_factor = clamp01(1 - strain_z/2.0)
                else:
                    recovery_factor = 0.5
            else:
                recovery_factor = 0.5
            sleep_component = 0.7*duration_score + 0.3*efficiency_score
            readiness = round(100*(0.50*sleep_component + 0.25*bedtime_consistency + 0.25*recovery_factor))
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
            fuel = round(100*(0.45*protein_score + 0.25*fiber_score + 0.15*(1-sugar_penalty) + 0.15*(1-sodium_penalty)))
        else:
            fuel = 50

        # Strain
        if activity_entries:
            today_activity = activity_entries[-1]
            steps_7d = [a.steps for a in activity_entries[-7:]]
            steps_mean, steps_std = mean_std(steps_7d if steps_7d else [today_activity.steps])
            steps_z_score = (today_activity.steps - steps_mean) / (steps_std if steps_std else 1.0)
            steps_norm = 0.6 * clamp01((steps_z_score / 2.0) + 0.5)
            hr_norm = 0.4 * clamp01((today_activity.heart_rate_avg - 90) / (170 - 90))
            activity_norm = 0.2 * clamp01(today_activity.active_minutes / 120)
            strain = round(100 * clamp01(steps_norm + hr_norm + activity_norm))
        else:
            strain = 40

        return {"Readiness": int(min(100,max(0,readiness))),
                "Fuel": int(min(100,max(0,fuel))),
                "Strain": int(min(100,max(0,strain)))}
    
    def _thompson_sample_contextual(self, user_id: str, domain: str, state: Dict[str, int]) -> str:
        """Thompson sampling with state context using MABWiser (IDENTICAL to backend)."""
        bandit = self._get_or_create_bandit(user_id, domain)
        context = self._get_state_context(state)

        try:
            # If bandit has been trained, predict with context
            arm = bandit.predict([context])[0]
        except:
            # If not trained yet, randomly select an arm
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
                }
            }
            arms = list(ARMS[domain].keys())
            import random
            arm = random.choice(arms)

        return arm
    
    def _get_state_context(self, state: Dict[str, int]) -> List[float]:
        """Convert state dict to context vector for bandit (IDENTICAL to backend)."""
        return [
            state["Readiness"] / 100.0,  # Normalize to 0-1
            state["Fuel"] / 100.0,
            state["Strain"] / 100.0
        ]
    
    def _get_or_create_bandit(self, user_id: str, domain: str):
        """Get or create a contextual bandit for user and domain (IDENTICAL to backend)."""
        from mabwiser.mab import MAB, LearningPolicy, NeighborhoodPolicy
        
        key = (user_id, domain)
        if key not in self.bandits:
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
                }
            }
            arms = list(ARMS[domain].keys())
            # Use Thompson Sampling with contextual features
            self.bandits[key] = MAB(
                arms=arms,
                learning_policy=LearningPolicy.ThompsonSampling(),
                neighborhood_policy=NeighborhoodPolicy.KNearest(k=3)
            )
        return self.bandits[key]
    
    def _reward_from_feedback(self, domain: str, fb) -> float:
        """Calculate reward from user feedback (IDENTICAL to backend)."""
        from shared.utils import clamp01
        
        if domain == "music":
            return clamp01(0.4*(fb.hr_zone_frac or 0) + 0.3*(1 if fb.thumbs>0 else 0) + 0.2*(fb.completed or 0) + 0.1*(0 if (fb.skipped_early or 0) else 1))
        if domain == "meal":
            return clamp01(0.5*(fb.ate or 0) + 0.3*(fb.protein_gap_closed_norm or 0) + 0.2*(1 if fb.thumbs>0 else 0))
        if domain == "workout":
            return clamp01(0.4*(fb.completed or 0) + 0.3*(fb.hr_zone_frac or 0) + 0.3*(1 - min(1.0, abs((fb.rpe or 0) - 5)/5)))
        return 0.0
    
    def _update_bandit(self, user_id: str, domain: str, arm_id: str, r: float, state: Dict[str, int]):
        """Update bandit arm based on reward with state context (IDENTICAL to backend)."""
        bandit = self._get_or_create_bandit(user_id, domain)

        context = self._get_state_context(state)
        # Train the bandit with context, chosen arm, and reward
        bandit.partial_fit(
            decisions=[arm_id],
            rewards=[r],
            contexts=[context]
        )
        
        logger.debug(f"📊 Updated bandit for {user_id}/{domain}/{arm_id}: reward={r:.3f}, context={context}")
    
    def _get_item_tags(self, domain: str, item_id: str) -> List[str]:
        """Get item tags for preference updates."""
        if domain == "music":
            track = next((m for m in self.MUSIC if m.id == item_id), None)
            return track.genres if track else []
        elif domain == "meal":
            meal = next((m for m in self.MEALS if m.id == item_id), None)
            return meal.cuisine_tags if meal else []
        else:  # workout
            workout = next((w for w in self.WORKOUTS if w.id == item_id), None)
            return workout.focus_tags if workout else []
    
    def _update_preferences(self, user, domain: str, item_tags: List[str], thumbs: int):
        """Update user preferences based on feedback (IDENTICAL to backend)."""
        if thumbs == 0 or not item_tags:
            return
        
        import numpy as np
        lr_fast = 0.3
        
        if domain == "music":
            for t in item_tags:
                w = user.pref_music_genres.get(t, 0.0)
                user.pref_music_genres[t] = float(np.clip(w + (lr_fast if thumbs>0 else -lr_fast), 0.0, 1.0))
        elif domain == "meal":
            for t in item_tags:
                w = user.pref_meal_cuisines.get(t, 0.0)
                user.pref_meal_cuisines[t] = float(np.clip(w + (lr_fast if thumbs>0 else -lr_fast), 0.0, 1.0))
        elif domain == "workout":
            for t in item_tags:
                w = user.pref_workout_focus.get(t, 0.0)
                user.pref_workout_focus[t] = float(np.clip(w + (lr_fast if thumbs>0 else -lr_fast), 0.0, 1.0))
    
    async def _save_user_preferences(self, user):
        """Save updated user preferences to MongoDB."""
        try:
            db = self.db_client[self.db_name]
            collection = db['users']
            
            # Update user preferences in database
            result = collection.update_one(
                {"user_id": user.user_id},
                {"$set": {
                    "pref_music_genres": user.pref_music_genres,
                    "pref_meal_cuisines": user.pref_meal_cuisines,
                    "pref_workout_focus": user.pref_workout_focus
                }}
            )
            
            if result.modified_count > 0:
                logger.debug(f"✅ Updated preferences for user {user.user_id}")
            else:
                logger.warning(f"⚠️ No preferences updated for user {user.user_id}")
                
        except Exception as e:
            logger.error(f"❌ Error saving preferences for user {user.user_id}: {e}")
            raise
    
    async def cleanup(self):
        """Clean up resources."""
        if self.db_client:
            self.db_client.close()
            logger.info("📝 MongoDB connection closed")