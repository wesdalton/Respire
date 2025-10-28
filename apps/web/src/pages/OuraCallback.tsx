import { useEffect, useState, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { usePageTitle } from '../hooks/usePageTitle';
import { apiClient } from '../services/api';
import { Loader, AlertCircle, CheckCircle } from 'lucide-react';

export default function OuraCallback() {
  usePageTitle('Connecting Oura');
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('Connecting to Oura...');
  const hasRun = useRef(false);

  useEffect(() => {
    // Prevent double execution in React Strict Mode
    if (hasRun.current) return;
    hasRun.current = true;

    const handleCallback = async () => {
      const code = searchParams.get('code');
      const error = searchParams.get('error');
      const errorDescription = searchParams.get('error_description');

      if (error) {
        console.error('OAuth error:', error, errorDescription);
        setStatus('error');
        setMessage(errorDescription || `Oura authorization failed: ${error}`);
        setTimeout(() => navigate('/dashboard'), 3000);
        return;
      }

      if (!code) {
        setStatus('error');
        setMessage('No authorization code received from Oura');
        setTimeout(() => navigate('/dashboard'), 3000);
        return;
      }

      try {
        const redirectUri = `${window.location.origin}/settings/oura/callback`;
        console.log('Oura Callback - Code:', code);
        console.log('Oura Callback - Redirect URI:', redirectUri);
        await apiClient.connectOura(code, redirectUri);
        setStatus('success');
        setMessage('Successfully connected to Oura!');
        setTimeout(() => navigate('/dashboard'), 2000);
      } catch (err: any) {
        console.error('Oura callback error:', err);
        setStatus('error');
        setMessage(err.response?.data?.detail || 'Failed to connect to Oura');
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
              <h2 className="text-xl font-semibold text-gray-900">Connecting to Oura</h2>
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
