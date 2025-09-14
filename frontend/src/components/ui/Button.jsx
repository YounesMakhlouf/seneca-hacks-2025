export default function Button({ children, className = '', variant = 'primary', ...props }) {
  const variants = {
    primary: 'bg-primary text-white hover:bg-primary-dark',
    outline: 'bg-white text-ink border border-slate-200',
    ghost: 'bg-transparent text-ink',
  };
  return (
    <button
      className={`w-full rounded-xl px-4 py-3 font-semibold shadow-sm transition ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
