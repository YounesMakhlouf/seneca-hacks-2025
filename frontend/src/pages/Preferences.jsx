import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Chip from '../components/ui/Chip';
import Button from '../components/ui/Button';

const sections = {
  Music: ['Pop', 'Electronic', 'Classical', 'Jazz', 'Hip Hop', 'Folk'],
  Meals: ['Vegan', 'Vegetarian', 'Gluten-Free', 'Keto', 'Paleo', 'Pescatarian'],
  Workouts: ['Yoga', 'Pilates', 'HIIT', 'Strength Training', 'Cardio', 'Dance'],
  'Wellness Goals': ['Stress Relief', 'Improved Sleep', 'Increased Energy', 'Mindfulness', 'Better Focus', 'Weight Management'],
};

export default function Preferences() {
  const [prefs, setPrefs] = useState({});
  const navigate = useNavigate();

  const toggle = (section, item) => {
    setPrefs((p) => {
      const set = new Set(p[section] || []);
      set.has(item) ? set.delete(item) : set.add(item);
      return { ...p, [section]: Array.from(set) };
    });
  };

  return (
    <div className="px-4 pt-4 pb-24">
      <button onClick={() => navigate(-1)} className="text-xl">←</button>
      <h2 className="text-center text-xl font-bold mb-4">Preferences</h2>
      {Object.entries(sections).map(([title, items]) => (
        <section key={title} className="mb-4">
          <h3 className="font-semibold text-lg mb-2">{title}</h3>
          <div>
            {items.map((i) => (
              <Chip key={i} label={i} selected={(prefs[title] || []).includes(i)} onClick={() => toggle(title, i)} />
            ))}
          </div>
        </section>
      ))}

      <div className="fixed bottom-20 left-0 right-0 mobile-shell mx-auto px-4">
        <Button onClick={() => navigate('/dashboard')}>Save Preferences</Button>
      </div>
    </div>
  );
}
