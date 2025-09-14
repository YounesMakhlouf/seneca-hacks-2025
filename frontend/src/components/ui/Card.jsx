export default function Card({ children, className = '' }) {
  return (
    <div className={`bg-white rounded-xl shadow-card border border-slate-100 ${className}`}>{children}</div>
  );
}
