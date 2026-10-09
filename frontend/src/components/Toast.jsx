import React, { useEffect } from 'react';
import { 
  CheckCircle2, 
  AlertCircle, 
  AlertTriangle, 
  Info, 
  X, 
  Sparkles 
} from 'lucide-react';

export default function Toast({ toasts = [], onDismiss }) {
  if (!toasts || toasts.length === 0) return null;

  return (
    <div 
      className="fixed bottom-5 right-5 z-50 flex flex-col gap-2.5 max-w-sm w-full pointer-events-none"
      role="region"
      aria-label="Action Notifications"
    >
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onDismiss={onDismiss} />
      ))}
    </div>
  );
}

function ToastItem({ toast, onDismiss }) {
  const { id, title, message, type = 'success', action, duration = 4500 } = toast;

  useEffect(() => {
    const timer = setTimeout(() => {
      onDismiss(id);
    }, duration);
    return () => clearTimeout(timer);
  }, [id, duration, onDismiss]);

  const config = {
    success: {
      border: 'border-emerald-200 bg-emerald-50/95',
      iconBg: 'bg-emerald-500 text-white shadow-emerald-500/20',
      icon: CheckCircle2,
      titleColor: 'text-emerald-950',
      textColor: 'text-emerald-800',
      progress: 'bg-emerald-500'
    },
    error: {
      border: 'border-rose-200 bg-rose-50/95',
      iconBg: 'bg-rose-500 text-white shadow-rose-500/20',
      icon: AlertCircle,
      titleColor: 'text-rose-950',
      textColor: 'text-rose-800',
      progress: 'bg-rose-500'
    },
    warning: {
      border: 'border-amber-200 bg-amber-50/95',
      iconBg: 'bg-amber-500 text-white shadow-amber-500/20',
      icon: AlertTriangle,
      titleColor: 'text-amber-950',
      textColor: 'text-amber-800',
      progress: 'bg-amber-500'
    },
    info: {
      border: 'border-blue-200 bg-blue-50/95',
      iconBg: 'bg-blue-600 text-white shadow-blue-500/20',
      icon: Sparkles,
      titleColor: 'text-blue-950',
      textColor: 'text-blue-800',
      progress: 'bg-blue-600'
    }
  }[type] || {
    border: 'border-slate-200 bg-white',
    iconBg: 'bg-slate-700 text-white',
    icon: Info,
    titleColor: 'text-slate-900',
    textColor: 'text-slate-600',
    progress: 'bg-slate-600'
  };

  const Icon = config.icon;

  return (
    <div 
      className={`pointer-events-auto rounded-2xl p-4 shadow-xl border backdrop-blur-md transition-all duration-200 animate-in slide-in-from-bottom-3 relative overflow-hidden ${config.border}`}
    >
      <div className="flex items-start gap-3">
        <div className={`w-7 h-7 rounded-xl flex items-center justify-center shrink-0 shadow-md ${config.iconBg}`}>
          <Icon className="w-4 h-4" />
        </div>

        <div className="flex-1 min-w-0 pr-4">
          <h4 className={`text-xs font-bold leading-tight font-sans ${config.titleColor}`}>
            {title}
          </h4>
          {message && (
            <p className={`text-[11px] leading-relaxed mt-0.5 font-sans ${config.textColor}`}>
              {message}
            </p>
          )}

          {action && (
            <div className="mt-2">
              <button
                type="button"
                onClick={() => {
                  action.onClick();
                  onDismiss(id);
                }}
                className="text-[10px] font-bold uppercase tracking-wider text-blue-700 hover:text-blue-900 underline cursor-pointer"
              >
                {action.label}
              </button>
            </div>
          )}
        </div>

        <button
          onClick={() => onDismiss(id)}
          className="text-slate-400 hover:text-slate-600 p-1 rounded-lg transition-colors absolute top-2.5 right-2.5 cursor-pointer"
          aria-label="Dismiss feedback"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Auto-dismiss progress bar */}
      <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-black/5 overflow-hidden">
        <div 
          className={`h-full ${config.progress} transition-all ease-linear`}
          style={{
            animation: `shrinkWidth ${duration}ms linear forwards`
          }}
        />
      </div>
    </div>
  );
}
