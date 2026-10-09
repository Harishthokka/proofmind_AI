import React from 'react';
import { FileText, Calendar, Layers, ShieldCheck, AlertCircle, HelpCircle, CheckCircle2 } from 'lucide-react';

export default function EvidenceCard({ item }) {
  const {
    source_filename,
    page_number,
    source_date,
    version_info,
    passage,
    type,
    confidence_score,
    citation_verified,
    verification_note
  } = item;

  const typeStyles = {
    SUPPORTING: {
      badge: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
      icon: ShieldCheck,
      border: 'border-l-4 border-l-emerald-500',
      label: 'SUPPORTING EVIDENCE'
    },
    CONFLICTING: {
      badge: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
      icon: AlertCircle,
      border: 'border-l-4 border-l-amber-500',
      label: 'CONFLICTING EVIDENCE'
    },
    UNCERTAIN: {
      badge: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30',
      icon: HelpCircle,
      border: 'border-l-4 border-l-indigo-500',
      label: 'UNCERTAIN EVIDENCE'
    }
  };

  const style = typeStyles[type] || typeStyles.SUPPORTING;
  const TypeIcon = style.icon;

  return (
    <div className={`glass-card rounded-2xl p-5 ${style.border} space-y-3 relative group`}>
      {/* Top Header Row */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-2 text-slate-200 font-semibold text-xs truncate max-w-[70%]">
          <FileText className="w-4 h-4 text-cyan-400 shrink-0" />
          <span className="truncate" title={source_filename}>{source_filename}</span>
        </div>

        <div className="flex items-center gap-2">
          {confidence_score && (
            <span className="text-[10px] font-mono font-semibold text-slate-300 bg-navy-850 px-2 py-0.5 rounded border border-navy-700">
              Relevance: {Math.round(confidence_score * 100)}%
            </span>
          )}
          <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wider uppercase border ${style.badge}`}>
            <TypeIcon className="w-3 h-3" />
            {style.label}
          </span>
        </div>
      </div>

      {/* Extracted Passage */}
      <blockquote className="text-xs text-slate-300 bg-navy-950/80 rounded-xl p-3.5 border border-navy-800/80 italic leading-relaxed font-sans">
        "{passage}"
      </blockquote>

      {/* Metadata & Verification Row */}
      <div className="flex items-center justify-between flex-wrap gap-3 text-[11px] text-slate-400 pt-1 border-t border-navy-800/60">
        <div className="flex items-center gap-4">
          {page_number && (
            <div className="flex items-center gap-1">
              <Layers className="w-3.5 h-3.5 text-cyan-400" />
              <span>Page {page_number}</span>
            </div>
          )}
          {source_date && (
            <div className="flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5 text-slate-400" />
              <span>Date: {source_date}</span>
            </div>
          )}
          {version_info && (
            <span className="text-slate-400 font-mono">Ver: {version_info}</span>
          )}
        </div>

        {/* F05 Citation Verification Badge */}
        {citation_verified !== undefined && (
          <div className="flex items-center gap-1 text-[10px] font-semibold text-emerald-400">
            <CheckCircle2 className="w-3 h-3" />
            <span>{verification_note || 'Citation Verified'}</span>
          </div>
        )}
      </div>
    </div>
  );
}
