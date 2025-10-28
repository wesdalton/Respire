import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { usePageTitle } from '../hooks/usePageTitle';
import { apiClient } from '../services/api';
import { Settings as SettingsIcon, Link as LinkIcon, LogOut, AlertCircle, CheckCircle, Loader, Save, Trash2, X } from 'lucide-react';
import { Avatar } from '../components/common/Avatar';
import { formatDateTime } from '../utils/dateUtils';
import type { WHOOPConnection, OuraConnection } from '../types';

export default function Settings() {
  usePageTitle('Settings');
  const { user, signout } = useAuth();
  const [whoopConnection, setWhoopConnection] = useState<WHOOPConnection | null>(null);
  const [ouraConnection, setOuraConnection] = useState<OuraConnection | null>(null);
  const [loadingWhoop, setLoadingWhoop] = useState(true);
  const [loadingOura, setLoadingOura] = useState(true);
  const [disconnecting, setDisconnecting] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [primaryDevice, setPrimaryDevice] = useState<'whoop' | 'oura'>('whoop');
  const [changingPrimary, setChangingPrimary] = useState(false);

  // Profile editing state
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [editedFirstName, setEditedFirstName] = useState('');
  const [editedLastName, setEditedLastName] = useState('');
  const [editedProfilePictureUrl, setEditedProfilePictureUrl] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>('');
  const [savingProfile, setSavingProfile] = useState(false);

  // Delete account state
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    loadConnections();
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    try {
      const prefs = await apiClient.getUserPreferences();
      setPrimaryDevice(prefs.primary_data_source || 'whoop');
    } catch (error) {
      console.error('Failed to load preferences:', error);
    }
  };

  const handleChangePrimaryDevice = async (device: 'whoop' | 'oura') => {
    setChangingPrimary(true);
    try {
      await apiClient.updateUserPreferences({ primary_data_source: device });
      setPrimaryDevice(device);
      setSuccessMessage(`Primary device changed to ${device.toUpperCase()}`);
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to change primary device');
    } finally {
      setChangingPrimary(false);
    }
  };

  const loadConnections = async () => {
    setLoadingWhoop(true);
    setLoadingOura(true);
    try {
      const [whoop, oura] = await Promise.all([
        apiClient.getWHOOPConnection().catch(err => {
          if (err.response?.status !== 404) {
            console.error('Failed to load WHOOP connection:', err);
          }
          return null;
        }),
        apiClient.getOuraConnection().catch(err => {
          if (err.response?.status !== 404) {
            console.error('Failed to load Oura connection:', err);
          }
          return null;
        }),
      ]);
      setWhoopConnection(whoop);
      setOuraConnection(oura);
    } catch (error) {
      console.error('Failed to load connections:', error);
    } finally {
      setLoadingWhoop(false);
      setLoadingOura(false);
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

  const handleConnectOura = async () => {
    try {
      setError('');
      const redirectUri = `${window.location.origin}/settings/oura/callback`;
      console.log('Oura Redirect URI:', redirectUri);
      const { authorization_url } = await apiClient.getOuraAuthURL(redirectUri);
      console.log('Oura Auth URL:', authorization_url);
      window.location.href = authorization_url;
    } catch (err: any) {
      console.error('Oura connect error:', err);
      setError(err.response?.data?.detail || 'Failed to connect to Oura');
    }
  };

  const handleDisconnectOura = async () => {
    if (!confirm('Are you sure you want to disconnect your Oura Ring?')) {
      return;
    }

    try {
      setError('');
      setDisconnecting(true);
      await apiClient.disconnectOura();
      setOuraConnection(null);
      setSuccessMessage('Oura Ring disconnected successfully');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to disconnect Oura');
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

  const handleEditProfile = () => {
    setEditedFirstName(user?.user_metadata?.first_name || '');
    setEditedLastName(user?.user_metadata?.last_name || '');
    setEditedProfilePictureUrl(user?.user_metadata?.profile_picture_url || '');
    setPreviewUrl(user?.user_metadata?.profile_picture_url || '');
    setIsEditingProfile(true);
    setError('');
    setSuccessMessage('');
  };

  const handleCancelEdit = () => {
    setIsEditingProfile(false);
    setEditedFirstName('');
    setEditedLastName('');
    setEditedProfilePictureUrl('');
    setSelectedFile(null);
    setPreviewUrl('');
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setError('Please select an image file');
        return;
      }

      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setError('Image size must be less than 5MB');
        return;
      }

      setSelectedFile(file);
      setError('');

      // Create preview URL
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSaveProfile = async () => {
    try {
      setSavingProfile(true);
      setError('');

      // If a file was selected, upload it first
      let profilePictureUrl = editedProfilePictureUrl;
      if (selectedFile) {
        const uploadedUrl = await apiClient.uploadProfilePicture(selectedFile);
        profilePictureUrl = uploadedUrl;
      }

      await apiClient.updateProfile({
        first_name: editedFirstName,
        last_name: editedLastName,
        profile_picture_url: profilePictureUrl,
      });
      setSuccessMessage('Profile updated successfully!');
      setIsEditingProfile(false);
      setTimeout(() => setSuccessMessage(''), 3000);
      // Reload the page to fetch updated user data
      window.location.reload();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update profile');
    } finally {
      setSavingProfile(false);
    }
  };

  const handleDeleteAllData = async () => {
    if (deleteConfirmText !== 'ERASE') {
      return;
    }

    try {
      setIsDeleting(true);
      setError('');

      await apiClient.deleteAllUserData();

      // Sign out and redirect to login
      await signout();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete account data');
      setIsDeleting(false);
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
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <Avatar
                  src={user?.user_metadata?.profile_picture_url}
                  alt={user?.user_metadata?.first_name || user?.email}
                  size="md"
                />
                <h2 className="text-xl font-semibold text-gray-900">Account</h2>
              </div>
              {!isEditingProfile && (
                <button
                  onClick={handleEditProfile}
                  className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition"
                >
                  Edit Profile
                </button>
              )}
            </div>

            {isEditingProfile ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      First Name
                    </label>
                    <input
                      type="text"
                      value={editedFirstName}
                      onChange={(e) => setEditedFirstName(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Last Name
                    </label>
                    <input
                      type="text"
                      value={editedLastName}
                      onChange={(e) => setEditedLastName(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Profile Picture <span className="text-gray-400 text-xs">(optional)</span>
                  </label>
                  <div className="flex items-center gap-4">
                    {previewUrl && (
                      <Avatar src={previewUrl} alt="Preview" size="lg" />
                    )}
                    <div className="flex-1">
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleFileChange}
                        className="block w-full text-sm text-gray-500
                          file:mr-4 file:py-2 file:px-4
                          file:rounded-lg file:border-0
                          file:text-sm file:font-medium
                          file:bg-blue-50 file:text-blue-700
                          hover:file:bg-blue-100
                          file:cursor-pointer cursor-pointer"
                      />
                      <p className="mt-1 text-xs text-gray-500">
                        Upload an image (max 5MB)
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex gap-3 pt-2">
                  <button
                    onClick={handleSaveProfile}
                    disabled={savingProfile}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                  >
                    <Save className="w-4 h-4" />
                    {savingProfile ? 'Saving...' : 'Save Changes'}
                  </button>
                  <button
                    onClick={handleCancelEdit}
                    disabled={savingProfile}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
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
            )}
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
                        {formatDateTime(whoopConnection.connected_at)}
                      </p>
                    </div>

                    {whoopConnection.last_synced_at && (
                      <div>
                        <label className="block text-sm font-medium text-gray-500 mb-1">Last Synced</label>
                        <p className="text-gray-900">
                          {formatDateTime(whoopConnection.last_synced_at)}
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

          {/* Oura Connection Section */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <span className="text-2xl">⭕</span>
              </div>
              <h2 className="text-xl font-semibold text-gray-900">Oura Ring Connection</h2>
            </div>

            {loadingOura ? (
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
                      {ouraConnection ? (
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

                  {ouraConnection ? (
                    <button
                      onClick={handleDisconnectOura}
                      disabled={disconnecting}
                      className="px-4 py-2 border border-red-300 text-red-700 rounded-lg hover:bg-red-50 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                    >
                      {disconnecting ? 'Disconnecting...' : 'Disconnect'}
                    </button>
                  ) : (
                    <button
                      onClick={handleConnectOura}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
                    >
                      Connect Oura
                    </button>
                  )}
                </div>

                {ouraConnection && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-500 mb-1">Connected At</label>
                      <p className="text-gray-900">
                        {new Date(ouraConnection.connected_at).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </p>
                    </div>

                    {ouraConnection.last_synced_at && (
                      <div>
                        <label className="block text-sm font-medium text-gray-500 mb-1">Last Synced</label>
                        <p className="text-gray-900">
                          {new Date(ouraConnection.last_synced_at).toLocaleDateString('en-US', {
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
                        {ouraConnection.sync_enabled ? 'Enabled' : 'Disabled'}
                      </p>
                    </div>
                  </>
                )}

                {!ouraConnection && (
                  <p className="text-sm text-gray-600 mt-4">
                    Connect your Oura Ring to automatically sync your health data and get personalized burnout predictions.
                  </p>
                )}
              </div>
            )}
          </div>

          {/* Primary Device Selector */}
          {whoopConnection && ouraConnection && (
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <SettingsIcon className="w-5 h-5 text-blue-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900">Primary Data Source</h3>
              </div>
              <p className="text-sm text-gray-600 mb-4">
                Both WHOOP and Oura are connected. Choose which device should be your primary source for health metrics.
                Only your primary device will sync data to prevent conflicts.
              </p>
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => handleChangePrimaryDevice('whoop')}
                  disabled={changingPrimary || primaryDevice === 'whoop'}
                  className={`p-4 rounded-lg border-2 transition ${
                    primaryDevice === 'whoop'
                      ? 'border-purple-600 bg-purple-50'
                      : 'border-gray-200 hover:border-purple-300'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-lg">💪</span>
                    {primaryDevice === 'whoop' && (
                      <CheckCircle className="w-5 h-5 text-purple-600" />
                    )}
                  </div>
                  <p className="font-semibold text-gray-900">WHOOP</p>
                  <p className="text-xs text-gray-600 mt-1">
                    {primaryDevice === 'whoop' ? 'Current primary' : 'Set as primary'}
                  </p>
                </button>
                <button
                  onClick={() => handleChangePrimaryDevice('oura')}
                  disabled={changingPrimary || primaryDevice === 'oura'}
                  className={`p-4 rounded-lg border-2 transition ${
                    primaryDevice === 'oura'
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-200 hover:border-blue-300'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-lg">⭕</span>
                    {primaryDevice === 'oura' && (
                      <CheckCircle className="w-5 h-5 text-blue-600" />
                    )}
                  </div>
                  <p className="font-semibold text-gray-900">Oura Ring</p>
                  <p className="text-xs text-gray-600 mt-1">
                    {primaryDevice === 'oura' ? 'Current primary' : 'Set as primary'}
                  </p>
                </button>
              </div>
            </div>
          )}

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

            <div className="space-y-3">
              <button
                onClick={handleSignOut}
                className="w-full sm:w-auto px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition flex items-center justify-center gap-2 font-medium"
              >
                <LogOut className="w-5 h-5" />
                Sign Out
              </button>

              <button
                onClick={() => setShowDeleteModal(true)}
                className="w-full sm:w-auto px-6 py-3 bg-white text-red-600 border-2 border-red-600 rounded-lg hover:bg-red-50 transition flex items-center justify-center gap-2 font-medium"
              >
                <Trash2 className="w-5 h-5" />
                Delete All Account Data
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                  <Trash2 className="w-6 h-6 text-red-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Delete All Account Data</h3>
                </div>
              </div>
              <button
                onClick={() => {
                  setShowDeleteModal(false);
                  setDeleteConfirmText('');
                }}
                className="text-gray-400 hover:text-gray-600 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="mb-6">
              <p className="text-sm text-gray-700 mb-4">
                This action will <span className="font-semibold text-red-600">permanently delete</span>:
              </p>
              <ul className="text-sm text-gray-600 space-y-2 mb-4">
                <li className="flex items-start gap-2">
                  <span className="text-red-500 mt-0.5">•</span>
                  <span>All your health metrics and wearable data</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-500 mt-0.5">•</span>
                  <span>All mood ratings and journal entries</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-500 mt-0.5">•</span>
                  <span>All AI-generated insights and recommendations</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-500 mt-0.5">•</span>
                  <span>Your WHOOP and Oura connections</span>
                </li>
              </ul>
              <p className="text-sm text-gray-700 font-medium mb-4">
                This action cannot be undone. Your account will remain active, but all data will be erased.
              </p>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Type <span className="font-mono bg-gray-100 px-1.5 py-0.5 rounded text-red-600">ERASE</span> to confirm
                </label>
                <input
                  type="text"
                  value={deleteConfirmText}
                  onChange={(e) => setDeleteConfirmText(e.target.value)}
                  placeholder="Type ERASE here"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  disabled={isDeleting}
                />
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowDeleteModal(false);
                  setDeleteConfirmText('');
                }}
                disabled={isDeleting}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteAllData}
                disabled={deleteConfirmText !== 'ERASE' || isDeleting}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {isDeleting ? 'Deleting...' : 'Delete All Data'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
