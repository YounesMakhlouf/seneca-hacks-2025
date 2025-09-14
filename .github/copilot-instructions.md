# GitHub Copilot Project Instructions

You are assisting on a FastAPI + Pydantic (v2) + MongoDB hackathon project: a "Body→Behavior" recommender that transforms daily health signals (sleep, nutrition, activity) into adaptive suggestions (music track, meal/snack, micro‑workout). The project uses **MongoDB** for persistent data storage and **Docker** for containerized deployment. Large JSON datasets are ingested at startup and stored in MongoDB with appropriate indexing.itHub Copilot Project Instructions


## 1. Architecture At a Glance
- Entry: `main.py` / `src/body_behavior_recommender/app.py` bootstraps FastAPI, connects to MongoDB via `mongo_wrapper.py`.
- Data layer: `data_loader.py` loads users, sleep, nutrition, activity, measurements into MongoDB collections with proper indexing.
- Database: `db.py` and `mongo_wrapper.py` handle MongoDB connections, collection management, and queries.
- Domain models: `models.py` (Pydantic) for UserProfile, SleepEntry, NutritionEntry, ActivityEntry + recommendation artifacts.
- Services: `services.py` houses scoring (Readiness/Fuel/Strain), candidate filtering, ranking, bandit logic (mabwiser Thompson Sampling + kNN context), preference updates.
- API layer: `endpoints.py` exposes `/health`, `/state`, `/recommend`, `/feedback`, plus user/data introspection endpoints.
- Utilities: `utils.py` for math/clamping/time helpers & state->zone/targets.
- Container: `Dockerfile` and `docker-compose.yml` for MongoDB + FastAPI deployment.

## 2. Core Loop (Sense → Decide → Act → Learn)
1. Compute state (Readiness, Fuel, Strain) from recent data.
2. Choose domain (meal if Fuel low & >=3h since meal; else workout if readiness ok & strain moderate; else music).
3. Generate + filter candidates (domain specific constraints & user prefs).
4. Rank: score = 0.35 GoalFit + 0.30 StateFit + 0.25 PrefFit + 0.10 Novelty − penalties.
5. Bandit: Thompson sample arm → influences candidate pool.
6. Return top item; later POST `/feedback` → reward → bandit + preference updates.

## 3. Data Ingestion Strategy
- Large files: `users.json`, `sleep.json`, `activities.json`, `measurements.json`.
- MongoDB collections: Users, Sleep, Activities, Measurements with appropriate indexes for performance.
- Bulk insertion with batch processing for large datasets.
- Data validation and transformation during ingestion.
- Heart rate data (3GB) handling optimized for streaming ingestion.
- Indexing strategy: user_id, timestamps, and frequently queried fields.

## 4. Performance / Safety Constraints
- MongoDB queries optimized with proper indexing and aggregation pipelines.
- Connection pooling and efficient query patterns for scalability.
- Docker containerization for consistent deployment across environments.
- Environment variables for MongoDB connection strings and configuration.
- Graceful error handling for database connection issues.
- Data validation at ingestion and query time.

## 5. Recommendation Logic Details
- Readiness: sleep duration & efficiency + bedtime consistency + recovery factor from recent steps.
- Fuel: protein & fiber adequacy minus sugar/sodium penalties.
- Strain: normalized steps z-score + avg HR + active minutes.
- Domain selection rules must remain deterministic given same inputs (pure function style).
- Bandits keyed by (user_id, domain); context = normalized state vector.

## 6. Feedback & Learning
- Reward functions per domain (see `services.py::reward_from_feedback`). Threshold r>=0.6 treated as positive for bandit Beta update.
- Preferences: simple bounded additive updates to tag weights on thumbs.
- Novelty: mild boost for less frequently used items.

## 7. Coding Guidelines
Do:
- Use existing Pydantic models; extend with optional fields instead of altering required schema abruptly.
- Keep functions small & testable; avoid side effects outside designated stores.
- Add helper pure functions in `services.py` or `utils.py` as appropriate.
- Preserve public endpoint signatures unless coordinating change.
- Log concise startup summaries (counts) only.

Avoid:
- Adding heavy dependencies (DBs, ML frameworks) – hackathon scope.
- Blocking I/O in request handlers; all heavy work should be at startup or lightweight per request.
- Large per-request scans over entire global datasets (pre-filter by user_id first).

## 8. Extensibility Hooks
Future (not required now): heart rate streaming ingestion, weather bias, grocery planner, social/group bandit, more nuanced macro planning.

## 9. Testing / Running
- Environment uses `uv`. Docker deployment: `docker-compose up --build`.
- Local development: `uv run uvicorn main:app --reload` (requires MongoDB running).
- MongoDB connection configured via environment variables or docker-compose.
- For new logic, add minimal unit tests under `tests/` folder using `pytest`.

## 10. Common Pitfalls
- MongoDB connection timeouts or authentication issues.
- Improper indexing leading to slow queries on large datasets.
- Docker container networking issues between FastAPI and MongoDB.
- Data validation failures during bulk insertion operations.

## 11. Style Preferences
- Snake_case, type hints, early returns for clarity.
- Prefer list comprehensions over manual loops when readable.
- Keep print statements minimal & prefixed with emoji already used (📊, ✅, ❌) for quick visual scanning.

## 12. When Unsure
Surface a concise comment/TODO describing assumption (e.g., `# TODO: confirm if HR variance should mod readiness`). Avoid speculative refactors without data.

---
By following this guide, Copilot should generate changes that respect MongoDB integration, Docker deployment patterns, recommendation logic integrity, and hackathon velocity.
