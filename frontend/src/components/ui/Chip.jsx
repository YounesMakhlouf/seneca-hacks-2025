export default function Chip({ label, selected, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`px-3 py-1.5 rounded-full text-sm mr-2 mb-2 border transition ${
        selected ? 'bg-primary text-white border-primary' : 'bg-white text-slate-700 border-slate-200'
      }`}
    >
      {label}
    </button>
  );
}
