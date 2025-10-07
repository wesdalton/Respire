import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Sidebar } from './Sidebar';

interface LayoutProps {
  children?: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen);
  const closeSidebar = () => setIsSidebarOpen(false);

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <Header onMenuClick={toggleSidebar} />

      {/* Main Content Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <Sidebar isOpen={isSidebarOpen} onClose={closeSidebar} />

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children || <Outlet />}
          </div>
        </main>
      </div>
    </div>
  );
}
