import { Link } from 'react-router-dom';

export default function Settings() {
  return (
    <div className="px-4 pt-4 pb-24 space-y-3">
      <h2 className="text-xl font-bold">Settings</h2>
      <div className="bg-white border rounded-xl p-3">
        <p className="font-semibold">Account</p>
        <ul className="list-disc pl-5 text-sm text-slate-600">
          <li><Link to="/login" className="text-primary">Login</Link></li>
          <li><Link to="/" className="text-primary">Welcome</Link></li>
          <li><Link to="/form-corrector" className="text-primary">Open Form Corrector (Upload)</Link></li>
          <li><Link to="/live-coach" className="text-primary">Open Live Coach (Camera)</Link></li>
        </ul>
      </div>
    </div>
  );
}
