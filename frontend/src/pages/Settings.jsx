import React from 'react';
import { Settings as SettingsIcon, Shield, Server, Cpu, Database, Key } from 'lucide-react';

export default function Settings() {
  return (
    <div className="space-y-6 animate-fadeIn max-w-4xl">
      <div>
        <h1 className="text-xl font-extrabold text-slate-900 tracking-tight font-sans flex items-center gap-2">
          <SettingsIcon className="w-5 h-5 text-blue-600" />
          System Settings
        </h1>
        <p className="text-xs text-slate-500 font-medium">
          Configure API connections, reasoning thresholds, and project metadata.
        </p>
      </div>

      <div className="space-y-4">
        {/* Card 1 */}
        <div className="saas-card rounded-2xl p-5 space-y-4">
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
            <Server className="w-4 h-4 text-blue-600" />
            Backend API Configuration
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block text-[11px] font-semibold text-slate-600 mb-1">API Base URL</label>
              <input
                type="text"
                readOnly
                value="http://localhost:8000/api/v1"
                className="w-full px-3 py-2 rounded-xl bg-slate-100 border border-slate-200 text-slate-700 font-mono"
              />
            </div>
            <div>
              <label className="block text-[11px] font-semibold text-slate-600 mb-1">Environment</label>
              <input
                type="text"
                readOnly
                value="Development (Hackathon Mode)"
                className="w-full px-3 py-2 rounded-xl bg-slate-100 border border-slate-200 text-slate-700 font-mono"
              />
            </div>
          </div>
        </div>

        {/* Card 2 */}
        <div className="saas-card rounded-2xl p-5 space-y-4">
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
            <Cpu className="w-4 h-4 text-purple-600" />
            Evidence & Contradiction Reasoning
          </h2>

          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-200">
              <div>
                <p className="font-semibold text-slate-900">Strict Contradiction Threshold</p>
                <p className="text-[11px] text-slate-500">Flag conflicts when passage similarity &gt; 75%</p>
              </div>
              <input type="checkbox" defaultChecked className="rounded text-blue-600" />
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-200">
              <div>
                <p className="font-semibold text-slate-900">Enforce Date Precedence Warnings</p>
                <p className="text-[11px] text-slate-500">Do not automatically treat newest file as authoritative</p>
              </div>
              <input type="checkbox" defaultChecked className="rounded text-blue-600" />
            </div>
          </div>
        </div>

        {/* Card 3 */}
        <div className="saas-card rounded-2xl p-5 space-y-2">
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-2">
            <Shield className="w-4 h-4 text-emerald-600" />
            Team & Project Credits
          </h2>
          <p className="text-xs text-slate-600">
            <strong>Project:</strong> ProofMind AI (PS-01 — Evidence-Aware AI Decision Engine)<br />
            <strong>Team:</strong> Team NeverExist<br />
            <strong>Institution:</strong> Vishnu Institute of Technology
          </p>
        </div>
      </div>
    </div>
  );
}
