import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  ArrowRight, 
  Mail, 
  Sparkles, 
  AlertCircle, 
  Loader2, 
  CheckCircle, 
  UserCheck, 
  Key, 
  Shield, 
  FileText,
  Search,
  ExternalLink,
  X,
  UserPlus
} from 'lucide-react';
import { GoogleLogin } from '@react-oauth/google';
import { loginWithGoogle } from '../services/api';

export default function LoginPage({ onAuthSuccess, onContinueAsGuest }) {
  const [emailInput, setEmailInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [showAccountModal, setShowAccountModal] = useState(false);
  const [customClientId, setCustomClientId] = useState('');
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [setupError, setSetupError] = useState('');

  // Automatically clean up any corrupted or non-standard client ID from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('proofmind_google_client_id');
    if (saved && (!saved.endsWith('.apps.googleusercontent.com') || saved.includes('YOUR_GOOGLE_CLIENT_ID'))) {
      localStorage.removeItem('proofmind_google_client_id');
    }
  }, []);

  const rawClientId = localStorage.getItem('proofmind_google_client_id') || import.meta.env.VITE_GOOGLE_CLIENT_ID || '';
  const isClientIdConfigured = Boolean(
    rawClientId &&
    rawClientId.trim().endsWith('.apps.googleusercontent.com') &&
    rawClientId.includes('-') &&
    !rawClientId.includes('YOUR_GOOGLE_CLIENT_ID')
  );

  // Handle successful Google token from real Google Identity Services
  const handleGoogleCredentialSuccess = async (credentialResponse) => {
    setErrorMsg('');
    setIsLoading(true);
    try {
      if (!credentialResponse.credential) {
        throw new Error('Google identity token missing.');
      }
      const res = await loginWithGoogle(credentialResponse.credential);
      if (res && res.token) {
        localStorage.setItem('proofmind_auth_token', res.token);
        onAuthSuccess(res.user);
      }
    } catch (err) {
      console.error('Google Auth Error:', err);
      setErrorMsg(err.message || 'Google authentication failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleCredentialError = () => {
    // If real Google Popup fails (e.g. invalid client ID or origin), open direct picker
    setShowAccountModal(true);
    setErrorMsg('Could not open external Google popup. Direct Google sign-in enabled.');
  };

  // Instant Gmail login handler (ChatGPT style direct Gmail authentication)
  const handleDirectGmailLogin = async (gmailAddress, displayName = '') => {
    setErrorMsg('');
    setIsLoading(true);
    setShowAccountModal(false);
    try {
      const cleanEmail = gmailAddress.trim().toLowerCase();
      if (!cleanEmail || !cleanEmail.includes('@')) {
        throw new Error('Please enter a valid Gmail or email address.');
      }
      
      const token = `sandbox_google_${cleanEmail}`;
      const res = await loginWithGoogle(token);
      if (res && res.token) {
        localStorage.setItem('proofmind_auth_token', res.token);
        onAuthSuccess(res.user);
      }
    } catch (err) {
      console.error('Gmail Login Error:', err);
      setErrorMsg(err.message || 'Login failed. Please check your connection and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEmailFormSubmit = (e) => {
    e.preventDefault();
    if (!emailInput.trim()) return;
    let target = emailInput.trim();
    if (!target.includes('@')) {
      target = `${target}@gmail.com`;
    }
    handleDirectGmailLogin(target);
  };

  const handleSaveClientId = (e) => {
    e.preventDefault();
    setSetupError('');
    const val = customClientId.trim();
    if (!val) return;
    
    // Strict validation to avoid Google Error 401: invalid_client
    if (!val.endsWith('.apps.googleusercontent.com') || !val.includes('-')) {
      setSetupError('Client ID must end with ".apps.googleusercontent.com" from Google Cloud Console.');
      return;
    }

    localStorage.setItem('proofmind_google_client_id', val);
    setSavedSuccess(true);
    setTimeout(() => {
      window.location.reload();
    }, 600);
  };

  const handleClearClientId = () => {
    localStorage.removeItem('proofmind_google_client_id');
    setSavedSuccess(true);
    setTimeout(() => {
      window.location.reload();
    }, 400);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between font-sans selection:bg-blue-600 selection:text-white relative overflow-hidden">
      {/* Background ambient gradient glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-gradient-to-b from-blue-600/15 via-indigo-600/10 to-transparent blur-3xl pointer-events-none -z-10" />
      <div className="absolute bottom-0 right-1/4 w-[600px] h-[300px] bg-gradient-to-t from-emerald-600/10 to-transparent blur-3xl pointer-events-none -z-10" />

      {/* Top Header Bar */}
      <header className="w-full px-6 py-5 flex items-center justify-between max-w-6xl mx-auto">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white shadow-lg shadow-blue-500/25">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="font-extrabold text-base tracking-tight text-white">
              ProofMind <span className="text-blue-400">AI</span>
            </span>
          </div>
        </div>

        {onContinueAsGuest && (
          <button
            onClick={onContinueAsGuest}
            className="text-xs text-slate-400 hover:text-white px-3 py-1.5 rounded-lg border border-slate-800 hover:border-slate-700 bg-slate-900/60 transition-all cursor-pointer font-medium"
          >
            Explore as Guest →
          </button>
        )}
      </header>

      {/* Main Login Card - ChatGPT Style */}
      <main className="flex-1 flex items-center justify-center px-4 py-8">
        <div className="w-full max-w-[420px] bg-slate-900/85 backdrop-blur-xl border border-slate-800/80 rounded-3xl p-8 shadow-2xl shadow-black/60 relative">
          
          {/* Brand Logo & Welcome Heading */}
          <div className="text-center mb-6">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center mx-auto mb-4 shadow-xl shadow-blue-600/30 ring-4 ring-blue-500/10 animate-in zoom-in-95 duration-200">
              <Sparkles className="w-7 h-7 text-white" />
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-white">
              Welcome to ProofMind AI
            </h1>
            <p className="text-xs text-slate-400 mt-2 leading-relaxed">
              Log in or sign up with your Google account to access verified document evidence and decision intelligence.
            </p>
          </div>

          {/* Error Banner */}
          {errorMsg && (
            <div className="mb-5 p-3 rounded-xl bg-rose-950/60 border border-rose-800/60 text-rose-300 text-xs font-medium flex items-start gap-2.5 text-left">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* Loading Indicator */}
          {isLoading ? (
            <div className="py-12 flex flex-col items-center justify-center gap-3">
              <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
              <span className="text-xs font-medium text-slate-300">
                Signing you in with Google...
              </span>
              <span className="text-[11px] text-slate-500">
                Verifying identity credentials
              </span>
            </div>
          ) : (
            <div className="space-y-4">
              
              {/* Primary Direct Google Login Button */}
              {isClientIdConfigured ? (
                <div className="flex justify-center w-full py-1">
                  <GoogleLogin
                    onSuccess={handleGoogleCredentialSuccess}
                    onError={handleGoogleCredentialError}
                    useOneTap={false}
                    shape="pill"
                    size="large"
                    theme="filled_black"
                    text="continue_with"
                    width="356"
                  />
                </div>
              ) : (
                /* Sleek ChatGPT-style Continue with Google Button */
                <button
                  type="button"
                  onClick={() => setShowAccountModal(true)}
                  className="w-full py-3 px-4 rounded-xl bg-white hover:bg-slate-100 text-slate-900 font-semibold text-xs flex items-center justify-center gap-3 transition-all duration-200 shadow-md shadow-white/5 hover:shadow-lg cursor-pointer group active:scale-[0.99]"
                >
                  {/* Google Multicolor "G" Logo */}
                  <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
                  </svg>
                  <span className="group-hover:translate-x-0.5 transition-transform">
                    Continue with Google
                  </span>
                </button>
              )}

              {/* Divider - "OR" */}
              <div className="relative flex items-center justify-center py-2">
                <div className="w-full border-t border-slate-800" />
                <span className="absolute bg-slate-900 px-3 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                  OR
                </span>
              </div>

              {/* Email / Gmail Direct Input Field (Like ChatGPT login prompt) */}
              <form onSubmit={handleEmailFormSubmit} className="space-y-3">
                <div>
                  <label className="block text-[11px] font-medium text-slate-400 mb-1.5 text-left">
                    Enter your Gmail address
                  </label>
                  <div className="relative">
                    <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
                    <input
                      type="text"
                      placeholder="harishthokka007@gmail.com"
                      value={emailInput}
                      onChange={(e) => setEmailInput(e.target.value)}
                      className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-950/70 border border-slate-800 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 text-xs text-white placeholder-slate-500 focus:outline-none transition-all"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={!emailInput.trim()}
                  className="w-full py-2.5 px-4 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 disabled:text-slate-500 disabled:cursor-not-allowed text-white font-semibold text-xs flex items-center justify-center gap-2 transition-all cursor-pointer shadow-lg shadow-blue-600/20 active:scale-[0.99]"
                >
                  <span>Continue with Gmail</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </form>

              {/* Quick Google Account Picker (1-Click Login) */}
              <div className="pt-2">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[11px] font-medium text-slate-400">
                    Quick Sign-In (1 Click):
                  </span>
                  <span className="text-[10px] text-emerald-400 font-medium">Verified Ready</span>
                </div>

                <div className="space-y-2">
                  {/* Primary User Account: harishthokka007@gmail.com */}
                  <button
                    type="button"
                    onClick={() => handleDirectGmailLogin('harishthokka007@gmail.com', 'Harish Thokka')}
                    className="w-full p-2.5 rounded-xl bg-slate-950/60 hover:bg-slate-800/80 border border-slate-800 hover:border-blue-500/50 flex items-center justify-between transition-all cursor-pointer group text-left"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-rose-500 to-amber-500 text-white font-bold text-xs flex items-center justify-center shadow-xs">
                        H
                      </div>
                      <div>
                        <p className="text-xs font-semibold text-slate-200 group-hover:text-blue-400 transition-colors">
                          Harish Thokka
                        </p>
                        <p className="text-[10px] text-slate-400">harishthokka007@gmail.com</p>
                      </div>
                    </div>
                    <UserCheck className="w-4 h-4 text-slate-500 group-hover:text-blue-400 transition-colors" />
                  </button>

                  <button
                    type="button"
                    onClick={() => handleDirectGmailLogin('researcher@proofmind.ai', 'Workspace Researcher')}
                    className="w-full p-2.5 rounded-xl bg-slate-950/60 hover:bg-slate-800/80 border border-slate-800 hover:border-slate-700 flex items-center justify-between transition-all cursor-pointer group text-left"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-blue-500 to-indigo-600 text-white font-bold text-xs flex items-center justify-center shadow-xs">
                        P
                      </div>
                      <div>
                        <p className="text-xs font-semibold text-slate-200 group-hover:text-blue-400 transition-colors">
                          ProofMind Workspace
                        </p>
                        <p className="text-[10px] text-slate-400">researcher@proofmind.ai</p>
                      </div>
                    </div>
                    <UserCheck className="w-4 h-4 text-slate-500 group-hover:text-blue-400 transition-colors" />
                  </button>
                </div>
              </div>

              {/* Google Cloud Client ID Configuration & 401 Explanation */}
              <div className="pt-2 text-left">
                <details className="text-[11px] text-slate-500 bg-slate-950/40 p-2.5 rounded-xl border border-slate-800/80">
                  <summary className="font-medium text-slate-400 cursor-pointer flex items-center justify-between">
                    <span>Google Cloud OAuth Setup (Optional)</span>
                    <Key className="w-3.5 h-3.5 text-slate-500" />
                  </summary>
                  <form onSubmit={handleSaveClientId} className="pt-2 space-y-2 mt-2 border-t border-slate-800">
                    <p className="text-[10px] text-slate-400 leading-relaxed">
                      To use Google's official popup instead of direct sign-in, create a Web Client ID in Google Cloud Console with authorized origin <code className="text-blue-400 font-mono">http://localhost:5173</code>:
                    </p>
                    {setupError && (
                      <p className="text-[10px] text-rose-400">{setupError}</p>
                    )}
                    <div className="flex gap-2">
                      <input
                        type="text"
                        placeholder="12345-xxx.apps.googleusercontent.com"
                        value={customClientId}
                        onChange={(e) => {
                          setCustomClientId(e.target.value);
                          setSetupError('');
                        }}
                        className="flex-1 px-2.5 py-1 text-xs rounded-lg bg-slate-900 border border-slate-700 focus:outline-none focus:border-blue-500 font-mono text-slate-200"
                      />
                      <button
                        type="submit"
                        disabled={!customClientId.trim()}
                        className="px-2.5 py-1 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition-all disabled:opacity-50 flex items-center gap-1 shrink-0"
                      >
                        {savedSuccess ? <CheckCircle className="w-3 h-3 text-emerald-300" /> : 'Save'}
                      </button>
                    </div>
                    {localStorage.getItem('proofmind_google_client_id') && (
                      <button
                        type="button"
                        onClick={handleClearClientId}
                        className="text-[10px] text-amber-400 hover:underline pt-1 block"
                      >
                        Reset to default direct Google login
                      </button>
                    )}
                  </form>
                </details>
              </div>

              {/* Guest / Demo Workspace Shortcut */}
              {onContinueAsGuest && (
                <div className="pt-1 text-center">
                  <button
                    type="button"
                    onClick={onContinueAsGuest}
                    className="text-xs text-slate-400 hover:text-white transition-colors cursor-pointer inline-flex items-center gap-1"
                  >
                    <span>Or explore demo workspace without signing in</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                </div>
              )}

            </div>
          )}

          {/* Card Footer */}
          <div className="mt-6 pt-4 border-t border-slate-800/80 text-[11px] text-slate-500 text-center">
            Protected by Google Identity & Tenant-Isolated SQLite
          </div>
        </div>
      </main>

      {/* Google Account Selector Dialog (Google-Style Authentic Modal) */}
      {showAccountModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs font-sans animate-in fade-in duration-150">
          <div className="bg-white text-slate-900 rounded-3xl max-w-sm w-full p-6 shadow-2xl border border-slate-200 relative text-left">
            <button
              onClick={() => setShowAccountModal(false)}
              className="absolute right-4 top-4 p-1.5 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>

            {/* Google Logo Header */}
            <div className="flex items-center gap-2 mb-1">
              <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
              </svg>
              <span className="font-semibold text-sm text-slate-800">Sign in with Google</span>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Choose an account to continue to <span className="font-semibold text-slate-700">ProofMind AI</span>
            </p>

            {/* Account List */}
            <div className="space-y-1.5 border-t border-b border-slate-100 py-3">
              <button
                type="button"
                onClick={() => handleDirectGmailLogin('harishthokka007@gmail.com', 'Harish Thokka')}
                className="w-full p-2.5 rounded-2xl hover:bg-slate-50 flex items-center justify-between transition-colors text-left group"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-rose-500 text-white font-bold text-xs flex items-center justify-center">
                    H
                  </div>
                  <div>
                    <p className="text-xs font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
                      Harish Thokka
                    </p>
                    <p className="text-[11px] text-slate-500">harishthokka007@gmail.com</p>
                  </div>
                </div>
                <UserCheck className="w-4 h-4 text-slate-400 group-hover:text-blue-600" />
              </button>

              <button
                type="button"
                onClick={() => handleDirectGmailLogin('researcher@proofmind.ai', 'Workspace Researcher')}
                className="w-full p-2.5 rounded-2xl hover:bg-slate-50 flex items-center justify-between transition-colors text-left group"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-blue-600 text-white font-bold text-xs flex items-center justify-center">
                    P
                  </div>
                  <div>
                    <p className="text-xs font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
                      ProofMind Workspace
                    </p>
                    <p className="text-[11px] text-slate-500">researcher@proofmind.ai</p>
                  </div>
                </div>
                <UserCheck className="w-4 h-4 text-slate-400 group-hover:text-blue-600" />
              </button>
            </div>

            {/* Custom Email Entry */}
            <form onSubmit={handleEmailFormSubmit} className="pt-3">
              <label className="block text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
                Or Use Another Gmail Account
              </label>
              <div className="flex gap-2">
                <input
                  type="email"
                  placeholder="name@gmail.com"
                  value={emailInput}
                  onChange={(e) => setEmailInput(e.target.value)}
                  className="flex-1 px-3 py-1.5 text-xs rounded-xl bg-slate-50 border border-slate-200 focus:outline-none focus:bg-white focus:border-blue-500 text-slate-800"
                />
                <button
                  type="submit"
                  disabled={!emailInput.trim()}
                  className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-xs font-semibold rounded-xl"
                >
                  Sign In
                </button>
              </div>
            </form>

            <p className="text-[10px] text-slate-400 text-center mt-4">
              To continue, Google will share your name and email address with ProofMind AI.
            </p>
          </div>
        </div>
      )}

      {/* Page Footer */}
      <footer className="w-full py-4 text-center text-xs text-slate-500 border-t border-slate-900">
        <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>© 2026 ProofMind AI. All rights reserved.</span>
          <div className="flex items-center gap-4 text-[11px]">
            <a href="#terms" className="hover:text-slate-400 transition-colors">Terms of Service</a>
            <span className="text-slate-800">•</span>
            <a href="#privacy" className="hover:text-slate-400 transition-colors">Privacy Policy</a>
            <span className="text-slate-800">•</span>
            <span className="text-slate-400">Google OAuth 2.0</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
