'use client';

import { useEffect, useState, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import dynamic from 'next/dynamic';
import {
  getCollaborativeSession,
  getSessionParticipants,
  CollaborativeSession,
  Participant,
  CollaborativeWebSocket,
  CodeUpdate,
  getLanguageDisplayName,
  getMonacoLanguage,
} from '@/lib/collaborative-service';
import { Users, Wifi, WifiOff, ArrowLeft, Copy, Check } from 'lucide-react';

// Dynamically import Monaco Editor to avoid SSR issues
const MonacoEditor = dynamic(() => import('@monaco-editor/react'), { ssr: false });

export default function CollaborativeEditorPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.id as string;

  const [session, setSession] = useState<CollaborativeSession | null>(null);
  const [participants, setParticipants] = useState<Participant[]>([]);
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [connected, setConnected] = useState(false);
  const [copied, setCopied] = useState(false);

  const wsRef = useRef<CollaborativeWebSocket | null>(null);
  const editorRef = useRef<any>(null);

  useEffect(() => {
    if (sessionId) {
      loadSession();
      connectWebSocket();
    }

    return () => {
      wsRef.current?.disconnect();
    };
  }, [sessionId]);

  async function loadSession() {
    try {
      setLoading(true);
      setError('');

      const [sessionData, participantsData] = await Promise.all([
        getCollaborativeSession(sessionId),
        getSessionParticipants(sessionId),
      ]);

      setSession(sessionData);
      setCode(sessionData.code_content);
      setParticipants(participantsData.filter((p) => p.is_active));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load session');
    } finally {
      setLoading(false);
    }
  }

  function connectWebSocket() {
    const token = localStorage.getItem('access_token') || '';

    wsRef.current = new CollaborativeWebSocket(sessionId, token, {
      onCodeUpdate: handleCodeUpdate,
      onConnectionChange: setConnected,
    });

    wsRef.current.connect();
  }

  function handleCodeUpdate(update: CodeUpdate) {
    if (update.type === 'code_update' && update.content !== undefined) {
      setCode(update.content);
      
      // Update editor content if it's from another user
      if (editorRef.current) {
        const currentValue = editorRef.current.getValue();
        if (currentValue !== update.content) {
          const position = editorRef.current.getPosition();
          editorRef.current.setValue(update.content);
          editorRef.current.setPosition(position);
        }
      }
    } else if (update.type === 'user_joined' || update.type === 'user_left') {
      loadSession(); // Reload to update participant list
    }
  }

  function handleEditorChange(value: string | undefined) {
    if (value !== undefined && value !== code) {
      setCode(value);
      wsRef.current?.sendCodeUpdate(value);
    }
  }

  function handleEditorMount(editor: any) {
    editorRef.current = editor;

    // Send cursor updates on position change
    editor.onDidChangeCursorPosition((e: any) => {
      const { lineNumber, column } = e.position;
      wsRef.current?.sendCursorUpdate(lineNumber, column);
    });
  }

  async function copyToClipboard() {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          <p className="mt-4 text-gray-400">Loading session...</p>
        </div>
      </div>
    );
  }

  if (error && !session) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-400 mb-4">{error}</p>
          <button
            onClick={() => router.back()}
            className="text-blue-400 hover:text-blue-300 font-medium"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  if (!session) return null;

  return (
    <div className="h-screen bg-gray-900 flex flex-col">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push('/dashboard/collaborative')}
              className="text-gray-400 hover:text-white transition-colors"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
            <div>
              <h1 className="text-xl font-semibold text-white">{session.title}</h1>
              <p className="text-sm text-gray-400">
                {getLanguageDisplayName(session.language)}
                {session.description && ` • ${session.description}`}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Connection Status */}
            <div className="flex items-center gap-2">
              {connected ? (
                <>
                  <Wifi className="h-4 w-4 text-green-400" />
                  <span className="text-sm text-green-400">Connected</span>
                </>
              ) : (
                <>
                  <WifiOff className="h-4 w-4 text-red-400" />
                  <span className="text-sm text-red-400">Disconnected</span>
                </>
              )}
            </div>

            {/* Participants */}
            <div className="flex items-center gap-2 bg-gray-700 px-3 py-2 rounded-lg">
              <Users className="h-4 w-4 text-gray-300" />
              <span className="text-sm text-white">{participants.length}</span>
            </div>

            {/* Copy Button */}
            <button
              onClick={copyToClipboard}
              className="flex items-center gap-2 bg-gray-700 hover:bg-gray-600 px-4 py-2 rounded-lg transition-colors text-sm text-white"
            >
              {copied ? (
                <>
                  <Check className="h-4 w-4" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="h-4 w-4" />
                  Copy Code
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Editor */}
      <div className="flex-1 overflow-hidden">
        <MonacoEditor
          height="100%"
          language={getMonacoLanguage(session.language)}
          value={code}
          onChange={handleEditorChange}
          onMount={handleEditorMount}
          theme="vs-dark"
          options={{
            fontSize: 14,
            minimap: { enabled: true },
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 2,
            wordWrap: 'on',
            lineNumbers: 'on',
            renderWhitespace: 'selection',
            cursorBlinking: 'smooth',
            cursorSmoothCaretAnimation: 'on',
            smoothScrolling: true,
          }}
        />
      </div>

      {/* Participants Sidebar (if needed) */}
      {participants.length > 1 && (
        <div className="absolute top-20 right-6 bg-gray-800 border border-gray-700 rounded-lg shadow-lg p-4 max-w-xs">
          <h3 className="text-sm font-semibold text-white mb-3">
            Active Participants ({participants.length})
          </h3>
          <div className="space-y-2">
            {participants.slice(0, 10).map((participant) => (
              <div
                key={participant.id}
                className="flex items-center gap-2 text-sm"
              >
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-gray-300">
                  User {participant.user_id.substring(0, 8)}
                </span>
              </div>
            ))}
            {participants.length > 10 && (
              <p className="text-xs text-gray-500">+{participants.length - 10} more</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
