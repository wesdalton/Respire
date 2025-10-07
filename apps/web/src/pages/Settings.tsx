import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { apiClient } from '../services/api';
import { User, Settings as SettingsIcon, Link as LinkIcon, LogOut, AlertCircle, CheckCircle, Loader } from 'lucide-react';
import type { WHOOPConnection } from '../types';

export default function Settings() {
  const { user, signout } = useAuth();
  const [whoopConnection, setWhoopConnection] = useState<WHOOPConnection | null>(null);
  const [loadingWhoop, setLoadingWhoop] = useState(true);
  const [disconnecting, setDisconnecting] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    loadWhoopConnection();
  }, []);

  const loadWhoopConnection = async () => {
    try {
      setLoadingWhoop(true);
      const connection = await apiClient.getWHOOPConnection();
      setWhoopConnection(connection);
    } catch (err: any) {
      if (err.response?.status !== 404) {
        console.error('Failed to load WHOOP connection:', err);
      }
    } finally {
      setLoadingWhoop(false);
    }
  };

  const handleConnectWhoop = async () => {
    try {
      setError('');
      const redirectUri = `${window.location.origin}/settings/whoop/callback`;
      console.log('WHOOP Redirect URI:', redirectUri);
      const { authorization_url } = await apiClient.getWHOOPAuthURL(redirectUri);
      console.log('WHOOP Auth URL:', authorization_url);
      window.location.href = authorization_url;
    } catch (err: any) {
      console.error('WHOOP connect error:', err);
      setError(err.response?.data?.detail || 'Failed to connect to WHOOP');
    }
  };

  const handleDisconnectWhoop = async () => {
    if (!confirm('Are you sure you want to disconnect your WHOOP account?')) {
      return;
    }

    try {
      setError('');
      setDisconnecting(true);
      await apiClient.disconnectWHOOP();
      setWhoopConnection(null);
      setSuccessMessage('WHOOP account disconnected successfully');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to disconnect WHOOP');
    } finally {
      setDisconnecting(false);
    }
  };

  const handleSignOut = async () => {
    try {
      await signout();
    } catch (err) {
      console.error('Failed to sign out:', err);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Settings</h1>
          <p className="text-gray-600">Manage your account and preferences</p>
        </div>

        {/* Messages */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        {successMessage && (
          <div className="mb-6 bg-green-50 border border-green-200 rounded-xl p-4 flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            <p className="text-green-800 text-sm">{successMessage}</p>
          </div>
        )}

        <div className="space-y-6">
          {/* Account Section */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <User className="w-5 h-5 text-blue-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900">Account</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-500 mb-1">Email</label>
                <p className="text-gray-900">{user?.email || 'Not available'}</p>
              </div>

              {user?.user_metadata?.first_name && (
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">Name</label>
                  <p className="text-gray-900">
                    {user.user_metadata.first_name} {user.user_metadata.last_name || ''}
                  </p>
                </div>
              )}

              {user?.created_at && (
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">Member Since</label>
                  <p className="text-gray-900">
                    {new Date(user.created_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* WHOOP Connection Section */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <LinkIcon className="w-5 h-5 text-purple-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900">WHOOP Connection</h2>
            </div>

            {loadingWhoop ? (
              <div className="flex items-center gap-3 text-gray-600">
                <Loader className="w-5 h-5 animate-spin" />
                <span>Loading connection status...</span>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <label className="block text-sm font-medium text-gray-500 mb-1">Status</label>
                    <div className="flex items-center gap-2">
                      {whoopConnection ? (
                        <>
                          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                          <span className="text-gray-900 font-medium">Connected</span>
                        </>
                      ) : (
                        <>
                          <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                          <span className="text-gray-900 font-medium">Not Connected</span>
                        </>
                      )}
                    </div>
                  </div>

                  {whoopConnection ? (
                    <button
                      onClick={handleDisconnectWhoop}
                      disabled={disconnecting}
                      className="px-4 py-2 border border-red-300 text-red-700 rounded-lg hover:bg-red-50 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                    >
                      {disconnecting ? 'Disconnecting...' : 'Disconnect'}
                    </button>
                  ) : (
                    <button
                      onClick={handleConnectWhoop}
                      className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition font-medium"
                    >
                      Connect WHOOP
                    </button>
                  )}
                </div>

                {whoopConnection && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-500 mb-1">Connected At</label>
                      <p className="text-gray-900">
                        {new Date(whoopConnection.connected_at).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </p>
                    </div>

                    {whoopConnection.last_synced_at && (
                      <div>
                        <label className="block text-sm font-medium text-gray-500 mb-1">Last Synced</label>
                        <p className="text-gray-900">
                          {new Date(whoopConnection.last_synced_at).toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </p>
                      </div>
                    )}

                    <div>
                      <label className="block text-sm font-medium text-gray-500 mb-1">Auto-Sync</label>
                      <p className="text-gray-900">
                        {whoopConnection.sync_enabled ? 'Enabled' : 'Disabled'}
                      </p>
                    </div>
                  </>
                )}

                {!whoopConnection && (
                  <p className="text-sm text-gray-600 mt-4">
                    Connect your WHOOP account to automatically sync your health data and get personalized burnout predictions.
                  </p>
                )}
              </div>
            )}
          </div>

          {/* Preferences Section */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                <SettingsIcon className="w-5 h-5 text-gray-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900">Preferences</h2>
            </div>

            <div className="text-gray-600 text-sm">
              <p>Preference settings coming soon...</p>
            </div>
          </div>

          {/* Danger Zone */}
          <div className="bg-white rounded-xl shadow-sm border border-red-200 p-6">
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-red-900 mb-1">Danger Zone</h2>
              <p className="text-sm text-gray-600">Irreversible actions for your account</p>
            </div>

            <button
              onClick={handleSignOut}
              className="w-full sm:w-auto px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition flex items-center justify-center gap-2 font-medium"
            >
              <LogOut className="w-5 h-5" />
              Sign Out
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
