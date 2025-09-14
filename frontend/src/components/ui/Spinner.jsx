export default function Spinner({ size = 20 }) {
  const s = typeof size === 'number' ? `${size}px` : size;
  return (
    <span
      role="status"
      className="inline-block animate-spin rounded-full border-2 border-slate-300 border-t-primary"
      style={{ width: s, height: s }}
    />
  );
}
