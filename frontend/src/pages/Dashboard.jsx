import React from 'react';
import {
  FileText,
  TrendingUp,
  AlertTriangle,
  Upload,
  PlusCircle,
  ArrowRight,
  FileCheck,
  Search,
  BookOpen,
  Sparkles,
  FolderOpen
} from 'lucide-react';

export default function Dashboard({
  currentUser,
  documents = [],
  analyses = [],
  onNavigate,
  onUploadClick,
  onNewAnalysisClick
}) {
  const verifiedCount = analyses.filter(a => (a.decision_status || '').includes('SUPPORTED')).length;
  const conflictsCount = analyses.filter(a => (a.decision_status || '').includes('VERIFICATION')).length;

  const firstName = currentUser?.full_name?.split(' ')[0] || 
    (currentUser?.email ? currentUser.email.split('@')[0].replace('.', ' ') : 'Researcher');
  const capitalizedName = firstName.charAt(0).toUpperCase() + firstName.slice(1);

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Hero Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-blue-50/80 via-indigo-50/40 to-cyan-50/60 p-8 border border-blue-100 shadow-sm">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="max-w-2xl space-y-3 text-left">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white text-blue-600 border border-blue-200 text-xs font-semibold shadow-xs">
              <FileText className="w-3.5 h-3.5" />
              <span>Evidence-Aware Engine</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight font-sans">
              Welcome back, {capitalizedName} 👋
            </h1>
            <h2 className="text-base font-bold text-slate-800">
              Turn your documents into evidence-backed answers.
            </h2>
            <p className="text-xs text-slate-600 leading-relaxed">
              Analyze multiple PDF documents, verify freshness, detect conflicting claims, and get decision-grade answers backed by direct source citations.
            </p>

            <div className="pt-2 flex flex-wrap items-center gap-3">
              <button
                onClick={onNewAnalysisClick}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs transition-all shadow-md shadow-blue-500/20 active:scale-95"
              >
                <PlusCircle className="w-4 h-4" />
                <span>Start New Analysis +</span>
              </button>

              <button
                onClick={onUploadClick}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 font-semibold text-xs transition-all shadow-xs active:scale-95"
              >
                <Upload className="w-4 h-4 text-slate-600" />
                <span>Upload PDF Document</span>
              </button>
            </div>
          </div>

          {/* Banner Graphic Illustration */}
          <div className="relative hidden md:flex items-center justify-center w-48 h-48 shrink-0">
            <div className="w-36 h-44 bg-white rounded-2xl border border-blue-100 shadow-xl p-3 flex flex-col justify-between transform rotate-3">
              <div className="space-y-2">
                <div className="w-full h-3 bg-blue-100 rounded"></div>
                <div className="w-3/4 h-2 bg-slate-100 rounded"></div>
                <div className="w-5/6 h-2 bg-slate-100 rounded"></div>
              </div>
              <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white mx-auto shadow-md">
                <Search className="w-5 h-5 text-white" />
              </div>
            </div>
            <div className="absolute top-2 left-2 w-28 h-36 bg-blue-600/10 backdrop-blur-xs rounded-xl border border-blue-200 transform -rotate-6"></div>
          </div>
        </div>
      </div>

      {/* 4 Real Metric Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1 */}
        <div className="saas-card rounded-2xl p-5 flex items-start justify-between">
          <div className="space-y-1">
            <p className="text-xs font-semibold text-slate-500">Indexed Documents</p>
            <h3 className="text-2xl font-bold text-slate-900">{documents.length}</h3>
            <span className="inline-block text-[11px] font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
              {documents.length > 0 ? `${documents.length} File(s)` : 'No files'}
            </span>
          </div>
          <div className="p-3 rounded-xl bg-blue-50 text-blue-600 border border-blue-100">
            <FileText className="w-5 h-5" />
          </div>
        </div>

        {/* Card 2 */}
        <div className="saas-card rounded-2xl p-5 flex items-start justify-between">
          <div className="space-y-1">
            <p className="text-xs font-semibold text-slate-500">Analyses Run</p>
            <h3 className="text-2xl font-bold text-slate-900">{analyses.length}</h3>
            <span className="inline-block text-[11px] font-semibold text-purple-600 bg-purple-50 px-2 py-0.5 rounded">
              {analyses.length > 0 ? 'Active' : 'Standby'}
            </span>
          </div>
          <div className="p-3 rounded-xl bg-purple-50 text-purple-600 border border-purple-100">
            <TrendingUp className="w-5 h-5" />
          </div>
        </div>

        {/* Card 3 */}
        <div className="saas-card rounded-2xl p-5 flex items-start justify-between">
          <div className="space-y-1">
            <p className="text-xs font-semibold text-slate-500">Verified Answers</p>
            <h3 className="text-2xl font-bold text-slate-900">{verifiedCount}</h3>
            <span className="inline-block text-[11px] font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded">
              {verifiedCount > 0 ? 'Verified Grounded' : '0 Verified'}
            </span>
          </div>
          <div className="p-3 rounded-xl bg-emerald-50 text-emerald-600 border border-emerald-100">
            <FileCheck className="w-5 h-5" />
          </div>
        </div>

        {/* Card 4 */}
        <div className="saas-card rounded-2xl p-5 flex items-start justify-between">
          <div className="space-y-1">
            <p className="text-xs font-semibold text-slate-500">Conflicts Detected</p>
            <h3 className="text-2xl font-bold text-slate-900">{conflictsCount}</h3>
            <span className="inline-block text-[11px] font-semibold text-rose-600 bg-rose-50 px-2 py-0.5 rounded">
              {conflictsCount > 0 ? 'Needs Review' : '0 Conflicts'}
            </span>
          </div>
          <div className="p-3 rounded-xl bg-rose-50 text-rose-600 border border-rose-100">
            <AlertTriangle className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Split Main Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Recent Documents Table */}
        <div className="lg:col-span-2 saas-card rounded-2xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-bold text-slate-900 font-sans flex items-center gap-2">
              <FileText className="w-4 h-4 text-blue-600" />
              Recent Documents
            </h2>
            <button
              onClick={() => onNavigate('analysis')}
              className="text-xs text-blue-600 hover:text-blue-700 font-semibold flex items-center gap-1"
            >
              <span>View All</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {documents.length === 0 ? (
            <div className="text-center py-10 space-y-3 bg-slate-50/50 rounded-xl border border-dashed border-slate-200">
              <FolderOpen className="w-8 h-8 text-slate-400 mx-auto" />
              <div>
                <p className="text-xs font-bold text-slate-800">No documents uploaded yet</p>
                <p className="text-[11px] text-slate-400">Upload PDF files to start indexing evidence for Q&A reasoning.</p>
              </div>
              <button
                onClick={onUploadClick}
                className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs transition-all shadow-sm"
              >
                Upload PDF Document
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-600">
                <thead className="bg-slate-50 text-slate-400 font-semibold uppercase text-[10px] border-b border-slate-200">
                  <tr>
                    <th className="py-2.5 px-3">Name</th>
                    <th className="py-2.5 px-3">Pages</th>
                    <th className="py-2.5 px-3">Size</th>
                    <th className="py-2.5 px-3">Uploaded On</th>
                    <th className="py-2.5 px-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {documents.map((doc) => (
                    <tr key={doc.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3 px-3 font-semibold text-slate-900 flex items-center gap-2 max-w-[220px] truncate">
                        <FileText className="w-4 h-4 text-rose-500 shrink-0" />
                        <span className="truncate" title={doc.filename}>{doc.filename}</span>
                      </td>
                      <td className="py-3 px-3 font-medium">{doc.page_count || 1}</td>
                      <td className="py-3 px-3 font-mono text-[11px]">
                        {doc.file_size ? `${(doc.file_size / (1024 * 1024)).toFixed(1)} MB` : '1.2 MB'}
                      </td>
                      <td className="py-3 px-3 text-slate-500 text-[11px]">
                        {doc.uploaded_at?.slice(0, 10) || new Date().toISOString().slice(0, 10)}
                      </td>
                      <td className="py-3 px-3">
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-700">
                          ● {doc.status || 'Processed'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Right Column: Quick Actions */}
        <div className="lg:col-span-1 saas-card rounded-2xl p-5 space-y-4">
          <h2 className="text-sm font-bold text-slate-900 font-sans">
            Quick Actions
          </h2>

          <div className="space-y-3">
            <div
              onClick={onUploadClick}
              className="p-3.5 rounded-xl bg-slate-50 hover:bg-blue-50/50 border border-slate-200 hover:border-blue-200 cursor-pointer transition-all flex items-center gap-3 group"
            >
              <div className="p-2.5 rounded-xl bg-blue-100 text-blue-600 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                <Upload className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs font-bold text-slate-900 group-hover:text-blue-600 transition-colors">Upload Document</p>
                <p className="text-[11px] text-slate-400">Add PDFs to your library</p>
              </div>
            </div>

            <div
              onClick={onNewAnalysisClick}
              className="p-3.5 rounded-xl bg-slate-50 hover:bg-purple-50/50 border border-slate-200 hover:border-purple-200 cursor-pointer transition-all flex items-center gap-3 group"
            >
              <div className="p-2.5 rounded-xl bg-purple-100 text-purple-600 group-hover:bg-purple-600 group-hover:text-white transition-colors">
                <Sparkles className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs font-bold text-slate-900 group-hover:text-purple-600 transition-colors">Ask a Question</p>
                <p className="text-[11px] text-slate-400">Get evidence-backed answers</p>
              </div>
            </div>

            <div
              onClick={() => onNavigate('evidence')}
              className="p-3.5 rounded-xl bg-slate-50 hover:bg-emerald-50/50 border border-slate-200 hover:border-emerald-200 cursor-pointer transition-all flex items-center gap-3 group"
            >
              <div className="p-2.5 rounded-xl bg-emerald-100 text-emerald-600 group-hover:bg-emerald-600 group-hover:text-white transition-colors">
                <BookOpen className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs font-bold text-slate-900 group-hover:text-emerald-600 transition-colors">Explore Evidence</p>
                <p className="text-[11px] text-slate-400">View and search key information</p>
              </div>
            </div>

            <div
              onClick={() => onNavigate('evidence')}
              className="p-3.5 rounded-xl bg-slate-50 hover:bg-rose-50/50 border border-slate-200 hover:border-rose-200 cursor-pointer transition-all flex items-center gap-3 group"
            >
              <div className="p-2.5 rounded-xl bg-rose-100 text-rose-600 group-hover:bg-rose-600 group-hover:text-white transition-colors">
                <AlertTriangle className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs font-bold text-slate-900 group-hover:text-rose-600 transition-colors">Check Conflicts</p>
                <p className="text-[11px] text-slate-400">Find contradictory information</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
