import React from 'react';
import { CheckCircle2, AlertTriangle, HelpCircle } from 'lucide-react';

export default function StatusBadge({ status }) {
  const norm = (status || '').toUpperCase().replace(/_/g, ' ');

  if (norm.includes('SUPPORTED')) {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-bold bg-emerald-100 text-emerald-700 border border-emerald-200">
        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
        SUPPORTED
      </span>
    );
  }

  if (norm.includes('NEEDS VERIFICATION')) {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-bold bg-amber-100 text-amber-800 border border-amber-200">
        <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
        Needs Verification
      </span>
    );
  }

  if (norm.includes('INSUFFICIENT EVIDENCE')) {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-bold bg-rose-100 text-rose-700 border border-rose-200">
        <HelpCircle className="w-3.5 h-3.5 text-rose-600" />
        Insufficient Evidence
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-bold bg-slate-100 text-slate-700 border border-slate-200">
      {status || 'PROCESSED'}
    </span>
  );
}
