import React from 'react';

const Header = () => {
  return (
    <header className="bg-gray-800 border-b border-gray-700">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="text-3xl">♿</div>
            <div>
              <h1 className="text-2xl font-bold text-green-400">ACCESSIBLE NAVIGATOR</h1>
              <p className="text-gray-400 text-sm">Voice-Guided Navigation for the Visually Impaired</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4 text-sm text-gray-400">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span>Voice Ready</span>
            </div>
            <div className="text-xs">
              Screen Reader Compatible
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
