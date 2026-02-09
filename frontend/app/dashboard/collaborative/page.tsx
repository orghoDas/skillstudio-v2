'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  getCollaborativeSessions,
  createCollaborativeSession,
  deleteCollaborativeSession,
  CollaborativeSession,
  CreateSession,
  getLanguageDisplayName,
  getDefaultCodeTemplate,
} from '@/lib/collaborative-service';
import { Code, Plus, Users, Clock, Trash2, ExternalLink, Globe, Lock } from 'lucide-react';

export default function CollaborativeSessionsPage() {
  const router = useRouter();
  const [sessions, setSessions] = useState<CollaborativeSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [creating, setCreating] = useState(false);
  const [filter, setFilter] = useState<'all' | 'my'>('all');

  const [formData, setFormData] = useState<CreateSession>({
    title: '',
    description: '',
    language: 'javascript',
    code_content: getDefaultCodeTemplate('javascript'),
    is_public: true,
  });

  useEffect(() => {
    loadSessions();
  }, [filter]);

  async function loadSessions() {
    try {
      setLoading(true);
      setError('');

      const data = await getCollaborativeSessions({
        my_sessions: filter === 'my',
        limit: 100,
      });

      setSessions(data.sessions);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load sessions');
    } finally {
      setLoading(false);
    }
  }

  async function handleCreate() {
    try {
      setCreating(true);
      setError('');

      const session = await createCollaborativeSession(formData);
      setShowCreateModal(false);
      
      // Reset form
      setFormData({
        title: '',
        description: '',
        language: 'javascript',
        code_content: getDefaultCodeTemplate('javascript'),
        is_public: true,
      });

      // Navigate to the new session
      router.push(`/dashboard/collaborative/${session.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create session');
    } finally {
      setCreating(false);
    }
  }

  async function handleDelete(sessionId: string) {
    if (!confirm('Are you sure you want to delete this session?')) return;

    try {
      await deleteCollaborativeSession(sessionId);
      await loadSessions();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete session');
    }
  }

  function handleLanguageChange(language: string) {
    setFormData({
      ...formData,
      language,
      code_content: getDefaultCodeTemplate(language),
    });
  }

  function formatDate(dateString: string) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  }

  const languages = [
    'javascript',
    'typescript',
    'python',
    'java',
    'cpp',
    'csharp',
    'go',
    'rust',
    'php',
    'ruby',
    'html',
    'css',
    'sql',
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Collaborative Code Editor
            </h1>
            <p className="text-gray-600">
              Create and join real-time collaborative coding sessions
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            <Plus className="h-5 w-5" />
            New Session
          </button>
        </div>

        {/* Filter Tabs */}
        <div className="mb-6 border-b border-gray-200">
          <nav className="flex space-x-8">
            <button
              onClick={() => setFilter('all')}
              className={`pb-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                filter === 'all'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              All Sessions
            </button>
            <button
              onClick={() => setFilter('my')}
              className={`pb-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                filter === 'my'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              My Sessions
            </button>
          </nav>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Loading State */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Loading sessions...</p>
          </div>
        ) : sessions.length === 0 ? (
          /* Empty State */
          <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
            <Code className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Sessions Found</h3>
            <p className="text-gray-500 mb-6">
              {filter === 'my'
                ? "You haven't created any sessions yet"
                : 'No collaborative sessions available'}
            </p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              <Plus className="h-5 w-5" />
              Create First Session
            </button>
          </div>
        ) : (
          /* Session Grid */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sessions.map((session) => (
              <div
                key={session.id}
                className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-all cursor-pointer"
                onClick={() => router.push(`/dashboard/collaborative/${session.id}`)}
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1 line-clamp-1">
                      {session.title}
                    </h3>
                    <div className="flex items-center gap-2">
                      <span className="inline-flex items-center gap-1 text-xs font-medium bg-blue-100 text-blue-700 px-2 py-1 rounded">
                        <Code className="h-3 w-3" />
                        {getLanguageDisplayName(session.language)}
                      </span>
                      {session.is_public ? (
                        <Globe className="h-4 w-4 text-green-600" />
                      ) : (
                        <Lock className="h-4 w-4 text-gray-600" />
                      )}
                    </div>
                  </div>
                </div>

                {/* Description */}
                {session.description && (
                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                    {session.description}
                  </p>
                )}

                {/* Stats */}
                <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
                  <div className="flex items-center gap-1">
                    <Users className="h-4 w-4" />
                    {session.current_participants}
                    {session.max_participants && `/${session.max_participants}`}
                  </div>
                  <div className="flex items-center gap-1">
                    <Clock className="h-4 w-4" />
                    {formatDate(session.created_at)}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      router.push(`/dashboard/collaborative/${session.id}`);
                    }}
                    className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium flex items-center justify-center gap-2"
                  >
                    <ExternalLink className="h-4 w-4" />
                    Open Editor
                  </button>
                  {filter === 'my' && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(session.id);
                      }}
                      className="text-red-600 hover:text-red-700 px-3 py-2"
                      title="Delete Session"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Create Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                Create Collaborative Session
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Session Title *
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., Algorithm Practice Session"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={3}
                    placeholder="Optional session description"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Programming Language *
                  </label>
                  <select
                    value={formData.language}
                    onChange={(e) => handleLanguageChange(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    {languages.map((lang) => (
                      <option key={lang} value={lang}>
                        {getLanguageDisplayName(lang)}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Max Participants
                  </label>
                  <input
                    type="number"
                    value={formData.max_participants || ''}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        max_participants: e.target.value ? parseInt(e.target.value) : undefined,
                      })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Leave empty for unlimited"
                    min="2"
                  />
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="is_public"
                    checked={formData.is_public}
                    onChange={(e) => setFormData({ ...formData, is_public: e.target.checked })}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="is_public" className="text-sm text-gray-700">
                    Public session (anyone can join)
                  </label>
                </div>
              </div>

              {error && (
                <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm">
                  {error}
                </div>
              )}

              <div className="mt-6 flex gap-3">
                <button
                  onClick={handleCreate}
                  disabled={creating || !formData.title || !formData.language}
                  className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {creating ? 'Creating...' : 'Create Session'}
                </button>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
