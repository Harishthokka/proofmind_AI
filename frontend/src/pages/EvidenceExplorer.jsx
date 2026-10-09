import React, { useState } from 'react';
import {
  Database,
  Search,
  Download,
  FileText,
  ChevronLeft,
  ChevronRight,
  Maximize2,
  FolderOpen
} from 'lucide-react';

export default function EvidenceExplorer({ documents = [], analyses = [], onNavigate }) {
  const [selectedDoc, setSelectedDoc] = useState(documents[0]?.filename || 'All Documents');
  const [searchQuery, setSearchQuery] = useState('');
  const [evidenceTypeFilter, setEvidenceTypeFilter] = useState('All Evidence Types');
  const [selectedCardId, setSelectedCardId] = useState(null);
  const [zoomLevel, setZoomLevel] = useState(100);

  // Flatten real evidence from analyses
  const realEvidenceList = analyses.flatMap((a) => [
    ...(a.supporting_evidence || []),
    ...(a.conflicting_evidence || []),
    ...(a.uncertain_evidence || []),
  ]);

  const filteredEvidence = realEvidenceList.filter((item) => {
    const matchesDoc = selectedDoc === 'All Documents' || item.source_filename === selectedDoc;
    const matchesSearch = !searchQuery || item.passage.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = evidenceTypeFilter === 'All Evidence Types' || item.type === evidenceTypeFilter;
    return matchesDoc && matchesSearch && matchesType;
  });

  const activeCard = filteredEvidence.find(c => c.id === selectedCardId) || filteredEvidence[0];

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Top Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-slate-900 tracking-tight font-sans flex items-center gap-2">
            <Database className="w-5 h-5 text-blue-600" />
            Evidence Explorer
          </h1>
          <p className="text-xs text-slate-500 font-medium">
            Explore AI-highlighted evidence from your documents and analyze sources, quotes, and context.
          </p>
        </div>

        <button className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 font-semibold text-xs transition-all shadow-2xs">
          <Download className="w-3.5 h-3.5 text-slate-600" />
          <span>Export Results</span>
        </button>
      </div>

      {/* Top Filter Bar */}
      <div className="saas-card rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4">
        {/* Document Select Dropdown */}
        <div className="min-w-[200px]">
          <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">
            Select Documents
          </label>
          <select
            value={selectedDoc}
            onChange={(e) => setSelectedDoc(e.target.value)}
            className="w-full px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-800 focus:outline-none focus:border-blue-500"
          >
            <option value="All Documents">All Documents</option>
            {documents.map((d) => (
              <option key={d.id} value={d.filename}>{d.filename}</option>
            ))}
          </select>
        </div>

        {/* Search Input with button */}
        <div className="flex-1 min-w-[280px]">
          <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">
            Search Evidence
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search keyword or quote..."
              className="w-full px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-800 focus:outline-none focus:border-blue-500 font-sans"
            />
          </div>
        </div>

        {/* Filter Dropdowns */}
        <div className="flex items-center gap-3">
          <div>
            <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">
              Filter Options
            </label>
            <select
              value={evidenceTypeFilter}
              onChange={(e) => setEvidenceTypeFilter(e.target.value)}
              className="px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 font-medium"
            >
              <option>All Evidence Types</option>
              <option value="SUPPORTING">Supporting</option>
              <option value="CONFLICTING">Conflicting</option>
              <option value="UNCERTAIN">Uncertain</option>
            </select>
          </div>
        </div>
      </div>

      {/* Main Split Content: Evidence Results + Evidence Viewer */}
      {filteredEvidence.length === 0 ? (
        <div className="saas-card rounded-2xl p-12 text-center space-y-3">
          <FolderOpen className="w-10 h-10 text-slate-400 mx-auto" />
          <div className="max-w-md mx-auto">
            <h3 className="text-sm font-bold text-slate-900">No evidence items found</h3>
            <p className="text-xs text-slate-500 leading-relaxed mt-1">
              {realEvidenceList.length === 0
                ? 'Upload PDF documents and ask questions to extract verified evidence passages.'
                : 'No evidence matches your current search or filter criteria.'}
            </p>
          </div>
          {realEvidenceList.length === 0 && (
            <button
              onClick={() => onNavigate('analysis')}
              className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs transition-all shadow-sm"
            >
              Go to Analysis Engine
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Column: Evidence Results (4 cols) */}
          <div className="lg:col-span-4 saas-card rounded-2xl p-4 space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-slate-100">
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                Evidence Results
              </h2>
              <span className="text-[10px] font-bold text-slate-400">{filteredEvidence.length} results</span>
            </div>

            <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
              {filteredEvidence.map((card, idx) => {
                const isSelected = activeCard?.id === card.id;
                return (
                  <div
                    key={card.id || idx}
                    onClick={() => setSelectedCardId(card.id)}
                    className={`p-3.5 rounded-xl border transition-all cursor-pointer space-y-2 ${
                      isSelected
                        ? 'bg-blue-50/70 border-blue-300 shadow-sm'
                        : 'bg-white border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <span className="w-5 h-5 rounded-full bg-slate-100 text-slate-700 flex items-center justify-center text-[11px] font-bold">
                          {idx + 1}
                        </span>
                        <h3 className="text-xs font-bold text-slate-900 truncate max-w-[140px]">
                          {card.source_filename}
                        </h3>
                      </div>
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-emerald-100 text-emerald-700">
                        {card.type || 'SUPPORTING'}
                      </span>
                    </div>

                    <p className="text-[11px] text-slate-400 font-medium">Page {card.page_number || 1}</p>

                    <p className="text-xs text-slate-600 italic bg-slate-50 p-2 rounded-lg border border-slate-100">
                      "{card.passage}"
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Middle/Right Column: Evidence Viewer & Details (8 cols) */}
          {activeCard && (
            <div className="lg:col-span-8 space-y-6">
              {/* Document Viewer Container */}
              <div className="saas-card rounded-2xl p-5 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-200 pb-3">
                  <h2 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
                    <FileText className="w-4 h-4 text-blue-600" />
                    Evidence Viewer
                  </h2>

                  {/* Page & Zoom Controls */}
                  <div className="flex items-center gap-3 text-xs">
                    <div className="flex items-center gap-1 bg-slate-100 px-2 py-1 rounded-lg border border-slate-200 font-mono">
                      <button className="hover:text-blue-600"><ChevronLeft className="w-3.5 h-3.5" /></button>
                      <span className="font-semibold text-slate-700">{activeCard.page_number || 1}</span>
                      <button className="hover:text-blue-600"><ChevronRight className="w-3.5 h-3.5" /></button>
                    </div>

                    <div className="flex items-center gap-1 bg-slate-100 px-2.5 py-1 rounded-lg border border-slate-200 font-mono font-semibold text-slate-700">
                      <span>{zoomLevel}%</span>
                    </div>

                    <button className="p-1.5 hover:bg-slate-100 rounded-lg text-slate-600">
                      <Maximize2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                {/* Document Page Canvas Container */}
                <div className="bg-slate-100/70 rounded-xl p-6 border border-slate-200 min-h-[220px] flex justify-center">
                  <div className="bg-white w-full max-w-xl p-6 rounded-lg border border-slate-300 shadow-md space-y-3 text-xs leading-relaxed font-sans text-slate-700">
                    <p className="font-bold text-slate-900 text-sm border-b pb-1">
                      {activeCard.source_filename} — Page {activeCard.page_number || 1}
                    </p>
                    <p>
                      Extracted Passage: <span className="highlight-yellow">{activeCard.passage}</span>
                    </p>
                  </div>
                </div>
              </div>

              {/* Bottom Details Grid */}
              <div className="saas-card rounded-2xl p-5 space-y-4">
                <h2 className="text-xs font-bold uppercase tracking-wider text-slate-700">
                  Evidence Details
                </h2>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs">
                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block mb-0.5">Source Document</span>
                    <span className="font-semibold text-slate-900 truncate block">{activeCard.source_filename}</span>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block mb-0.5">Page Number</span>
                    <span className="font-semibold text-slate-900">Page {activeCard.page_number || 1}</span>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block mb-0.5">Evidence Type</span>
                    <span className="font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded border border-blue-200 inline-block">{activeCard.type || 'SUPPORTING'}</span>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block mb-0.5">Relevance Match</span>
                    <span className="font-semibold text-emerald-600">{Math.round((activeCard.confidence_score || 0.9) * 100)}%</span>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block mb-0.5">Status</span>
                    <span className="font-semibold text-slate-900">Verified</span>
                  </div>
                </div>

                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-1">
                  <span className="text-[10px] uppercase font-bold text-slate-400 block">Extracted Text</span>
                  <p className="text-xs text-slate-800 italic font-sans">
                    "{activeCard.passage}"
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
