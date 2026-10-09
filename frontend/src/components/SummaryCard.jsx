import React from 'react';

export default function SummaryCard({ title, value, icon: Icon, subtitle, trend, accentColor = 'cyan' }) {
  const accentStyles = {
    cyan: 'from-cyan-500/20 to-blue-500/10 border-cyan-500/30 text-cyan-400',
    emerald: 'from-emerald-500/20 to-teal-500/10 border-emerald-500/30 text-emerald-400',
    amber: 'from-amber-500/20 to-orange-500/10 border-amber-500/30 text-amber-400',
    purple: 'from-purple-500/20 to-indigo-500/10 border-purple-500/30 text-purple-400',
  }[accentColor] || 'from-cyan-500/20 to-blue-500/10 border-cyan-500/30 text-cyan-400';

  return (
    <div className="glass-card rounded-2xl p-5 relative overflow-hidden group hover:-translate-y-0.5 transition-all">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
            {title}
          </p>
          <h3 className="text-2xl font-bold text-white tracking-tight font-sans">
            {value}
          </h3>
        </div>
        <div className={`p-3 rounded-xl bg-gradient-to-br border ${accentStyles}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      {(subtitle || trend) && (
        <div className="mt-4 flex items-center gap-2 text-xs">
          {trend && (
            <span className="font-semibold text-cyan-400 bg-cyan-950/80 px-2 py-0.5 rounded border border-cyan-800">
              {trend}
            </span>
          )}
          <span className="text-slate-400 truncate">{subtitle}</span>
        </div>
      )}
    </div>
  );
}
