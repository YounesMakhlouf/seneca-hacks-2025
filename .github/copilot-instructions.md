# GitHub Copilot Project Instructions

You are assisting on a FastAPI + Pydantic (v2) hackathon MVP: a "Body→Behavior" recommender that transforms daily health signals (sleep, nutrition, activity) into adaptive suggestions (music track, meal/snack, micro‑workout). All storage is **in‑memory**; no database. Large JSON datasets are ingested at startup with memory caps.

## 1. Architecture At a Glance
- Entry: `main.py` / `src/body_behavior_recommender/app.py` bootstraps FastAPI, loads data via `EnhancedDataLoader`.
- Data layer: `data_loader.py` loads users, sleep, nutrition, activity, measurements. Heart rate huge dataset intentionally skipped.
- Domain models: `models.py` (Pydantic) for UserProfile, SleepEntry, NutritionEntry, ActivityEntry + recommendation artifacts.
- Services: `services.py` houses scoring (Readiness/Fuel/Strain), candidate filtering, ranking, bandit logic (mabwiser Thompson Sampling + kNN context), preference updates.
- API layer: `endpoints.py` exposes `/health`, `/state`, `/recommend`, `/feedback`, plus user/data introspection endpoints.
- Utilities: `utils.py` for math/clamping/time helpers & state->zone/targets.

## 2. Core Loop (Sense → Decide → Act → Learn)
1. Compute state (Readiness, Fuel, Strain) from recent data.
2. Choose domain (meal if Fuel low & >=3h since meal; else workout if readiness ok & strain moderate; else music).
3. Generate + filter candidates (domain specific constraints & user prefs).
4. Rank: score = 0.35 GoalFit + 0.30 StateFit + 0.25 PrefFit + 0.10 Novelty − penalties.
5. Bandit: Thompson sample arm → influences candidate pool.
6. Return top item; later POST `/feedback` → reward → bandit + preference updates.

## 3. Data Ingestion Strategy
- Large files: `users.json`, `sleep.json`, `activities.json`, `measurements.json`.
- Caps (current): users 50k, sleep 500k, activity target 1M (chunk loader WIP), measurements 100k.
- Sleep loader already bulk loads & slices then normalizes (hours→minutes).
- Activity loader still line‑parse; will be refactored to bulk load + slice (prefer simple `json.load` + slicing unless file is too large to fit in memory). Heart rate is skipped (3GB) to stay memory safe.
- Measurement loader erroneously re-imports `fitness-users.json` (cleanup pending) – avoid re‑adding this bug when editing.

## 4. Performance / Safety Constraints
- Keep startup reasonable (< ~10s). Avoid O(N^2) passes; single linear transform + append.
- Never load > configured caps; introduce constants or env overrides if expanding.
- Do not persist global mutable state across module reloads except the intended in‑memory stores.
- Validate ranges defensively; skip malformed entries silently (log optional warning).

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
- Environment uses `uv`. Typical run: `uv run uvicorn main:app --reload` (already in dev scripts).
- For new logic, add minimal unit tests (if added) under a `tests/` folder (not present yet) using `pytest` (dependency already declared).

## 10. Common Pitfalls
- Double-loading users (current measurement loader bug). Fix instead of propagating.
- Activity loader producing 0 entries due to naive line parsing of pretty JSON array.
- Forgetting to cap large list slices → memory blowup risk.

## 11. Style Preferences
- Snake_case, type hints, early returns for clarity.
- Prefer list comprehensions over manual loops when readable.
- Keep print statements minimal & prefixed with emoji already used (📊, ✅, ❌) for quick visual scanning.

## 12. When Unsure
Surface a concise comment/TODO describing assumption (e.g., `# TODO: confirm if HR variance should mod readiness`). Avoid speculative refactors without data.

---
By following this guide, Copilot should generate changes that respect data scale, recommendation logic integrity, and hackathon velocity.
