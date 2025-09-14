import { useNavigate } from 'react-router-dom';
import Button from '../components/ui/Button';

export default function Login() {
  const navigate = useNavigate();
  return (
    <div className="px-4 pt-4">
      <button onClick={() => navigate(-1)} className="text-2xl">←</button>
      <h2 className="text-center text-xl font-bold my-4">Login</h2>
      <div className="space-y-4">
        <input className="w-full rounded-xl border border-slate-300 px-4 py-3" placeholder="Email or Username" />
        <input className="w-full rounded-xl border border-slate-300 px-4 py-3" placeholder="Password" type="password" />
        <p className="text-center text-sm text-slate-500">Forgot Password?</p>
        <Button onClick={() => navigate('/preferences')}>Login</Button>
        <p className="text-center text-sm text-slate-500">
          Don't have an account?{' '}
          <button className="text-primary" onClick={() => navigate('/preferences')}>Sign Up</button>
        </p>
      </div>
    </div>
  );
}
