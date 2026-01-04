import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-30 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="bg-primary/10 p-2 rounded-lg">
            <span className="material-symbols-outlined text-primary">hub</span>
          </div>
          <h1 className="text-lg font-bold tracking-tight text-slate-900 dark:text-white">IoT Monitor</h1>
          <div className="hidden md:block h-6 w-px bg-slate-200 dark:bg-slate-700 mx-2"></div>
          <div className="hidden md:flex items-center gap-2 px-2 py-1 bg-green-50 dark:bg-green-900/20 rounded-full border border-green-100 dark:border-green-800/30">
            <span className="relative flex h-2 w-2 ml-1">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
            </span>
            <span className="text-xs font-medium text-green-700 dark:text-green-400 pr-1">Cassandra DB Live</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
