const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://proofmind-ai.onrender.com/api/v1';

function getAuthHeaders() {
  const token = localStorage.getItem('proofmind_auth_token');
  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    if (!res.ok) throw new Error('Health check failed');
    return await res.json();
  } catch (err) {
    console.warn('Backend health check warning:', err.message);
    return { status: 'offline', message: 'Backend unreachable' };
  }
}

// --- Auth API ---
export async function registerUser(email, fullName, password) {
  const res = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, full_name: fullName, password }),
  });
  if (!res.ok) {
    const errorData = await res.json();
    throw new Error(errorData.detail || 'Registration failed');
  }
  return await res.json();
}

export async function loginUser(email, password) {
  const res = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const errorData = await res.json();
    throw new Error(errorData.detail || 'Login failed');
  }
  return await res.json();
}

export async function loginWithGoogle(googleToken) {
  const res = await fetch(`${API_BASE_URL}/auth/google`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token: googleToken }),
  });
  if (!res.ok) {
    const errorData = await res.json();
    throw new Error(errorData.detail || 'Google authentication failed');
  }
  return await res.json();
}

export async function fetchCurrentUser() {
  try {
    const res = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: { ...getAuthHeaders() }
    });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

export async function logoutUser() {
  try {
    await fetch(`${API_BASE_URL}/auth/logout`, {
      method: 'POST',
      headers: { ...getAuthHeaders() }
    });
  } catch (e) {
    console.warn('Logout error:', e);
  } finally {
    localStorage.removeItem('proofmind_auth_token');
  }
}

// --- Documents API ---
export async function fetchDocuments() {
  try {
    const res = await fetch(`${API_BASE_URL}/documents`, {
      headers: { ...getAuthHeaders() }
    });
    if (!res.ok) throw new Error('Failed to fetch documents');
    return await res.json();
  } catch (err) {
    console.warn('API error fetching documents:', err.message);
    return null;
  }
}

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch(`${API_BASE_URL}/documents/upload`, {
      method: 'POST',
      headers: { ...getAuthHeaders() },
      body: formData,
    });
    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.detail || 'Upload failed');
    }
    return await res.json();
  } catch (err) {
    console.error('Document upload error:', err);
    throw err;
  }
}

export async function uploadMultipleDocuments(files) {
  const formData = new FormData();
  for (const file of files) {
    formData.append('files', file);
  }

  try {
    const res = await fetch(`${API_BASE_URL}/documents/upload-batch`, {
      method: 'POST',
      headers: { ...getAuthHeaders() },
      body: formData,
    });
    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.detail || 'Batch upload failed');
    }
    return await res.json();
  } catch (err) {
    console.error('Batch upload error:', err);
    throw err;
  }
}

export async function deleteDocumentApi(documentId) {
  try {
    const res = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
      method: 'DELETE',
      headers: { ...getAuthHeaders() }
    });
    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.detail || 'Failed to delete document');
    }
    return await res.json();
  } catch (err) {
    console.error('Delete document error:', err);
    throw err;
  }
}

// --- Analysis API ---
export async function runAnalysis(question, documentIds = null) {
  try {
    const res = await fetch(`${API_BASE_URL}/analysis/run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      body: JSON.stringify({ question, document_ids: documentIds }),
    });

    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.detail || 'Analysis request failed');
    }
    return await res.json();
  } catch (err) {
    console.error('Analysis error:', err);
    throw err;
  }
}

export async function fetchAnalysisHistory() {
  try {
    const res = await fetch(`${API_BASE_URL}/analysis/history`, {
      headers: { ...getAuthHeaders() }
    });
    if (!res.ok) throw new Error('Failed to fetch history');
    return await res.json();
  } catch (err) {
    console.warn('API error fetching analysis history:', err.message);
    return null;
  }
}

// --- Conversations API ---
export async function fetchConversations() {
  try {
    const res = await fetch(`${API_BASE_URL}/conversations`, {
      headers: { ...getAuthHeaders() }
    });
    if (!res.ok) throw new Error('Failed to fetch conversations');
    return await res.json();
  } catch (err) {
    console.warn('API error fetching conversations:', err.message);
    return [];
  }
}

export async function createConversation(title = 'New Document Analysis Conversation', documentIds = null) {
  const res = await fetch(`${API_BASE_URL}/conversations`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders()
    },
    body: JSON.stringify({ title, document_ids: documentIds }),
  });
  if (!res.ok) {
    const errorData = await res.json();
    throw new Error(errorData.detail || 'Failed to create conversation');
  }
  return await res.json();
}

export async function fetchConversationDetail(convId) {
  const res = await fetch(`${API_BASE_URL}/conversations/${convId}`, {
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) throw new Error('Failed to fetch conversation details');
  return await res.json();
}

export async function sendConversationMessage(convId, question, documentIds = null) {
  const res = await fetch(`${API_BASE_URL}/conversations/${convId}/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders()
    },
    body: JSON.stringify({ question, document_ids: documentIds }),
  });
  if (!res.ok) {
    const errorData = await res.json();
    throw new Error(errorData.detail || 'Failed to send message');
  }
  return await res.json();
}

export async function uploadAndReanalyze(convId, file, originalQuestion = null) {
  const formData = new FormData();
  formData.append('file', file);
  if (originalQuestion) {
    formData.append('original_question', originalQuestion);
  }

  const res = await fetch(`${API_BASE_URL}/conversations/${convId}/upload-and-reanalyze`, {
    method: 'POST',
    headers: { ...getAuthHeaders() },
    body: formData,
  });
  if (!res.ok) {
    const errorData = await res.json();
    throw new Error(errorData.detail || 'Reanalysis request failed');
  }
  return await res.json();
}

export async function deleteConversation(convId) {
  const res = await fetch(`${API_BASE_URL}/conversations/${convId}`, {
    method: 'DELETE',
    headers: { ...getAuthHeaders() }
  });
  if (!res.ok) throw new Error('Failed to delete conversation');
  return await res.json();
}

// --- Information Editing APIs (Constraint Card 04) ---
export async function updateAnalysisApi(analysisId, updates) {
  const res = await fetch(`${API_BASE_URL}/analysis/${analysisId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders()
    },
    body: JSON.stringify(updates),
  });
  if (!res.ok) {
    const errorData = await res.json();
    throw new Error(errorData.detail || 'Failed to update analysis');
  }
  return await res.json();
}

export async function updateDocumentApi(documentId, updates) {
  const res = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders()
    },
    body: JSON.stringify(updates),
  });
  if (!res.ok) {
    const errorData = await res.json();
    throw new Error(errorData.detail || 'Failed to update document');
  }
  return await res.json();
}
