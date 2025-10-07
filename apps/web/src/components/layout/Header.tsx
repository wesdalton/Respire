import { Activity, LogOut, Menu } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { Avatar } from '../common/Avatar';

interface HeaderProps {
  onMenuClick: () => void;
}

export function Header({ onMenuClick }: HeaderProps) {
  const { user, signout } = useAuth();

  const handleSignout = async () => {
    try {
      await signout();
    } catch (error) {
      console.error('Signout error:', error);
    }
  };

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="flex items-center justify-between px-4 sm:px-6 lg:px-8 h-16">
        {/* Left side: Menu button + Logo */}
        <div className="flex items-center space-x-3">
          {/* Mobile Menu Button */}
          <button
            onClick={onMenuClick}
            className="lg:hidden p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Toggle navigation menu"
          >
            <Menu className="w-6 h-6" />
          </button>

          {/* Logo and Brand */}
          <div className="flex items-center space-x-2">
            <Activity className="w-6 h-6 text-blue-600" />
            <span className="text-xl font-semibold text-gray-900">Respire</span>
          </div>
        </div>

        {/* Right side: User Info and Logout */}
        <div className="flex items-center space-x-4">
          {user && (
            <div className="hidden sm:flex items-center space-x-3">
              <Avatar
                src={user.user_metadata?.profile_picture_url}
                alt={user.user_metadata?.first_name || user.email}
                size="sm"
              />
              <span className="text-sm text-gray-900 font-semibold">
                {user.user_metadata?.first_name && user.user_metadata?.last_name
                  ? `${user.user_metadata.first_name} ${user.user_metadata.last_name}`
                  : user.user_metadata?.first_name || user.email}
              </span>
            </div>
          )}
          <button
            onClick={handleSignout}
            className="flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors duration-150"
            aria-label="Sign out"
          >
            <LogOut className="w-4 h-4" />
            <span className="hidden sm:inline">Logout</span>
          </button>
        </div>
      </div>
    </header>
  );
}
