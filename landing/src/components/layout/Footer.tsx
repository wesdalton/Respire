import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="py-8 px-4 bg-gray-50 border-t border-gray-200">
      <div className="max-w-6xl mx-auto text-center">
        <p className="text-gray-600 text-sm">
          © {new Date().getFullYear()} Respire. Built by Wes Dalton as a passion project.
        </p>
        <p className="text-gray-500 text-xs mt-2">
          UPenn Computer Science '26
        </p>
      </div>
    </footer>
  );
};