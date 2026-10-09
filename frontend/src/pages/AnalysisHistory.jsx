import React, { useState } from 'react';
import { History, Search, Edit3, X, Check, FolderOpen, ArrowRight, ShieldCheck } from 'lucide-react';
import StatusBadge from '../components/StatusBadge';

export default function AnalysisHistory({ analyses = [], onNavigate, onUpdateAnalysis }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All Status');
  const [editingItem, setEditingItem] = useState(null);
  const [editAnswer, setEditAnswer] = useState('');
  const [editSummary, setEditSummary] = useState('');
  const [editStatus, setEditStatus] = useState('SUPPORTED');

  const filteredRows = analyses.filter(row => {
    const matchesSearch = row.question.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'All Status' || (row.decision_status || '').toUpperCase().includes(statusFilter.toUpperCase().replace(' ', '_'));
    return matchesSearch && matchesStatus;
  });

  const startEdit = (item) => {
    setEditingItem(item);
    setEditAnswer(item.grounded_answer || '');
    setEditSummary(item.summary || '');
    setEditStatus(item.decision_status || 'SUPPORTED');
  };

  const handleSaveEdit = async (e) => {
    e.preventDefault();
    if (!editingItem || !onUpdateAnalysis) return;
    try {
      await onUpdateAnalysis(editingItem.id, {
        grounded_answer: editAnswer,
        summary: editSummary,
        decision_status: editStatus
      });
      setEditingItem(null);
    } catch (err) {
      console.error('Failed to save history edit:', err);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-slate-900 tracking-tight font-sans flex items-center gap-2">
            <History className="w-5 h-5 text-blue-600" />
            Analysis History & Evidence Archive
          </h1>
          <p className="text-xs text-slate-500 font-medium">
            View, audit, and edit past generated decision answers.
          </p>
        </div>

        {/* Search & Filter */}
        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search analyses..."
              className="pl-9 pr-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 font-sans"
            />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 font-medium"
          >
            <option>All Status</option>
            <option>SUPPORTED</option>
            <option>NEEDS VERIFICATION</option>
            <option>INSUFFICIENT EVIDENCE</option>
          </select>
        </div>
      </div>

      {/* History Data Table */}
      {analyses.length === 0 ? (
        <div className="saas-card rounded-2xl p-12 text-center space-y-3">
          <FolderOpen className="w-10 h-10 text-slate-400 mx-auto" />
          <div className="max-w-md mx-auto">
            <h3 className="text-sm font-bold text-slate-900">No analysis history yet</h3>
            <p className="text-xs text-slate-500 leading-relaxed mt-1">
              Questions asked in the Document Analysis engine will appear here with decision status and evidence verification summaries.
            </p>
          </div>
          <button
            onClick={() => onNavigate('analysis')}
            className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs transition-all shadow-sm cursor-pointer"
          >
            Run First Analysis
          </button>
        </div>
      ) : (
        <div className="saas-card rounded-2xl p-5 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-600">
              <thead className="bg-slate-50 text-slate-400 font-semibold uppercase text-[10px] border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4">Question</th>
                  <th className="py-3 px-4">Source Documents</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Confidence</th>
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredRows.map((row) => (
                  <tr key={row.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-4 font-semibold text-slate-900 max-w-xs">
                      <div className="flex items-center gap-1.5 truncate">
                        <span className="truncate" title={row.question}>{row.question}</span>
                        {row.is_edited && (
                          <span className="text-[9px] px-1.5 py-0.2 bg-purple-100 text-purple-700 rounded font-bold shrink-0">
                            Edited
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3.5 px-4 font-medium text-slate-600 truncate max-w-[200px]">
                      {row.supporting_evidence && row.supporting_evidence.length > 0
                        ? row.supporting_evidence[0].source_filename
                        : 'Context Analysis'}
                    </td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={row.decision_status} />
                    </td>
                    <td className="py-3.5 px-4 font-mono font-bold text-slate-700">
                      {row.decision_status === 'INSUFFICIENT_EVIDENCE'
                        ? '0%'
                        : `${Math.round((row.reliability_score || 0) * 100)}% Match`}
                    </td>
                    <td className="py-3.5 px-4 text-slate-500 text-[11px] whitespace-nowrap">
                      {row.timestamp}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      {/* Edit Option for Generated Analysis (Constraint Card 04) */}
                      <button 
                        onClick={() => startEdit(row)}
                        className="px-2.5 py-1 text-slate-600 hover:text-blue-600 border border-slate-200 hover:border-blue-200 hover:bg-blue-50/50 rounded-lg text-xs font-semibold inline-flex items-center gap-1 transition-colors cursor-pointer"
                        title="Edit generated answer or notes"
                      >
                        <Edit3 className="w-3 h-3 text-blue-600" />
                        <span>Edit</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Edit Analysis Modal (Constraint Card 04) */}
      {editingItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs animate-in fade-in">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 space-y-4 text-left">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Edit3 className="w-4 h-4 text-blue-600" />
                <span>Edit Generated Answer</span>
              </h3>
              <button
                onClick={() => setEditingItem(null)}
                className="p-1 text-slate-400 hover:text-slate-600 rounded-lg cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSaveEdit} className="space-y-3">
              <div>
                <label className="block text-[11px] font-bold text-slate-700 mb-1">
                  Question Prompt
                </label>
                <p className="text-xs text-slate-600 bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                  {editingItem.question}
                </p>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-700 mb-1">
                  Decision Status
                </label>
                <select
                  value={editStatus}
                  onChange={(e) => setEditStatus(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:border-blue-500 text-slate-900 font-semibold"
                >
                  <option value="SUPPORTED">SUPPORTED</option>
                  <option value="NEEDS_VERIFICATION">NEEDS_VERIFICATION</option>
                  <option value="INSUFFICIENT_EVIDENCE">INSUFFICIENT_EVIDENCE</option>
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-700 mb-1">
                  Executive Summary
                </label>
                <input
                  type="text"
                  required
                  value={editSummary}
                  onChange={(e) => setEditSummary(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:border-blue-500 text-slate-900"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-700 mb-1">
                  Grounded Answer
                </label>
                <textarea
                  rows={5}
                  required
                  value={editAnswer}
                  onChange={(e) => setEditAnswer(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:border-blue-500 text-slate-900 leading-relaxed font-sans"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setEditingItem(null)}
                  className="px-3.5 py-1.5 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-100 text-xs font-semibold cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold shadow-xs cursor-pointer flex items-center gap-1.5"
                >
                  <Check className="w-3.5 h-3.5" />
                  <span>Save Changes</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
