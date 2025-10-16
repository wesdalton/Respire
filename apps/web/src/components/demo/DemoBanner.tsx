import { Link } from 'react-router-dom';
import { useDemo } from '../../context/DemoContext';

export function DemoBanner() {
  const { isDemoMode, exitDemo, resetDemo } = useDemo();

  if (!isDemoMode) {
    return null;
  }

  return (
    <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-4 py-2.5 shadow-md">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-lg">🎮</span>
          <span className="text-sm font-medium">
            You're exploring a demo account with simulated data
          </span>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={resetDemo}
            className="text-xs text-white/90 hover:text-white underline transition-colors"
          >
            Reset Demo
          </button>
          <button
            onClick={exitDemo}
            className="text-xs text-white/90 hover:text-white underline transition-colors"
          >
            Exit Demo
          </button>
          <Link
            to="/signup"
            className="text-xs bg-white text-purple-600 px-4 py-1.5 rounded-full font-semibold hover:bg-gray-100 transition-colors"
            onClick={exitDemo}
          >
            Create Account
          </Link>
        </div>
      </div>
    </div>
  );
}
