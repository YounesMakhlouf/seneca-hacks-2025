"""Data loader for fitness datasets."""

import json
import os
from collections import defaultdict
from typing import Dict, List

from .models import ActivityEntry, NutritionEntry, SleepEntry, UserProfile

USERS_CAP = int(os.getenv("BBR_USERS_CAP", "50000"))
SLEEP_CAP = int(os.getenv("BBR_SLEEP_CAP", "500000"))
ACTIVITY_CAP = int(os.getenv("BBR_ACTIVITY_CAP", "1000000"))
MEASUREMENTS_CAP = int(os.getenv("BBR_MEASUREMENTS_CAP", "100000"))


class EnhancedDataLoader:
    """Enhanced data loader that uses the largest and most comprehensive datasets."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.users: Dict[str, UserProfile] = {}
        self.sleep: Dict[str, List[SleepEntry]] = defaultdict(list)
        self.nutrition: Dict[str, List[NutritionEntry]] = defaultdict(list)
        self.activity: Dict[str, List[ActivityEntry]] = defaultdict(list)

        # Enhanced data (new larger datasets)
        self.heart_rate: Dict[str, List] = defaultdict(list)
        self.measurements: Dict[str, List] = defaultdict(list)
        self.detailed_activities: Dict[str, List] = defaultdict(list)

    def load_all_data(self, use_enhanced: bool = True) -> bool:
        """Load all fitness data from JSON files.

        Args:
            use_enhanced: If True, use larger datasets with more detailed data
        """
        try:
            print("🔄 Loading enhanced fitness data...")

            # Choose which datasets to use based on size and quality
            if use_enhanced:
                self._load_users_enhanced()
                self._load_sleep_enhanced()
                self._load_activities_enhanced()  # Use larger activities dataset
                self._load_measurements()
                # Skip heart_rate for now (3GB is too large for memory)
            else:
                # Fallback to smaller datasets
                self._load_users()
                self._load_sleep_data()
                self._load_activity_data()

            # Load nutrition from the best available source
            self._load_nutrition_data()

            total_sleep = sum(len(entries) for entries in self.sleep.values())
            total_nutrition = sum(len(entries) for entries in self.nutrition.values())
            total_activity = sum(len(entries) for entries in self.activity.values())
            total_measurements = sum(
                len(entries) for entries in self.measurements.values()
            )

            print(f"✅ Loaded {len(self.users)} users")
            print(f"✅ Loaded {total_sleep} sleep entries")
            print(f"✅ Loaded {total_nutrition} nutrition entries")
            print(f"✅ Loaded {total_activity} activity entries")
            print(f"✅ Loaded {total_measurements} measurement entries")
            print("🎉 Enhanced data loaded successfully!")
            return True

        except Exception as e:
            print(f"❌ Error loading enhanced data: {e}")
            print("🔄 Falling back to basic datasets...")
            return self._load_basic_data()

    def _load_basic_data(self) -> bool:
        """Fallback to load basic fitness data."""
        try:
            self._load_users()
            self._load_sleep_data()
            self._load_nutrition_data()
            self._load_activity_data()
            print("✅ Basic data loaded successfully!")
            return True
        except Exception as e:
            print(f"❌ Error loading basic data: {e}")
            return False

    def _load_users(self):
        """Load user profiles from JSON file (fallback method)."""
        file_path = os.path.join(self.data_dir, "fitness-users.json")

        with open(file_path, "r") as f:
            users_data = json.load(f)

        for user_data in users_data:
            # Add default preference and equipment data
            user_data.update(
                {
                    "pref_music_genres": {"lofi": 0.5, "pop": 0.3, "synthwave": 0.2},
                    "pref_meal_cuisines": {
                        "mediterranean": 0.4,
                        "mexican": 0.3,
                        "indian": 0.3,
                    },
                    "pref_workout_focus": {"endurance": 0.6, "mobility": 0.4},
                    "hr_max_override": None,
                    "allergens": [],
                    "diet_flags": [],
                    "equipment": ["shoes", "yoga_mat"],
                }
            )

            # Add equipment based on user goals
            if user_data["goals"] == "endurance":
                user_data["equipment"].extend(["stationary_bike", "running_watch"])
            elif user_data["goals"] == "strength":
                user_data["equipment"].extend(["dumbbells", "resistance_bands"])

            user = UserProfile(**user_data)
            self.users[user.user_id] = user

    def _load_users_enhanced(self):
        """Load user profiles from the larger users.json file."""
        file_path = os.path.join(self.data_dir, "users.json")

        # Check if the larger dataset exists, fallback to fitness-users.json
        if not os.path.exists(file_path):
            file_path = os.path.join(self.data_dir, "fitness-users.json")

        with open(file_path, "r") as f:
            users_data = json.load(f)

        # Limit to first USERS_CAP users for memory efficiency
        if len(users_data) > USERS_CAP:
            users_data = users_data[:USERS_CAP]
            print(f"📊 Limited users to {USERS_CAP}")

        for user_data in users_data:
            # Calculate BMI if not present
            if (
                "bmi" not in user_data
                and "height" in user_data
                and "weight" in user_data
            ):
                height_m = user_data["height"] / 100  # Convert cm to meters
                user_data["bmi"] = round(user_data["weight"] / (height_m**2), 1)
            elif "bmi" not in user_data:
                user_data["bmi"] = 25.0  # Default BMI

            # Add goals if not present
            if "goals" not in user_data:
                # Assign goals based on age and fitness level
                age = user_data.get("age", 30)
                fitness_level = user_data.get("fitness_level", "Beginner").lower()

                if age < 30:
                    user_data["goals"] = (
                        "strength" if fitness_level == "advanced" else "endurance"
                    )
                elif age > 50:
                    user_data["goals"] = "flexibility"
                else:
                    user_data["goals"] = "weight_loss"

            # Add default preference and equipment data if not present
            user_data.setdefault(
                "pref_music_genres", {"lofi": 0.5, "pop": 0.3, "synthwave": 0.2}
            )
            user_data.setdefault(
                "pref_meal_cuisines",
                {"mediterranean": 0.4, "mexican": 0.3, "indian": 0.3},
            )
            user_data.setdefault(
                "pref_workout_focus", {"endurance": 0.6, "mobility": 0.4}
            )
            user_data.setdefault("hr_max_override", None)
            user_data.setdefault("allergens", [])
            user_data.setdefault("diet_flags", [])
            user_data.setdefault("equipment", ["shoes", "yoga_mat"])

            # Add equipment based on user goals
            if user_data.get("goals") == "endurance":
                if "stationary_bike" not in user_data["equipment"]:
                    user_data["equipment"].extend(["stationary_bike", "running_watch"])
            elif user_data.get("goals") == "strength":
                if "dumbbells" not in user_data["equipment"]:
                    user_data["equipment"].extend(["dumbbells", "resistance_bands"])

            try:
                user = UserProfile(**user_data)
                self.users[user.user_id] = user
            except Exception as e:
                print(f"⚠️ Skipping user {user_data.get('user_id', 'unknown')}: {e}")
                continue

    def _load_sleep_enhanced(self):
        """Load sleep data from the larger sleep.json file."""
        file_path = os.path.join(self.data_dir, "sleep.json")

        # Check if larger dataset exists, fallback to fitness-sleep.json
        if not os.path.exists(file_path):
            return self._load_sleep_data()

        print("📊 Loading enhanced sleep data...")

        try:
            with open(file_path, "r") as f:
                sleep_data = json.load(f)

            # Limit to reasonable number for memory management
            if len(sleep_data) > SLEEP_CAP:
                sleep_data = sleep_data[:SLEEP_CAP]
                print(
                    f"📊 Limited sleep data to {SLEEP_CAP} entries for memory efficiency"
                )

            entries_processed = 0
            for entry_data in sleep_data:
                try:
                    # Convert to our expected format
                    sleep_entry = {
                        "user_id": entry_data["user_id"],
                        "date": entry_data["date"],
                        "sleep_duration_minutes": int(
                            entry_data.get("total_sleep", 0) * 60
                        ),
                        "deep_sleep_minutes": int(entry_data.get("deep_sleep", 0) * 60),
                        "rem_sleep_minutes": int(entry_data.get("rem_sleep", 0) * 60),
                        "light_sleep_minutes": int(
                            entry_data.get("light_sleep", 0) * 60
                        ),
                        "sleep_efficiency": entry_data.get("sleep_efficiency", 75.0),
                        "bedtime": str(entry_data.get("bedtime", "23:30")).split()[0]
                        if " " in str(entry_data.get("bedtime", "23:30"))
                        else str(entry_data.get("bedtime", "23:30")),
                        "wake_time": str(entry_data.get("wake_time", "07:00")).split()[
                            0
                        ]
                        if " " in str(entry_data.get("wake_time", "07:00"))
                        else str(entry_data.get("wake_time", "07:00")),
                    }

                    entry = SleepEntry(**sleep_entry)
                    self.sleep[entry.user_id].append(entry)
                    entries_processed += 1

                except (ValueError, TypeError):
                    continue  # Skip malformed entries

            print(f"📊 Processed {entries_processed} sleep entries")

        except Exception as e:
            print(f"❌ Error loading enhanced sleep data: {e}")
            print("🔄 Falling back to basic sleep data...")
            return self._load_sleep_data()

        # Sort sleep entries by date for each user
        for user_id in self.sleep:
            self.sleep[user_id].sort(key=lambda x: x.date)

    def _load_activities_enhanced(self):
        """Load activity data from the larger activities.json file using bulk load + slice cap."""
        file_path = os.path.join(self.data_dir, "activities.json")
        if not os.path.exists(file_path):
            return self._load_activity_data()

        print("📊 Loading enhanced activity data (bulk slice)...")
        try:
            with open(file_path, "r") as f:
                activity_data = json.load(f)
            if len(activity_data) > ACTIVITY_CAP:
                activity_data = activity_data[:ACTIVITY_CAP]
                print(
                    f"📊 Limited activity data to {ACTIVITY_CAP} entries for memory efficiency"
                )

            entries_processed = 0
            for entry_data in activity_data:
                try:
                    activity_entry = {
                        "user_id": entry_data["user_id"],
                        "date": entry_data["date"],
                        "steps": entry_data.get("steps", 0),
                        "calories_burned": entry_data.get("calories_burned", 0),
                        "active_minutes": entry_data.get(
                            "duration", entry_data.get("active_minutes", 0)
                        ),
                        "distance_km": entry_data.get("distance", 0.0),
                        "heart_rate_avg": entry_data.get(
                            "heart_rate_avg", entry_data.get("avg_hr", 0)
                        ),
                        "workout_duration": entry_data.get("duration", 0),
                    }
                    entry = ActivityEntry(**activity_entry)
                    self.activity[entry.user_id].append(entry)
                    entries_processed += 1
                except (ValueError, TypeError, KeyError):
                    continue
            print(f"📊 Processed {entries_processed} activity entries")
        except Exception as e:
            print(f"❌ Error loading enhanced activities data: {e}")
            print("🔄 Falling back to basic activity data...")
            return self._load_activity_data()

        for user_id in self.activity:
            self.activity[user_id].sort(key=lambda x: x.date)

    def _load_measurements(self):
        """Load body measurements data."""
        file_path = os.path.join(self.data_dir, "measurements.json")

        if not os.path.exists(file_path):
            return

        with open(file_path, "r") as f:
            measurements_data = json.load(f)

        # Limit to MEASUREMENTS_CAP entries for memory efficiency
        if len(measurements_data) > MEASUREMENTS_CAP:
            measurements_data = measurements_data[:MEASUREMENTS_CAP]
            print(f"📊 Limited measurements to {MEASUREMENTS_CAP}")

        for entry_data in measurements_data:
            user_id = entry_data.get("user_id")
            if user_id:
                self.measurements[user_id].append(entry_data)
        """Load user profiles from JSON file."""
        file_path = os.path.join(self.data_dir, "fitness-users.json")

        with open(file_path, "r") as f:
            users_data = json.load(f)

        # BUG: previously reloaded fitness-users.json here causing duplicate / conflicting users.
        # Removed duplicate user loading to avoid double-load. Measurements only appended above.

    def _load_sleep_data(self):
        """Load sleep data from JSON file."""
        file_path = os.path.join(self.data_dir, "fitness-sleep.json")

        with open(file_path, "r") as f:
            sleep_data = json.load(f)

        for entry_data in sleep_data:
            # Add missing bedtime and wake_time if not present
            if "bedtime" not in entry_data:
                entry_data["bedtime"] = "23:30"  # Default bedtime
            if "wake_time" not in entry_data:
                entry_data["wake_time"] = "07:00"  # Default wake time

            entry = SleepEntry(**entry_data)
            self.sleep[entry.user_id].append(entry)

        # Sort sleep entries by date for each user
        for user_id in self.sleep:
            self.sleep[user_id].sort(key=lambda x: x.date)

    def _load_sleep_data(self):
        """Load sleep data from JSON file."""
        file_path = os.path.join(self.data_dir, "fitness-sleep.json")

        with open(file_path, "r") as f:
            sleep_data = json.load(f)

        for entry_data in sleep_data:
            # Add missing bedtime and wake_time if not present
            if "bedtime" not in entry_data:
                entry_data["bedtime"] = "23:30"  # Default bedtime
            if "wake_time" not in entry_data:
                entry_data["wake_time"] = "07:00"  # Default wake time

            entry = SleepEntry(**entry_data)
            self.sleep[entry.user_id].append(entry)

        # Sort sleep entries by date for each user
        for user_id in self.sleep:
            self.sleep[user_id].sort(key=lambda x: x.date)

    def _load_nutrition_data(self):
        """Load nutrition data from JSON file."""
        file_path = os.path.join(self.data_dir, "fitness-nutrition.json")

        with open(file_path, "r") as f:
            nutrition_data = json.load(f)

        for entry_data in nutrition_data:
            entry = NutritionEntry(**entry_data)
            self.nutrition[entry.user_id].append(entry)

        # Sort nutrition entries by date for each user
        for user_id in self.nutrition:
            self.nutrition[user_id].sort(key=lambda x: x.date)

    def _load_activity_data(self):
        """Load activity data from JSON file."""
        file_path = os.path.join(self.data_dir, "fitness-activities.json")

        with open(file_path, "r") as f:
            activity_data = json.load(f)

        for entry_data in activity_data:
            entry = ActivityEntry(**entry_data)
            self.activity[entry.user_id].append(entry)

        # Sort activity entries by date for each user
        for user_id in self.activity:
            self.activity[user_id].sort(key=lambda x: x.date)

    def get_user_summary(self, user_id: str) -> Dict:
        """Get a summary of data available for a specific user."""
        if user_id not in self.users:
            return {"error": "User not found"}

        summary = {
            "user_id": user_id,
            "profile": self.users[user_id],
            "data_counts": {
                "sleep_entries": len(self.sleep.get(user_id, [])),
                "nutrition_entries": len(self.nutrition.get(user_id, [])),
                "activity_entries": len(self.activity.get(user_id, [])),
                "measurement_entries": len(self.measurements.get(user_id, [])),
            },
            "date_ranges": {
                "sleep": self._get_date_range(self.sleep.get(user_id, [])),
                "nutrition": self._get_date_range(self.nutrition.get(user_id, [])),
                "activity": self._get_date_range(self.activity.get(user_id, [])),
            },
        }

        # Add measurement info if available
        if user_id in self.measurements and self.measurements[user_id]:
            latest_measurement = max(
                self.measurements[user_id], key=lambda x: x.get("date", "")
            )
            summary["latest_measurement"] = latest_measurement

        return summary

    def _get_date_range(self, entries: List) -> Dict[str, str]:
        """Get the date range for a list of entries."""
        if not entries:
            return {"start": None, "end": None}

        dates = [entry.date for entry in entries]
        return {"start": min(dates), "end": max(dates)}

    def get_recent_data(self, user_id: str, days: int = 7) -> Dict:
        """Get recent data for a user (last N days)."""
        from datetime import datetime, timedelta

        if user_id not in self.users:
            return {"error": "User not found"}

        # Calculate cutoff date
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        result = {
            "user_id": user_id,
            "days": days,
            "cutoff_date": cutoff_date,
            "recent_sleep": [
                s for s in self.sleep.get(user_id, []) if s.date >= cutoff_date
            ],
            "recent_nutrition": [
                n for n in self.nutrition.get(user_id, []) if n.date >= cutoff_date
            ],
            "recent_activity": [
                a for a in self.activity.get(user_id, []) if a.date >= cutoff_date
            ],
        }

        # Add recent measurements if available
        if user_id in self.measurements:
            result["recent_measurements"] = [
                m
                for m in self.measurements[user_id]
                if m.get("date", "") >= cutoff_date
            ]

        return result


# Global data loader instance - use enhanced loader
data_loader = EnhancedDataLoader()
