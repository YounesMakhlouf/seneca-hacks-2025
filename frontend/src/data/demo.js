export const demoImages = {
  welcome: 'https://images.unsplash.com/photo-1518609878373-06d740f60d8b?w=800&q=80&auto=format&fit=crop',
  meal: 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800&q=80&auto=format&fit=crop',
  pasta: 'https://images.unsplash.com/photo-1525755662778-989d0524087e?w=800&q=80&auto=format&fit=crop',
  bowl: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT556q-kVidjVjl-Hk-HrhG_4OQAJ-_vUytlg&s',
  smoothie: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQV5dKjzCBSZeYQF5btsryWbEMEtowMm6un7A&s',
  wrap: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800&q=80&auto=format&fit=crop',
  parfait: 'https://images.unsplash.com/photo-1490474418585-ba9bad8fd0ea?w=800&q=80&auto=format&fit=crop',
  yoga: 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800&q=80&auto=format&fit=crop',
  run: 'https://images.stockcake.com/public/1/4/6/1465ef4d-3149-49a2-a8dc-21e14163366b_large/morning-jogging-routine-stockcake.jpg',
  strength: 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=800&q=80&auto=format&fit=crop',
  music1: 'https://i.ytimg.com/vi/IYLDF2-PvFg/maxresdefault.jpg',
  music2: 'https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=800&q=80&auto=format&fit=crop'
};

export const playlists = [
  { id: 1, title: 'Chill Vibes', subtitle: 'Relaxing tunes for a peaceful day', count: 20, image: demoImages.music1 },
  { id: 2, title: 'Workout Beats', subtitle: 'High-energy tracks to keep you motivated', count: 15, image: demoImages.music2 },
];

export const workouts = [
  { id: 1, title: 'Yoga Flow', duration: 25, image: demoImages.yoga, category: 'mobility' },
  { id: 2, title: 'Morning Run', duration: 20, image: demoImages.run, category: 'cardio' },
  { id: 3, title: 'Strength Circuit', duration: 18, image: demoImages.strength, category: 'strength' },
];

export const meals = [
  { id: 1, title: 'Healthy Salad', image: demoImages.meal, category: 'lunch' },
  { id: 2, title: 'Comforting Pasta', image: demoImages.pasta, category: 'dinner' },
  { id: 3, title: 'Protein Bowl', image: demoImages.bowl, category: 'lunch' },
  { id: 4, title: 'Berry Smoothie', image: demoImages.smoothie, category: 'breakfast' },
  { id: 5, title: 'Chicken Wrap', image: demoImages.wrap, category: 'dinner' },
  { id: 6, title: 'Yogurt Parfait', image: demoImages.parfait, category: 'snack' },
];

// Detailed mock recipes keyed by meal id
export const recipeDetails = {
  1: {
    id: 1,
    title: 'Healthy Salad',
    calories: 480,
    ingredients: [
      '2 cups mixed greens',
      '1/2 avocado, sliced',
      '1/2 cup cherry tomatoes',
      '1/4 cup chickpeas (rinsed)',
      '1 tbsp olive oil',
      '1 tsp lemon juice',
      'Salt & pepper to taste'
    ],
    steps: [
      'Rinse and dry greens and tomatoes.',
      'Combine greens, tomatoes, chickpeas in a bowl.',
      'Drizzle olive oil and lemon juice; season.',
      'Top with sliced avocado and serve.'
    ]
  },
  2: {
    id: 2,
    title: 'Comforting Pasta',
    calories: 620,
    ingredients: [
      '120g pasta',
      '1 cup tomato sauce',
      '1 clove garlic, minced',
      '1 tbsp olive oil',
      'Parmesan, to taste',
      'Salt & pepper'
    ],
    steps: [
      'Cook pasta per package until al dente.',
      'Saute garlic in olive oil 1 minute; add sauce.',
      'Simmer 5 minutes; combine with pasta.',
      'Top with parmesan; season and serve.'
    ]
  }
};

// Detailed mock workout plans keyed by workout id
export const workoutPlans = {
  1: {
    id: 1,
    title: 'Yoga Flow',
    steps: [
      { name: 'Sun Salutation A', minutes: 5 },
      { name: 'Warrior Sequence', minutes: 8 },
      { name: 'Balance Poses', minutes: 6 },
      { name: 'Cool Down', minutes: 6 }
    ]
  },
  2: {
    id: 2,
    title: 'Morning Run',
    steps: [
      { name: 'Warm-up Walk', minutes: 3 },
      { name: 'Easy Jog', minutes: 10 },
      { name: 'Intervals', minutes: 5 },
      { name: 'Cool Down Walk', minutes: 2 }
    ]
  },
  3: {
    id: 3,
    title: 'Strength Circuit',
    steps: [
      { name: 'Bodyweight Squats', minutes: 4 },
      { name: 'Push-ups', minutes: 3 },
      { name: 'Lunges', minutes: 4 },
      { name: 'Plank', minutes: 3 },
      { name: 'Stretch', minutes: 4 }
    ]
  }
};
