import React from 'react';
import { FolderOpen } from 'lucide-react';

export default function EmptyState({
  title = "No Data Found",
  description = "Get started by uploading your first document or running an evidence analysis.",
  icon: Icon = FolderOpen,
  actionLabel,
  onAction
}) {
  return (
    <div className="glass-panel rounded-2xl p-10 text-center flex flex-col items-center justify-center space-y-4 border border-dashed border-navy-700/80 my-4">
      <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-navy-800 to-navy-700 flex items-center justify-center text-cyan-400 border border-navy-600 shadow-inner">
        <Icon className="w-7 h-7 text-cyan-400" />
      </div>
      <div className="max-w-md">
        <h3 className="text-base font-bold text-white mb-1 font-sans">{title}</h3>
        <p className="text-xs text-slate-400 leading-relaxed">{description}</p>
      </div>
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="mt-2 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold text-xs transition-all shadow-md shadow-cyan-500/20 active:scale-95"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}
