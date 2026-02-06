'use client';

import { useEffect, useState } from 'react';
import { authService } from '@/lib/auth';
import api from '@/lib/api';

export default function AuthTestPage() {
  const [authStatus, setAuthStatus] = useState<any>(null);

  useEffect(() => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    const user = authService.getCurrentUser();
    
    setAuthStatus({
      isAuthenticated: authService.isAuthenticated(),
      hasToken: !!token,
      tokenValue: token ? `${token.substring(0, 20)}...` : null,
      user: user,
    });
  }, []);

  const testProtectedEndpoint = async () => {
    try {
      const response = await api.get('/assessments/01600d71-bae2-4e8e-8c96-9e7a4f229098/questions');
      alert('SUCCESS: ' + JSON.stringify(response.data, null, 2));
    } catch (error: any) {
      alert('ERROR: ' + error.message + '\nStatus: ' + error.response?.status);
      console.error('Protected endpoint error:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Authentication Status</h1>
        
        <div className="bg-white border rounded-lg p-6 mb-6">
          <pre className="text-sm">{JSON.stringify(authStatus, null, 2)}</pre>
        </div>

        <button
          onClick={testProtectedEndpoint}
          className="btn-primary"
        >
          Test Protected Endpoint (/questions)
        </button>

        <div className="mt-8 bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Issue Found</h2>
          <p className="mb-4">The <code>/assessments/{'{id}'}/questions</code> endpoint requires authentication.</p>
          <p className="mb-4">If you're not logged in or your token is invalid, you'll get a 401 error.</p>
          <p><strong>Solution:</strong> Log in first, then try accessing assessments.</p>
        </div>
      </div>
    </div>
  );
}
