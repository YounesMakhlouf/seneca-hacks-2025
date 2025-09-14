export default function Button({ children, className = '', variant = 'primary', ...props }) {
  const variants = {
    primary: 'bg-primary text-white hover:bg-primary-dark active:scale-[0.99] shadow-sm',
    outline: 'bg-white text-ink border border-slate-200 hover:border-slate-300 active:scale-[0.99]',
    ghost: 'bg-transparent text-ink hover:bg-slate-100/60',
  };
  return (
    <button
      className={`w-full rounded-xl px-4 py-3 font-semibold transition-colors duration-150 ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
