export default function Modal({ open, onClose, title, children, footer }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />
      <div className="relative bg-white w-full sm:w-[420px] rounded-t-2xl sm:rounded-2xl shadow-xl p-4">
        {title && <h3 className="text-lg font-bold mb-2">{title}</h3>}
        <div className="text-sm text-slate-700">{children}</div>
        {footer && <div className="mt-4">{footer}</div>}
      </div>
    </div>
  );
}
