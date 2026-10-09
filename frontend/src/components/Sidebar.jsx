import React from 'react';
import { LayoutDashboard, FileSearch, Database, History, Settings, ChevronRight, ShieldCheck } from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'analysis', label: 'Document Analysis', icon: FileSearch },
    { id: 'evidence', label: 'Evidence Explorer', icon: Database },
    { id: 'history', label: 'Analysis History', icon: History },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 p-4 flex flex-col justify-between shrink-0 min-h-[calc(100vh-61px)]">
      <div className="space-y-6">
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-blue-50 text-blue-600 border border-blue-100 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-blue-600' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </div>
              </button>
            );
          })}
        </nav>

        {/* EvidenceEngine info card */}
        <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 text-xs">
          <div className="flex items-center gap-2 mb-1 text-blue-600 font-bold">
            <ShieldCheck className="w-4 h-4" />
            <span>EvidenceEngine v1</span>
          </div>
          <p className="text-slate-500 text-[11px] leading-relaxed">
            Checks evidence freshness, contradiction detection & citation validity.
          </p>
        </div>
      </div>

      {/* Footer Team Info */}
      <div className="pt-4 border-t border-slate-100 flex items-center gap-2.5 px-1">
        <div className="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-xs shrink-0">
          N
        </div>
        <div className="min-w-0 text-left">
          <p className="text-xs font-bold text-slate-900 truncate">Team NeverExist</p>
          <p className="text-[10px] text-slate-400 truncate">Vishnu Institute of Technology</p>
        </div>
      </div>
    </aside>
  );
}
