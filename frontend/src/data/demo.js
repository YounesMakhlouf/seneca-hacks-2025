export const demoImages = {
  welcome: 'https://images.unsplash.com/photo-1518609878373-06d740f60d8b?w=800&q=80&auto=format&fit=crop',
  meal: 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=800&q=80&auto=format&fit=crop',
  pasta: 'https://images.unsplash.com/photo-1525755662778-989d0524087e?w=800&q=80&auto=format&fit=crop',
  yoga: 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800&q=80&auto=format&fit=crop',
  run: 'https://images.unsplash.com/photo-1517963628607-235ccdd5476e?w=800&q=80&auto=format&fit=crop',
  music1: 'https://images.unsplash.com/photo-1483412033650-1015ddeb83d4?w=800&q=80&auto=format&fit=crop',
  music2: 'https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=800&q=80&auto=format&fit=crop'
};

export const playlists = [
  { id: 1, title: 'Chill Vibes', subtitle: 'Relaxing tunes for a peaceful day', count: 20, image: demoImages.music1 },
  { id: 2, title: 'Workout Beats', subtitle: 'High-energy tracks to keep you motivated', count: 15, image: demoImages.music2 },
];

export const workouts = [
  { id: 1, title: 'Yoga Flow', duration: 25, image: demoImages.yoga },
  { id: 2, title: 'Morning Run', duration: 20, image: demoImages.run },
];

export const meals = [
  { id: 1, title: 'Healthy Salad', image: demoImages.meal },
  { id: 2, title: 'Comforting Pasta', image: demoImages.pasta },
];
