import { meals as demoMeals, workouts as demoWorkouts, playlists as demoPlaylists, recipeDetails, workoutPlans } from '../data/demo';

const delay = (ms) => new Promise((res) => setTimeout(res, ms));

export async function fetchMeals() {
  await delay(600);
  return demoMeals.map((m) => ({ ...m, calories: 420 + m.id * 37 }));
}

export async function selectMeal(mealId) {
  await delay(400);
  return { ok: true, mealId };
}

export async function fetchWorkouts() {
  await delay(700);
  return demoWorkouts.map((w, i) => ({ ...w, exercises: 5 + i * 2 }));
}

export async function startWorkout(id) {
  await delay(300);
  return { ok: true, id, startedAt: Date.now() };
}

export async function skipWorkoutStep(stepIdx) {
  await delay(250);
  return { ok: true, stepIdx };
}

export async function completeWorkout(id) {
  await delay(500);
  return { ok: true, id, completedAt: Date.now() };
}

export async function fetchPlaylists() {
  await delay(500);
  return demoPlaylists;
}

export async function playTrack(playlistId) {
  await delay(300);
  return { ok: true, playlistId };
}

export async function skipTrack(currentId) {
  await delay(250);
  // naive next id selection
  const ids = demoPlaylists.map((p) => p.id);
  const idx = Math.max(0, ids.indexOf(currentId));
  const next = ids[(idx + 1) % ids.length];
  return { ok: true, playlistId: next };
}

export async function getTodaySuggestions() {
  await delay(500);
  // naive pick based on timestamp
  const meal = demoMeals[(Math.floor(Date.now() / (1000 * 60)) % demoMeals.length)];
  const workout = demoWorkouts[(Math.floor(Date.now() / (1000 * 60 * 2)) % demoWorkouts.length)];
  return { mealId: meal.id, workoutId: workout.id };
}

export async function getRecipeDetail(id) {
  await delay(300);
  return recipeDetails[id];
}

export async function getWorkoutPlan(id) {
  await delay(300);
  return workoutPlans[id];
}

export async function getDailyStats() {
  await delay(350);
  // Simple deterministic values for demo
  const target = 2200;
  const consumed = 1200 + ((new Date().getHours() * 97) % 600);
  return { target, consumed, remaining: Math.max(0, target - consumed) };
}

export async function getTrainingCalendar(days = 14) {
  await delay(400);
  const today = new Date();
  const out = [];
  for (let i = days - 1; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(today.getDate() - i);
    // pseudo pattern: trained on even days or if day%5===0
    const day = d.getDate();
    const trained = day % 2 === 0 || day % 5 === 0;
    out.push({ date: d.toISOString().slice(0, 10), trained });
  }
  return out;
}

export async function getGoals() {
  await delay(300);
  // Mock weekly goals
  return [
    { id: 'g1', name: 'Train 4x this week', hit: Math.random() > 0.4 },
    { id: 'g2', name: 'Stay under calories today', hit: Math.random() > 0.2 },
    { id: 'g3', name: 'Walk 6k+ steps', hit: Math.random() > 0.5 },
  ];
}

export async function getTodayMeals(count = 5) {
  await delay(450);
  // rotate through demoMeals deterministically
  const start = Math.floor(Date.now() / (1000 * 60)) % demoMeals.length;
  const out = [];
  for (let i = 0; i < count; i++) {
    const m = demoMeals[(start + i) % demoMeals.length];
    out.push({ ...m, calories: 380 + ((m.id * 73) % 240) });
  }
  return out;
}

export async function getSuggestedMeal(category, prevId) {
  await delay(350);
  const pool = demoMeals.filter((m) => m.category === category);
  if (!pool.length) return null;
  if (prevId) {
    const idx = pool.findIndex((m) => m.id === prevId);
    const next = pool[(idx + 1) % pool.length];
    return { ...next, calories: 350 + ((next.id * 71) % 220) };
  }
  const seed = Math.floor(Date.now() / (1000 * 30)) % pool.length;
  const m = pool[seed];
  return { ...m, calories: 350 + ((m.id * 71) % 220) };
}

export async function acceptSuggestedMeal(category, id) {
  await delay(300);
  return { ok: true, category, id };
}

export async function getSuggestedWorkout(category, prevId) {
  await delay(350);
  const pool = demoWorkouts.filter((w) => w.category === category);
  if (!pool.length) return null;
  const enrich = (w) => ({ ...w, exercises: 5 + ((w.id * 2) % 6) });
  if (prevId) {
    const idx = pool.findIndex((w) => w.id === prevId);
    const next = pool[(idx + 1) % pool.length];
    return enrich(next);
  }
  const seed = Math.floor(Date.now() / (1000 * 30)) % pool.length;
  return enrich(pool[seed]);
}

export async function acceptSuggestedWorkout(category, id) {
  await delay(300);
  return { ok: true, category, id };
}
