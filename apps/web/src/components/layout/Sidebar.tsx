import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Heart, Clock, Lightbulb, Settings } from 'lucide-react';

interface NavItem {
  to: string;
  icon: React.ReactNode;
  label: string;
}

const navItems: NavItem[] = [
  { to: '/dashboard', icon: <LayoutDashboard className="w-5 h-5" />, label: 'Dashboard' },
  { to: '/mood', icon: <Heart className="w-5 h-5" />, label: 'Mood' },
  { to: '/history', icon: <Clock className="w-5 h-5" />, label: 'History' },
  { to: '/insights', icon: <Lightbulb className="w-5 h-5" />, label: 'Insights' },
  { to: '/settings', icon: <Settings className="w-5 h-5" />, label: 'Settings' },
];

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  return (
    <>
      {/* Backdrop - only visible on mobile when open */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/20 z-30 lg:hidden backdrop-blur-sm"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed lg:static inset-y-0 left-0 z-40
          w-64 bg-white border-r border-gray-200
          transform transition-transform duration-300 ease-in-out
          lg:translate-x-0
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        <nav className="flex flex-col h-full py-6 px-4 space-y-2 mt-16 lg:mt-0">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors duration-150 ${
                  isActive
                    ? 'bg-blue-50 text-blue-600'
                    : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                }`
              }
            >
              {item.icon}
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>
    </>
  );
}
