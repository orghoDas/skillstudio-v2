'use client';

import { useEffect, useState } from 'react';
import api from '@/lib/api';

export default function ApiTestPage() {
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const testDirectBackend = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await fetch('http://localhost:8000/api/v1/assessments');
      const data = await response.json();
      setResult({ type: 'Direct Backend', status: response.status, data });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const testNextProxy = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await fetch('/api/v1/assessments');
      const data = await response.json();
      setResult({ type: 'Next.js Proxy (fetch)', status: response.status, data });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const testAxios = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await api.get('/assessments');
      setResult({ type: 'Axios (from lib/api.ts)', status: response.status, data: response.data });
    } catch (err: any) {
      setError(`Status: ${err.response?.status || 'N/A'}, Message: ${err.message}`);
      console.error('Axios error details:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">API Connection Test</h1>
        
        <div className="space-y-4 mb-8">
          <button
            onClick={testDirectBackend}
            disabled={loading}
            className="btn-primary mr-4"
          >
            Test Direct Backend (localhost:8000)
          </button>
          
          <button
            onClick={testNextProxy}
            disabled={loading}
            className="btn-primary mr-4"
          >
            Test Next.js Proxy (fetch)
          </button>
          
          <button
            onClick={testAxios}
            disabled={loading}
            className="btn-primary"
          >
            Test Axios (actual service)
          </button>
        </div>

        {loading && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-blue-800">Loading...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <h3 className="font-semibold text-red-900 mb-2">Error</h3>
            <p className="text-red-700 font-mono text-sm">{error}</p>
          </div>
        )}

        {result && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h3 className="font-semibold text-green-900 mb-2">Success - {result.type}</h3>
            <p className="text-green-700 mb-4">Status: {result.status}</p>
            <pre className="bg-white border border-green-200 rounded p-4 overflow-auto max-h-96 text-xs">
              {JSON.stringify(result.data, null, 2)}
            </pre>
          </div>
        )}

        <div className="mt-8 bg-white border border-gray-200 rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Instructions</h2>
          <ol className="list-decimal list-inside space-y-2 text-gray-700">
            <li>Open browser DevTools (F12)</li>
            <li>Go to Console tab</li>
            <li>Click each button and check:
              <ul className="list-disc list-inside ml-6 mt-2">
                <li>Console logs showing request details</li>
                <li>Network tab showing actual HTTP requests</li>
                <li>Any error messages or stack traces</li>
              </ul>
            </li>
          </ol>
        </div>
      </div>
    </div>
  );
}
