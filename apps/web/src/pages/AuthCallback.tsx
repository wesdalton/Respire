import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Loader } from 'lucide-react';

export default function AuthCallback() {
  const navigate = useNavigate();
  const { setAuthFromCallback } = useAuth();

  useEffect(() => {
    const handleCallback = () => {
      // Supabase returns tokens in URL hash for OAuth
      const hash = window.location.hash.substring(1);
      const params = new URLSearchParams(hash);

      const accessToken = params.get('access_token');
      const refreshToken = params.get('refresh_token');
      const error = params.get('error');
      const errorDescription = params.get('error_description');

      if (error) {
        console.error('OAuth error:', error, errorDescription);
        navigate('/login?error=' + encodeURIComponent(errorDescription || error));
        return;
      }

      if (accessToken && refreshToken) {
        // Store tokens using AuthContext
        setAuthFromCallback(accessToken, refreshToken);
        // Redirect to dashboard
        navigate('/dashboard');
      } else {
        // No tokens found, redirect to login
        navigate('/login?error=' + encodeURIComponent('Authentication failed'));
      }
    };

    handleCallback();
  }, [navigate, setAuthFromCallback]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 flex items-center justify-center">
      <div className="text-center">
        <Loader className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Completing sign in...</h2>
        <p className="text-gray-600">Please wait while we set up your account</p>
      </div>
    </div>
  );
}
