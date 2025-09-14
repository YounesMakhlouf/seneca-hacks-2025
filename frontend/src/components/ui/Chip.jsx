export default function Chip({ label, selected, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`px-3 py-1.5 rounded-full text-sm mr-2 mb-2 border transition-colors focus:outline-none focus:ring-2 focus:ring-primary/40 ${
        selected ? 'bg-primary text-white border-primary' : 'bg-white text-slate-700 border-slate-200 hover:border-slate-300'
      }`}
    >
      {label}
    </button>
  );
}
