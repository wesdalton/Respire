import { useEffect, useState, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { usePageTitle } from '../hooks/usePageTitle';
import { apiClient } from '../services/api';
import { Loader, AlertCircle, CheckCircle } from 'lucide-react';

export default function WHOOPCallback() {
  usePageTitle('Connecting WHOOP');
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('Connecting to WHOOP...');
  const hasRun = useRef(false);

  useEffect(() => {
    // Prevent double execution in React Strict Mode
    if (hasRun.current) return;
    hasRun.current = true;

    const handleCallback = async () => {
      const code = searchParams.get('code');
      const error = searchParams.get('error');

      if (error) {
        setStatus('error');
        setMessage(`WHOOP authorization failed: ${error}`);
        setTimeout(() => navigate('/dashboard'), 3000);
        return;
      }

      if (!code) {
        setStatus('error');
        setMessage('No authorization code received from WHOOP');
        setTimeout(() => navigate('/dashboard'), 3000);
        return;
      }

      try {
        const redirectUri = `${window.location.origin}/settings/whoop/callback`;
        console.log('WHOOP Callback - Code:', code);
        console.log('WHOOP Callback - Redirect URI:', redirectUri);
        await apiClient.connectWHOOP(code, redirectUri);
        setStatus('success');
        setMessage('Successfully connected to WHOOP!');
        setTimeout(() => navigate('/dashboard'), 2000);
      } catch (err: any) {
        console.error('WHOOP callback error:', err);
        setStatus('error');
        setMessage(err.response?.data?.detail || 'Failed to connect to WHOOP');
        setTimeout(() => navigate('/dashboard'), 3000);
      }
    };

    handleCallback();
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 flex items-center justify-center p-6">
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8 max-w-md w-full">
        <div className="flex flex-col items-center text-center space-y-4">
          {status === 'loading' && (
            <>
              <Loader className="w-12 h-12 text-purple-600 animate-spin" />
              <h2 className="text-xl font-semibold text-gray-900">Connecting to WHOOP</h2>
              <p className="text-gray-600">{message}</p>
            </>
          )}

          {status === 'success' && (
            <>
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900">Success!</h2>
              <p className="text-gray-600">{message}</p>
              <p className="text-sm text-gray-500">Redirecting to dashboard...</p>
            </>
          )}

          {status === 'error' && (
            <>
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                <AlertCircle className="w-8 h-8 text-red-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900">Connection Failed</h2>
              <p className="text-gray-600">{message}</p>
              <p className="text-sm text-gray-500">Redirecting to dashboard...</p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
