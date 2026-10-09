import React from 'react';
import { Shield, Search, Bell, User } from 'lucide-react';

export default function Navbar({ searchTerm, setSearchTerm, isBackendOnline, currentUser, onOpenAuthModal, onLogout }) {
  return (
    <header className="sticky top-0 z-40 w-full bg-white border-b border-slate-200 px-6 py-3 shadow-sm">
      <div className="flex items-center justify-between max-w-[1600px] mx-auto gap-4">
        {/* Brand Logo & Tagline */}
        <div className="flex items-center gap-3 shrink-0">
          <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-base tracking-tight text-slate-900 font-sans">
                ProofMind <span className="text-blue-600">AI</span>
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium">
              Every decision needs evidence.
            </p>
          </div>
        </div>

        {/* Global Search Bar */}
        <div className="flex-1 max-w-xl mx-4 hidden sm:block">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-2.5" />
            <input
              type="text"
              value={searchTerm || ''}
              onChange={(e) => setSearchTerm && setSearchTerm(e.target.value)}
              placeholder="Search documents, analyses, or evidence..."
              className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-100 border border-slate-200 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:bg-white focus:border-blue-500 transition-all font-sans"
            />
          </div>
        </div>

        {/* Status, Notification Bell & User Profile */}
        <div className="flex items-center gap-4 shrink-0">
          {/* Connection status indicator */}
          <div className="hidden lg:flex items-center gap-2 px-2.5 py-1 rounded-full bg-slate-100 border border-slate-200 text-xs text-slate-600">
            <span className={`w-2 h-2 rounded-full ${isBackendOnline ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`}></span>
            <span className="text-[11px] font-medium">{isBackendOnline ? 'API Connected' : 'Local Mode'}</span>
          </div>

          {/* User Profile Pill or Auth Button */}
          {currentUser ? (
            <div className="flex items-center gap-3 pl-2 border-l border-slate-200">
              <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white text-xs font-bold shadow-sm">
                {(currentUser.full_name || currentUser.email || 'U').charAt(0).toUpperCase()}
              </div>
              <div className="hidden sm:block text-left">
                <p className="text-xs font-bold text-slate-900 leading-tight">{currentUser.full_name || 'Google User'}</p>
                <p className="text-[10px] text-slate-400 font-medium leading-tight">{currentUser.email}</p>
              </div>
              <button
                onClick={onLogout}
                className="text-[11px] text-slate-500 hover:text-slate-800 font-semibold px-2.5 py-1 rounded-lg hover:bg-slate-100 transition-all cursor-pointer"
              >
                Logout
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenAuthModal}
              className="px-3 py-1.5 rounded-xl bg-white hover:bg-slate-50 text-slate-700 font-semibold text-xs border border-slate-300 shadow-xs flex items-center gap-2 transition-all cursor-pointer"
            >
              <svg className="w-3.5 h-3.5" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
              </svg>
              <span>Log in with Google</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
