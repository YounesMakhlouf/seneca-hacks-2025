Project Brief for AI Agent: Body-to-Behavior Recommender
Version: 0.1 • Audience: AI agent integrated with our hackathon MVP

1) What this project is
A closed-loop system that turns recent personal health signals (sleep, activity, nutrition) into real-time, adaptive suggestions across three domains:

Music: selects tracks and adjusts tempo/energy to steer effort and mood during sessions.
Meals: proposes just‑in‑time, high‑utility meals/snacks that close macro/micro gaps.
Workouts: picks micro‑workouts that match user readiness, goals, and available equipment.
You (the AI agent) are the decision and explanation layer: you call our backend to compute state, choose a domain to act on, select items, collect feedback, and learn user preferences over time.

Non-medical: This is general wellness guidance, not medical advice.

2) User data you can rely on
We ingest lightweight per‑day records. Samples:

Sleep: duration, stages, efficiency, bedtime/wake.
Nutrition: calories, protein/carbs/fat, fiber, sugar, sodium.
Activity: steps, active minutes, distance, average HR, workout duration.
Profile: age, weight, height, BMI, fitness level, goals, join date, preferences, equipment, allergens, diet flags.
Data is imperfect. You must validate ranges and degrade gracefully if missing.

3) Core loop (sense → decide → act → learn)
Sense: compute three scores from the last 24–72 hours.
Readiness (0–100) from sleep, strain, chrono consistency.
Fuel (0–100) from daily protein/fiber sufficiency and sugar/sodium moderation.
Strain (0–100) from activity load today (steps/HR/active minutes).
Decide: pick which domain to act on now (music, meal, workout).
Act: deliver one suggestion and, for music, keep adapting during the session.
Learn: log outcomes (HR in zone, completion, thumbs, ate?, macro gap closure), update bandit priors and preference vectors.
4) Backend API you call
Endpoints exposed by our FastAPI service:

GET /state?user_id=...
Returns: { date, state: { Readiness, Fuel, Strain } }
POST /recommend
Body: { user_id, intent: "auto|music|meal|workout", hours_since_last_meal, now?, current_hr?, rpe? }
Returns: { domain, state, item, bandit_arm }
POST /feedback
Body: { user_id, domain, item_id, thumbs, completed?, hr_zone_frac?, rpe?, ate?, protein_gap_closed_norm?, skipped_early? }
Returns: { ok, reward, arm_updated }
You should:

Prefer intent="auto" unless the user explicitly requests a domain.
Always send /feedback after a suggestion window ends (or best effort).
5) Decision policy (how you pick what to do)
If Fuel < 50 and it’s been ≥ 3 hours since last meal → propose a meal/snack.
Else if the user is in a session or pressed “start” → music (and workout if requested).
Else:
If Readiness ≥ 50 and Strain < 70 → suggest a workout.
Otherwise → music to support light activity or focus.
Always respect hard constraints: allergens, diet flags, equipment availability, intensity caps from low readiness/high strain.

6) Candidate generation and ranking (how items are chosen)
Step 1: Candidate filters by domain:
Music: BPM near target (±15), energy ≤ cap, genres matching the selected bandit arm.
Meals: diet/allergen compliance; high‑protein/fiber options that fit remaining sugar/sodium budget.
Workouts: intensity ≤ cap (Z2_low/Z2/Tempo), equipment owned, goal-aligned.
Step 2: Ranking with a multi‑objective score:
Score = 0.35·GoalFit + 0.30·StateFit + 0.25·PrefFit + 0.10·Novelty − penalties
PrefFit uses user tag weights (genres/cuisines/focus). Novelty lightly boosts less‑seen items.
Step 3: Bandit exploration:
Thompson Sampling over small “template arms” per domain (e.g., lofi_low vs synth_mid for music).
You pick the arm with the sampled best θ, then rank items within that arm.
7) Preference learning (how tastes are learned)
Explicit signals: thumbs up/down; completion; skips.
Physiological signals: HR in target zone; RPE near target; macro gaps closed after meals.
Learning:
Bandit: Beta(α,β) per user×domain×arm; r≥0.6 → α+=1 else β+=1.
Preferences: simple tag-weight EMA updates (fast and slow), bounded to [0,1].
Soft-block disliked tags after repeated negatives; allow override.
8) Music control loop (during a session)
Target HR from readiness/strain → target BPM ≈ (TargetHR/HRmax)*180, clamped to [90, 180].
Every 15–30 s:
Compare current HR and RPE to target.
Adjust next track BPM by a small delta; cap energy if strain high.
Keep genres inside user preferences with some exploration.
Outcomes: “HR in zone,” “block completed,” “skipped early,” “thumbs” feed the reward.
9) Meal generator (closing today’s gaps)
Compute remaining protein/fiber and sugar/sodium room from today’s totals vs targets.
Select templates that:
Fill 60–100% of protein deficit without blowing sugar/sodium budgets.
Provide fiber if still lacking.
Return:
1–2 best options (name, macros, cuisine), simple serving guidance, and 1–2 swaps.
10) Workout selector (safe and goal-aligned)
Intensity cap from Readiness/Strain:
Low readiness or high strain → Z2_low.
Moderate → Z2.
Good → Tempo (still conservative).
Respect equipment and disliked movements.
Prefer templates the user completes.
11) What to output to the UI (formatting expectations)
For each suggestion, you provide a concise card:

Music: track title/artist, BPM, energy, short reason (“keeping you in zone 2”).
Meal: name, servings, macros (kcal, P/C/F, fiber, sugar, sodium), reason (“+35g protein to close today’s gap”).
Workout: name, duration, intensity, required equipment, reason (“Readiness 58 → Z2 focus”).
Keep reasons one line; avoid medical phrasing.

12) Data validation and fallbacks
Validate plausible ranges (examples): HRavg 40–200, sleep_eff 50–100, fiber 0–80 g, sodium 0–6000 mg.
If missing or implausible:
Down‑weight that component in the score.
Rely on safer defaults (e.g., Z2_low) and explicit preferences.
Surface a subtle “data uncertainty” flag in the reason text if needed.
13) Reward shaping (per domain)
Music r = 0.4·HR_in_zone + 0.3·thumbs + 0.2·block_completed + 0.1·(1 − skipped_early)
Meal r = 0.5·ate + 0.3·protein_gap_closed_norm + 0.2·taste_thumb
Workout r = 0.4·completed + 0.3·HR_in_zone + 0.3·(1 − |RPE − target|/5)
Use r to update both the bandit arm and preferences.

14) Cold start (first session)
Ask 6–8 quick questions:
Music genres, cuisines, diet flags/allergens, equipment, disliked movements, goal.
Seed tag weights from answers; use higher exploration for first 3–5 sessions.
Start with safer items: Z2_low workout, protein-forward snack, low‑energy music.
15) Safety, inclusivity, and constraints
Hard blocks:
Allergens/diet restrictions, missing equipment, excessive intensity under low readiness/high strain.
Always include an “easy option” and opt‑out.
Use user‑provided HRmax if available; otherwise conservative formulas.
16) Example interaction (happy path)
You call /state and get Readiness 58, Fuel 42, Strain 55.
Decide: Fuel low and 4 h since last meal → domain=meal.
Call /recommend with intent="auto".
You receive: meal item + bandit_arm.
Render meal card; await “ate?” and thumbs; then POST /feedback.
Bandit and preferences update; later, user starts a session → you switch to music/workout flow.
17) Minimal JSON schemas (reference)
MusicTrack: { id, title, artist, bpm, energy[0..1], valence[0..1], genres[] }
MealTemplate: { id, name, cuisine_tags[], calories, protein_g, carbs_g, fat_g, fiber_g, sugar_g, sodium_mg, allergens[], diet_ok[] }
WorkoutTemplate: { id, name, intensity_zone, impact, equipment_needed[], duration_min, focus_tags[] }
Feedback: see /feedback endpoint.
18) What we expect from you (operational checklist)
On app open or session start:
GET /state, decide domain, POST /recommend.
During music sessions:
Poll device HR every ~20 s (if available), track RPE prompt every ~3–5 min.
Adjust tracks as needed; batch outcomes to one /feedback per block.
After each suggestion window:
Gather thumbs/completion/ate; compute reward; POST /feedback.
Update UI reasons with one simple, evidence-backed line.
19) Extensibility hooks (optional for hackathon)
Weather-aware bias (heat → indoor, hydration snack).
Social “sync session” (group bandit).
Grocery mode (3-item list to close tomorrow’s predicted gaps).
20) Failure modes and what you should do
No candidates pass hard filters:
Relax within safe bounds (e.g., ignore equipment only if workout intensity is low and movement is safe), or switch domain.
Conflicting signals (high HR, low RPE):
Trust HR for safety; downshift intensity/music energy; ask for a brief RPE recheck.
Sparse nutrition logs:
Use last known day’s totals; down‑weight Fuel in decision; prefer balanced, modest‑size protein-forward meals.

---
## MongoDB (Optional Persistence Mode)

By default the app runs fully in-memory loading capped JSON datasets. A MongoDB mode is available for persistence & easier querying.

### Enable
1. Copy `.env.example` to `.env` and set `USE_MONGO=1` if you want Mongo persistence.
2. (Optional) Change `MONGO_HOST_PORT` (default 27017 to avoid conflicts with a local standalone Mongo) if needed.
3. Start services:
```bash
docker compose up --build
```
3. API will be at http://localhost:8000 (Mongo at localhost:27017).

### How It Works
- On first run with `USE_MONGO=1`, after JSON ingestion the app seeds Mongo collections (`users`, `sleep`, `nutrition`, `activity`, `measurements` when present) if empty.
- Subsequent runs reuse existing Mongo data (no re-seed unless collections are dropped).
- Heart rate mega file intentionally ignored for memory constraints.

### Environment Variables
| Variable | Purpose | Default |
|----------|---------|---------|
| USE_MONGO | Toggle persistence (0/1) | 0 |
| MONGODB_URI | Connection URI | mongodb://bbr:bbrpass@mongo:27017/?authSource=admin |
| BBR_USERS_CAP | User load cap | 50000 |
| BBR_SLEEP_CAP | Sleep entry cap | 500000 |
| BBR_ACTIVITY_CAP | Activity entry cap | 1000000 |
| BBR_MEASUREMENTS_CAP | Measurement cap | 100000 |

### Notes
- Endpoints transparently fetch from Mongo for user docs; services still read in-memory arrays for state (future enhancement: stream directly from DB).
- If you want to force a re-seed: drop the database (`docker exec -it bbr-mongo mongosh` then `db.dropDatabase()`).
- Keep caps conservative to protect local memory.

### Dev Tips
- For quick iteration without Mongo overhead leave `USE_MONGO=0`.
- Use `docker compose down -v` to reset volumes.
