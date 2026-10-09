import React from 'react'
import ReactDOM from 'react-dom/client'
import { GoogleOAuthProvider } from '@react-oauth/google'
import App from './App.jsx'
import './index.css'

const rawClientId = localStorage.getItem('proofmind_google_client_id') || import.meta.env.VITE_GOOGLE_CLIENT_ID || '';
const isRealClientId = Boolean(
  rawClientId &&
  rawClientId.trim().endsWith('.apps.googleusercontent.com') &&
  rawClientId.includes('-') &&
  !rawClientId.includes('YOUR_GOOGLE_CLIENT_ID')
);

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    {isRealClientId ? (
      <GoogleOAuthProvider clientId={rawClientId.trim()}>
        <App isGoogleOAuthConfigured={true} />
      </GoogleOAuthProvider>
    ) : (
      <App isGoogleOAuthConfigured={false} />
    )}
  </React.StrictMode>,
)

