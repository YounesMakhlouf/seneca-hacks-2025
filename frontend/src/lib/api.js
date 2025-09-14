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
