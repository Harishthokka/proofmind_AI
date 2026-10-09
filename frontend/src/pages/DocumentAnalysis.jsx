import React, { useState, useRef } from 'react';
import {
  Upload,
  FileText,
  Trash2,
  Send,
  Loader2,
  Sparkles,
  Paperclip,
  RotateCcw,
  PlusCircle,
  FolderOpen,
  AlertTriangle,
  Edit3,
  Check,
  X,
  Calendar,
  Layers,
  MessageSquare,
  Bookmark
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';

export default function DocumentAnalysis({
  documents = [],
  onUploadFiles,
  onDeleteDocument,
  onRunAnalysis,
  onUploadAndReanalyze,
  onUpdateAnalysis,
  onUpdateDocument,
  latestResult,
  isAnalyzing,
  onViewEvidence,
  showToast
}) {
  const [question, setQuestion] = useState('');
  const [docSearch, setDocSearch] = useState('');
  const [selectedDocIds, setSelectedDocIds] = useState([]);
  const fileInputRef = useRef(null);

  // Edit state for Generated Information (AI Answer & Decision)
  const [isEditingAnswer, setIsEditingAnswer] = useState(false);
  const [editGroundedAnswer, setEditGroundedAnswer] = useState('');
  const [editSummary, setEditSummary] = useState('');
  const [editDecisionStatus, setEditDecisionStatus] = useState('SUPPORTED');
  const [editAnalystNotes, setEditAnalystNotes] = useState('');
  const [showOriginalComparison, setShowOriginalComparison] = useState(false);

  // Edit state for Entered Information (Question Prompt)
  const [isEditingQuestion, setIsEditingQuestion] = useState(false);
  const [editedQuestionText, setEditedQuestionText] = useState('');

  // Edit state for Entered Information (Uploaded Document Details)
  const [editingDoc, setEditingDoc] = useState(null);
  const [editDocName, setEditDocName] = useState('');
  const [editDocSummary, setEditDocSummary] = useState('');
  const [editDocDate, setEditDocDate] = useState('');

  const filteredDocs = documents.filter(d =>
    d.filename.toLowerCase().includes(docSearch.toLowerCase())
  );

  const toggleDocSelect = (id) => {
    setSelectedDocIds(prev =>
      prev.includes(id) ? prev.filter(item => item !== id) : [...prev, id]
    );
  };

  const handleFileChange = async (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    try {
      await onUploadFiles(Array.from(files));
    } catch (err) {
      alert(err.message || 'Upload error');
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleAnalyzeSubmit = (e) => {
    e.preventDefault();
    if (!question.trim() || isAnalyzing) return;
    onRunAnalysis(question);
  };

  const handleSuggestionClick = (text) => {
    setQuestion(text);
    onRunAnalysis(text);
  };

  // --- Handlers for Editing Generated Information ---
  const startEditAnswer = () => {
    if (!latestResult) return;
    setEditGroundedAnswer(latestResult.grounded_answer || '');
    setEditSummary(latestResult.summary || '');
    setEditDecisionStatus(latestResult.decision_status || 'SUPPORTED');
    setEditAnalystNotes(latestResult.analyst_notes || '');
    setIsEditingAnswer(true);
  };

  const handleSaveAnswerEdits = async () => {
    if (!latestResult || !onUpdateAnalysis) return;
    try {
      await onUpdateAnalysis(latestResult.id, {
        grounded_answer: editGroundedAnswer,
        summary: editSummary,
        decision_status: editDecisionStatus,
        analyst_notes: editAnalystNotes
      });
      setIsEditingAnswer(false);
    } catch (err) {
      console.error('Failed to save answer edits:', err);
    }
  };

  const handleRevertToOriginal = async () => {
    if (!latestResult || !onUpdateAnalysis) return;
    const originalText = latestResult.original_answer || latestResult.grounded_answer;
    setEditGroundedAnswer(originalText);
    await onUpdateAnalysis(latestResult.id, {
      grounded_answer: originalText,
      analyst_notes: ''
    });
    setIsEditingAnswer(false);
    if (showToast) {
      showToast('Reverted to AI Original', 'Restored initial model generated answer.', 'info');
    }
  };

  // --- Handlers for Editing Entered Information (Question) ---
  const startEditQuestion = () => {
    if (!latestResult) return;
    setEditedQuestionText(latestResult.question);
    setIsEditingQuestion(true);
  };

  const handleSaveQuestionEdit = () => {
    if (!editedQuestionText.trim()) return;
    setIsEditingQuestion(false);
    onRunAnalysis(editedQuestionText.trim());
    if (showToast) {
      showToast('Question Updated', 'Prompt re-evaluated against indexed documents.', 'success');
    }
  };

  // --- Handlers for Editing Entered Information (Document Metadata) ---
  const startEditDoc = (doc) => {
    setEditingDoc(doc);
    setEditDocName(doc.filename);
    setEditDocSummary(doc.summary || doc.content_summary || '');
    setEditDocDate(doc.freshness_date || new Date().toISOString().slice(0, 10));
  };

  const handleSaveDocEdit = async (e) => {
    e.preventDefault();
    if (!editingDoc || !onUpdateDocument) return;
    try {
      await onUpdateDocument(editingDoc.id, {
        filename: editDocName,
        summary: editDocSummary,
        content_summary: editDocSummary,
        freshness_date: editDocDate
      });
      setEditingDoc(null);
    } catch (err) {
      console.error('Failed to save doc edits:', err);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Top Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-xl font-extrabold text-slate-900 tracking-tight font-sans">
            Document Analysis & Evidence Studio
          </h1>
          <p className="text-xs text-slate-500 font-medium">
            Ask questions about your uploaded documents, verify grounded citations, and edit answers.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => fileInputRef.current?.click()}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs transition-all shadow-sm cursor-pointer"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span>Upload Documents</span>
          </button>
          <button
            onClick={() => setQuestion('')}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 font-semibold text-xs transition-all cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5 text-slate-500" />
            <span>Clear Input</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        {/* Left Column: Select Documents Panel */}
        <div className="lg:col-span-1 saas-card rounded-2xl p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-700 font-sans">
              Select Documents
            </h2>
            <span className="text-[10px] text-blue-600 font-bold bg-blue-50 px-2 py-0.5 rounded">
              {documents.length} Available
            </span>
          </div>

          {/* Search Box */}
          <div className="relative">
            <input
              type="text"
              value={docSearch}
              onChange={(e) => setDocSearch(e.target.value)}
              placeholder="Search documents..."
              className="w-full px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 transition-all font-sans"
            />
          </div>

          {/* Document Checkbox List */}
          {documents.length === 0 ? (
            <div className="text-center py-8 space-y-2 bg-slate-50 rounded-xl border border-dashed border-slate-200">
              <FolderOpen className="w-6 h-6 text-slate-400 mx-auto" />
              <p className="text-xs font-semibold text-slate-700">No documents uploaded</p>
              <p className="text-[11px] text-slate-400">Upload PDF files to start analyzing.</p>
            </div>
          ) : (
            <div className="space-y-2 max-h-[380px] overflow-y-auto pr-1">
              {filteredDocs.map((doc) => {
                const isChecked = selectedDocIds.includes(doc.id) || selectedDocIds.length === 0;
                return (
                  <div
                    key={doc.id}
                    onClick={() => toggleDocSelect(doc.id)}
                    className={`p-3 rounded-xl border transition-all cursor-pointer flex items-start gap-3 group relative ${
                      isChecked
                        ? 'bg-blue-50/50 border-blue-200'
                        : 'bg-white border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={() => {}}
                      className="mt-1 rounded text-blue-600 focus:ring-blue-500"
                    />
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-1.5">
                        <p className="text-xs font-semibold text-slate-900 truncate" title={doc.filename}>
                          {doc.filename}
                        </p>
                        {doc.is_edited && (
                          <span className="text-[9px] px-1.5 py-0.2 bg-purple-100 text-purple-700 rounded font-bold">
                            Edited
                          </span>
                        )}
                      </div>
                      <p className="text-[10px] text-slate-400 mt-0.5">
                        {doc.page_count || 1} page(s) {doc.freshness_date && `• ${doc.freshness_date}`}
                      </p>
                    </div>

                    <div className="flex items-center gap-1 shrink-0">
                      {/* Edit Document Details Button (Constraint Card 04) */}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          startEditDoc(doc);
                        }}
                        className="text-slate-400 hover:text-blue-600 p-1 rounded-md hover:bg-slate-100 transition-colors"
                        title="Edit document details"
                      >
                        <Edit3 className="w-3.5 h-3.5" />
                      </button>

                      {/* Delete Document Button */}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onDeleteDocument(doc.id);
                        }}
                        className="text-slate-400 hover:text-rose-500 p-1 rounded-md hover:bg-slate-100 transition-colors"
                        title="Delete document"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Hidden File Input & Upload Button */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".pdf,application/pdf"
            multiple
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            className="w-full py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs border border-slate-200 flex items-center justify-center gap-2 transition-all cursor-pointer"
          >
            <Upload className="w-3.5 h-3.5" />
            <span>Upload PDF Files</span>
          </button>
        </div>

        {/* Right Column: Interactive Chat / Q&A Workspace */}
        <div className="lg:col-span-2 saas-card rounded-2xl p-6 flex flex-col justify-between min-h-[550px]">
          {/* Chat Messages Workspace */}
          <div className="space-y-6 flex-1 overflow-y-auto pr-1 pb-4">
            {latestResult ? (
              <>
                {/* User Prompt Chat Bubble (With Edit Question Option - Constraint Card 04) */}
                <div className="flex justify-end">
                  <div className="bg-indigo-600 text-white rounded-2xl rounded-tr-xs px-4 py-2.5 max-w-md shadow-sm space-y-1.5 relative group">
                    {isEditingQuestion ? (
                      <div className="space-y-2">
                        <label className="text-[10px] font-bold uppercase tracking-wider text-indigo-200 block">
                          Edit Question
                        </label>
                        <input
                          type="text"
                          value={editedQuestionText}
                          onChange={(e) => setEditedQuestionText(e.target.value)}
                          className="w-full px-2.5 py-1 text-xs rounded-lg bg-indigo-700 text-white border border-indigo-400 focus:outline-none focus:bg-indigo-800"
                        />
                        <div className="flex items-center justify-end gap-1.5 pt-1">
                          <button
                            type="button"
                            onClick={() => setIsEditingQuestion(false)}
                            className="text-[10px] text-indigo-200 hover:text-white px-2 py-0.5 rounded cursor-pointer"
                          >
                            Cancel
                          </button>
                          <button
                            type="button"
                            onClick={handleSaveQuestionEdit}
                            className="text-[10px] font-bold bg-white text-indigo-700 hover:bg-indigo-50 px-2.5 py-1 rounded shadow-xs cursor-pointer"
                          >
                            Save & Re-evaluate
                          </button>
                        </div>
                      </div>
                    ) : (
                      <>
                        <div className="flex items-start justify-between gap-3">
                          <p className="text-xs font-medium font-sans">
                            {latestResult.question}
                          </p>
                          <button
                            type="button"
                            onClick={startEditQuestion}
                            className="text-indigo-300 hover:text-white p-0.5 rounded transition-colors shrink-0 cursor-pointer"
                            title="Edit this question prompt"
                          >
                            <Edit3 className="w-3 h-3" />
                          </button>
                        </div>
                        <span className="text-[9px] text-indigo-200 block text-right font-mono">
                          {latestResult.timestamp}
                        </span>
                      </>
                    )}
                  </div>
                </div>

                {/* AI Answer Response Card (With Edit Option - Constraint Card 04) */}
                <div className="bg-slate-50 border border-slate-200 rounded-2xl p-5 space-y-4 shadow-2xs">
                  {/* Badges & Actions Header */}
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <div className="flex items-center gap-2">
                      <StatusBadge status={isEditingAnswer ? editDecisionStatus : latestResult.decision_status} />
                      
                      {latestResult.is_edited && !isEditingAnswer && (
                        <span className="inline-flex items-center gap-1 text-[10px] font-bold text-indigo-700 bg-indigo-50 border border-indigo-200 px-2 py-0.5 rounded-full">
                          <Edit3 className="w-2.5 h-2.5" />
                          Edited by Analyst
                        </span>
                      )}

                      {latestResult.decision_status === 'SUPPORTED' && !isEditingAnswer && (
                        <span className="text-[10px] font-bold text-emerald-700 bg-emerald-100 px-2.5 py-1 rounded-full border border-emerald-200">
                          {Math.round((latestResult.reliability_score || 0.9) * 100)}% Match
                        </span>
                      )}
                    </div>

                    {/* Edit Answer Action Button (Constraint Card 04) */}
                    <div>
                      {!isEditingAnswer ? (
                        <button
                          type="button"
                          onClick={startEditAnswer}
                          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white hover:bg-slate-100 text-slate-700 text-xs font-semibold border border-slate-200 shadow-2xs transition-colors cursor-pointer"
                          title="Edit generated answer and summary"
                        >
                          <Edit3 className="w-3.5 h-3.5 text-blue-600" />
                          <span>Edit Answer & Notes</span>
                        </button>
                      ) : (
                        <button
                          type="button"
                          onClick={() => setIsEditingAnswer(false)}
                          className="text-[11px] text-slate-500 hover:text-slate-800 underline cursor-pointer"
                        >
                          Close Editor
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Inline Answer Editor Mode */}
                  {isEditingAnswer ? (
                    <div className="space-y-3.5 bg-white p-4 rounded-xl border border-blue-200 shadow-sm animate-in fade-in">
                      <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                        <span className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                          <Edit3 className="w-3.5 h-3.5 text-blue-600" />
                          <span>Edit Generated Information & Analyst Notes</span>
                        </span>
                        <div className="flex items-center gap-1.5">
                          <span className="text-[10px] text-slate-500 font-semibold">Override Status:</span>
                          <select
                            value={editDecisionStatus}
                            onChange={(e) => setEditDecisionStatus(e.target.value)}
                            className="text-[11px] font-semibold border border-slate-300 rounded-lg px-2 py-1 bg-slate-50 text-slate-800 focus:outline-none"
                          >
                            <option value="SUPPORTED">SUPPORTED</option>
                            <option value="NEEDS_VERIFICATION">NEEDS_VERIFICATION</option>
                            <option value="INSUFFICIENT_EVIDENCE">INSUFFICIENT_EVIDENCE</option>
                          </select>
                        </div>
                      </div>

                      <div>
                        <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-600 mb-1">
                          Grounded Answer
                        </label>
                        <textarea
                          rows={6}
                          value={editGroundedAnswer}
                          onChange={(e) => setEditGroundedAnswer(e.target.value)}
                          className="w-full p-3 text-xs rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:border-blue-500 text-slate-900 font-sans focus:outline-none leading-relaxed"
                          placeholder="Edit grounded answer text..."
                        />
                      </div>

                      <div>
                        <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-600 mb-1">
                          Executive Summary
                        </label>
                        <input
                          type="text"
                          value={editSummary}
                          onChange={(e) => setEditSummary(e.target.value)}
                          className="w-full p-2.5 text-xs rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:border-blue-500 text-slate-900 font-sans focus:outline-none"
                          placeholder="Summary line..."
                        />
                      </div>

                      <div>
                        <label className="block text-[10px] font-bold uppercase tracking-wider text-slate-600 mb-1">
                          Analyst Annotations / Verification Notes (Optional)
                        </label>
                        <textarea
                          rows={2}
                          value={editAnalystNotes}
                          onChange={(e) => setEditAnalystNotes(e.target.value)}
                          placeholder="Add custom annotations or context, e.g.: 'Verified against internal compliance handbook'"
                          className="w-full p-2.5 text-xs rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:border-blue-500 text-slate-900 font-sans focus:outline-none"
                        />
                      </div>

                      <div className="flex items-center justify-between pt-2 border-t border-slate-100">
                        <button
                          type="button"
                          onClick={handleRevertToOriginal}
                          className="text-[11px] text-amber-700 hover:text-amber-900 font-semibold flex items-center gap-1.5 cursor-pointer"
                        >
                          <RotateCcw className="w-3 h-3" />
                          <span>Revert to AI Version</span>
                        </button>

                        <div className="flex items-center gap-2">
                          <button
                            type="button"
                            onClick={() => setIsEditingAnswer(false)}
                            className="px-3 py-1.5 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-100 text-xs font-semibold cursor-pointer"
                          >
                            Cancel
                          </button>
                          <button
                            type="button"
                            onClick={handleSaveAnswerEdits}
                            className="px-4 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold shadow-xs cursor-pointer flex items-center gap-1.5"
                          >
                            <Check className="w-3.5 h-3.5" />
                            <span>Save Changes</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  ) : (
                    /* Display Mode */
                    <div className="space-y-3">
                      <div className="text-xs text-slate-800 leading-relaxed font-sans whitespace-pre-wrap">
                        {latestResult.grounded_answer || latestResult.summary}
                      </div>

                      {latestResult.analyst_notes && (
                        <div className="p-3 bg-indigo-50/70 rounded-xl border border-indigo-100 text-xs text-indigo-950 space-y-1">
                          <span className="font-bold text-[10px] uppercase tracking-wider text-indigo-700 block">
                            Analyst Annotation:
                          </span>
                          <p className="text-[11px] italic leading-relaxed">{latestResult.analyst_notes}</p>
                        </div>
                      )}

                      {latestResult.is_edited && (
                        <div className="pt-1">
                          <button
                            type="button"
                            onClick={() => setShowOriginalComparison(!showOriginalComparison)}
                            className="text-[11px] text-blue-600 hover:underline font-semibold flex items-center gap-1 cursor-pointer"
                          >
                            <FileText className="w-3 h-3" />
                            <span>{showOriginalComparison ? 'Hide' : 'View'} Original AI Generated Text</span>
                          </button>
                          {showOriginalComparison && (
                            <div className="mt-2 p-3 bg-slate-100 rounded-xl border border-slate-200 text-xs text-slate-600 whitespace-pre-wrap">
                              <span className="font-bold text-[10px] text-slate-500 uppercase block mb-1">Original Unedited AI Output:</span>
                              {latestResult.original_answer || latestResult.summary}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Real Source Citations Section */}
                  {latestResult.supporting_evidence && latestResult.supporting_evidence.length > 0 && (
                    <div className="space-y-2.5 pt-2 border-t border-slate-200/80">
                      <p className="text-[11px] font-bold text-slate-700 uppercase tracking-wider">
                        Source Citations ({latestResult.supporting_evidence.length})
                      </p>

                      {latestResult.supporting_evidence.map((citation, idx) => (
                        <div
                          key={citation.id || idx}
                          className="p-3 rounded-xl bg-white border border-slate-200 flex items-center justify-between gap-3 text-xs shadow-2xs"
                        >
                          <div className="flex items-start gap-2.5 min-w-0">
                            <FileText className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
                            <div className="min-w-0">
                              <p className="font-bold text-slate-900 truncate">{citation.source_filename}</p>
                              <p className="text-[11px] text-slate-600 line-clamp-1 italic mt-0.5">
                                Page {citation.page_number} "{citation.passage}"
                              </p>
                            </div>
                          </div>

                          <button
                            onClick={() => onViewEvidence && onViewEvidence(citation)}
                            className="px-3 py-1 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 font-semibold text-[11px] border border-blue-200 transition-colors shrink-0 cursor-pointer"
                          >
                            View
                          </button>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Additional Evidence Needed / Upload & Re-analyze Card */}
                  {(latestResult.decision_status === 'INSUFFICIENT_EVIDENCE' || latestResult.suggested_doc_request || latestResult.missing_information) && (
                    <div className="bg-amber-50/80 border border-amber-200/90 rounded-2xl p-4 space-y-3 pt-3.5 shadow-2xs">
                      <div className="flex items-start gap-3">
                        <div className="p-2 bg-amber-100 text-amber-700 rounded-xl shrink-0 mt-0.5">
                          <AlertTriangle className="w-4 h-4" />
                        </div>
                        <div className="space-y-1 min-w-0 flex-1">
                          <h4 className="text-xs font-bold text-amber-900 tracking-tight">
                            Additional Evidence Required
                          </h4>
                          <p className="text-[11px] text-amber-800 leading-relaxed">
                            {latestResult.suggested_doc_request ||
                              'The available document set lacks sufficient evidence to answer this question accurately.'}
                          </p>
                          {latestResult.missing_information && (
                            <div className="mt-2 text-[11px] text-amber-900 bg-amber-100/60 p-2.5 rounded-xl border border-amber-200/50">
                              <span className="font-semibold block mb-1">Missing Information Identified:</span>
                              {Array.isArray(latestResult.missing_information) ? (
                                <ul className="list-disc list-inside space-y-0.5 text-amber-800">
                                  {latestResult.missing_information.map((item, idx) => <li key={idx}>{item}</li>)}
                                </ul>
                              ) : (
                                <p className="text-amber-800">{latestResult.missing_information}</p>
                              )}
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="pt-2 border-t border-amber-200/60 flex items-center justify-between flex-wrap gap-2">
                        <span className="text-[10px] text-amber-700 font-medium">
                          Upload missing document to automatically re-analyze original query.
                        </span>
                        <label className="cursor-pointer inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-amber-600 hover:bg-amber-700 text-white text-xs font-semibold shadow-xs transition-all">
                          <Upload className="w-3.5 h-3.5" />
                          <span>Upload & Re-analyze</span>
                          <input
                            type="file"
                            accept=".pdf,application/pdf"
                            className="hidden"
                            onChange={async (e) => {
                              const file = e.target.files?.[0];
                              if (file && onUploadAndReanalyze) {
                                await onUploadAndReanalyze(file, latestResult.question);
                              }
                              e.target.value = '';
                            }}
                          />
                        </label>
                      </div>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="text-center py-16 space-y-3">
                <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto border border-blue-100 shadow-sm">
                  <Sparkles className="w-6 h-6 text-blue-600" />
                </div>
                <div className="max-w-md mx-auto">
                  <h3 className="text-sm font-bold text-slate-900">Ask your question</h3>
                  <p className="text-xs text-slate-500 leading-relaxed mt-1">
                    Type a question below to analyze your uploaded PDF documents or query domain knowledge with evidence citations.
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Bottom Chat Bar & Suggestion Pills */}
          <div className="space-y-3 pt-3 border-t border-slate-200">
            <form onSubmit={handleAnalyzeSubmit} className="relative flex items-center">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask a question about your documents..."
                className="w-full pl-4 pr-20 py-3 rounded-2xl bg-slate-50 border border-slate-200 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:bg-white transition-all font-sans"
              />
              <div className="absolute right-2 flex items-center gap-1.5">
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="p-2 text-slate-400 hover:text-slate-600 rounded-xl transition-colors cursor-pointer"
                  title="Attach file"
                >
                  <Paperclip className="w-4 h-4" />
                </button>
                <button
                  type="submit"
                  disabled={!question.trim() || isAnalyzing}
                  className="w-8 h-8 rounded-full bg-blue-600 hover:bg-blue-700 text-white flex items-center justify-center transition-all disabled:opacity-50 shadow-md shadow-blue-500/20 cursor-pointer"
                >
                  {isAnalyzing ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-3.5 h-3.5" />
                  )}
                </button>
              </div>
            </form>

            {/* Quick Suggestion Pills */}
            <div className="flex items-center gap-2 overflow-x-auto text-[10px]">
              <span className="text-slate-400 shrink-0 font-medium">Suggestions:</span>
              {[
                "What are the Five Vs of Big Data?",
                "What are the key compliance rules?",
                "What are the core requirements?"
              ].map((pill, i) => (
                <button
                  key={i}
                  onClick={() => handleSuggestionClick(pill)}
                  className="px-3 py-1 rounded-full bg-slate-100 hover:bg-blue-50 text-slate-700 hover:text-blue-600 border border-slate-200 transition-all font-medium whitespace-nowrap cursor-pointer"
                >
                  {pill}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Edit Document Details Modal (Constraint Card 04) */}
      {editingDoc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs animate-in fade-in">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 space-y-4 text-left">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Edit3 className="w-4 h-4 text-blue-600" />
                <span>Edit Document Information</span>
              </h3>
              <button
                onClick={() => setEditingDoc(null)}
                className="p-1 text-slate-400 hover:text-slate-600 rounded-lg cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSaveDocEdit} className="space-y-3">
              <div>
                <label className="block text-[11px] font-bold text-slate-700 mb-1">
                  Document Display Title
                </label>
                <input
                  type="text"
                  required
                  value={editDocName}
                  onChange={(e) => setEditDocName(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:border-blue-500 text-slate-900"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-700 mb-1">
                  Freshness Date
                </label>
                <input
                  type="date"
                  value={editDocDate}
                  onChange={(e) => setEditDocDate(e.target.value)}
                  className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:border-blue-500 text-slate-900"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-700 mb-1">
                  Summary / Description
                </label>
                <textarea
                  rows={3}
                  value={editDocSummary}
                  onChange={(e) => setEditDocSummary(e.target.value)}
                  placeholder="Describe document topic or internal purpose..."
                  className="w-full px-3 py-2 text-xs rounded-xl bg-slate-50 border border-slate-200 focus:bg-white focus:border-blue-500 text-slate-900"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setEditingDoc(null)}
                  className="px-3.5 py-1.5 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-100 text-xs font-semibold cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold shadow-xs cursor-pointer"
                >
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
