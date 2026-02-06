'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  MessageSquare,
  Plus,
  ThumbsUp,
  Eye,
  MessageCircle,
  Pin,
  CheckCircle,
  Lock,
  ArrowLeft,
  Send,
} from 'lucide-react';
import { socialService, Discussion, DiscussionReply } from '@/lib/social-service';

export default function CourseDiscussionsPage() {
  const params = useParams();
  const router = useRouter();
  const courseId = params.courseId as string;

  const [discussions, setDiscussions] = useState<Discussion[]>([]);
  const [selectedDiscussion, setSelectedDiscussion] = useState<Discussion | null>(null);
  const [replies, setReplies] = useState<DiscussionReply[]>([]);
  const [loading, setLoading] = useState(true);
  const [showNewThread, setShowNewThread] = useState(false);

  const [newThread, setNewThread] = useState({
    title: '',
    content: '',
    category: 'general' as const,
    tags: [] as string[],
  });

  const [replyContent, setReplyContent] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchDiscussions();
  }, [courseId]);

  const fetchDiscussions = async () => {
    try {
      setLoading(true);
      const data = await socialService.getCourseDiscussions(courseId);
      setDiscussions(data);
    } catch (error) {
      console.error('Failed to fetch discussions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateThread = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      await socialService.createDiscussion(courseId, newThread);
      setShowNewThread(false);
      setNewThread({ title: '', content: '', category: 'general', tags: [] });
      await fetchDiscussions();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to create discussion');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSelectDiscussion = async (discussion: Discussion) => {
    setSelectedDiscussion(discussion);
    try {
      const fullDiscussion = await socialService.getDiscussion(discussion.id);
      setSelectedDiscussion(fullDiscussion);
      const repliesData = await socialService.getReplies(discussion.id);
      setReplies(repliesData);
    } catch (error) {
      console.error('Failed to load discussion:', error);
    }
  };

  const handleSubmitReply = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDiscussion || !replyContent.trim()) return;

    try {
      setSubmitting(true);
      await socialService.createReply(selectedDiscussion.id, { content: replyContent });
      setReplyContent('');
      const repliesData = await socialService.getReplies(selectedDiscussion.id);
      setReplies(repliesData);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to submit reply');
    } finally {
      setSubmitting(false);
    }
  };

  const handleUpvote = async (discussionId: string) => {
    try {
      await socialService.upvoteDiscussion(discussionId);
      await fetchDiscussions();
      if (selectedDiscussion) {
        const updated = await socialService.getDiscussion(discussionId);
        setSelectedDiscussion(updated);
      }
    } catch (error) {
      console.error('Failed to upvote:', error);
    }
  };

  const categoryColors: Record<string, string> = {
    general: 'bg-gray-100 text-gray-700',
    lesson_specific: 'bg-blue-100 text-blue-700',
    technical: 'bg-red-100 text-red-700',
    career: 'bg-green-100 text-green-700',
    projects: 'bg-purple-100 text-purple-700',
    announcements: 'bg-yellow-100 text-yellow-700',
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      {!selectedDiscussion ? (
        <>
          {/* Discussions List */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Course Discussions</h1>
                <p className="text-gray-600 mt-2">
                  Connect with other learners and instructors
                </p>
              </div>
              <button
                onClick={() => setShowNewThread(true)}
                className="btn-primary flex items-center gap-2"
              >
                <Plus className="w-5 h-5" />
                New Discussion
              </button>
            </div>

            {/* New Thread Form */}
            {showNewThread && (
              <form onSubmit={handleCreateThread} className="card mb-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Start a New Discussion
                </h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Title *
                    </label>
                    <input
                      type="text"
                      value={newThread.title}
                      onChange={(e) =>
                        setNewThread({ ...newThread, title: e.target.value })
                      }
                      className="input"
                      required
                      placeholder="What's your question or topic?"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Category
                    </label>
                    <select
                      value={newThread.category}
                      onChange={(e) =>
                        setNewThread({ ...newThread, category: e.target.value as any })
                      }
                      className="input"
                    >
                      <option value="general">General</option>
                      <option value="lesson_specific">Lesson Specific</option>
                      <option value="technical">Technical</option>
                      <option value="career">Career</option>
                      <option value="projects">Projects</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Content *
                    </label>
                    <textarea
                      value={newThread.content}
                      onChange={(e) =>
                        setNewThread({ ...newThread, content: e.target.value })
                      }
                      className="input min-h-[120px]"
                      required
                      placeholder="Provide details about your question or topic..."
                      rows={5}
                    />
                  </div>

                  <div className="flex gap-3">
                    <button type="submit" disabled={submitting} className="btn-primary">
                      {submitting ? 'Creating...' : 'Create Discussion'}
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowNewThread(false)}
                      className="btn-secondary"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </form>
            )}

            {/* Discussions List */}
            <div className="space-y-3">
              {discussions.length === 0 ? (
                <div className="card text-center py-12 text-gray-500">
                  No discussions yet. Start the conversation!
                </div>
              ) : (
                discussions.map((discussion) => (
                  <button
                    key={discussion.id}
                    onClick={() => handleSelectDiscussion(discussion)}
                    className="card w-full text-left hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start gap-4">
                      <div className="flex flex-col items-center gap-1">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleUpvote(discussion.id);
                          }}
                          className="p-1 hover:bg-gray-100 rounded"
                        >
                          <ThumbsUp className="w-4 h-4 text-gray-600" />
                        </button>
                        <span className="text-sm font-semibold text-gray-900">
                          {discussion.upvotes}
                        </span>
                      </div>

                      <div className="flex-1">
                        <div className="flex items-start gap-2 mb-2">
                          {discussion.is_pinned && (
                            <Pin className="w-4 h-4 text-primary-600" />
                          )}
                          {discussion.is_resolved && (
                            <CheckCircle className="w-4 h-4 text-green-600" />
                          )}
                          {discussion.is_locked && (
                            <Lock className="w-4 h-4 text-gray-600" />
                          )}
                          <h3 className="font-semibold text-gray-900 flex-1">
                            {discussion.title}
                          </h3>
                          <span
                            className={`px-2 py-1 rounded text-xs ${
                              categoryColors[discussion.category]
                            }`}
                          >
                            {discussion.category.replace('_', ' ')}
                          </span>
                        </div>

                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <span className="flex items-center gap-1">
                            <Eye className="w-4 h-4" />
                            {discussion.views_count} views
                          </span>
                          <span className="flex items-center gap-1">
                            <MessageCircle className="w-4 h-4" />
                            {discussion.reply_count} replies
                          </span>
                          <span>
                            {new Date(discussion.last_activity_at).toLocaleDateString()}
                          </span>
                        </div>

                        {discussion.tags && discussion.tags.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2">
                            {discussion.tags.map((tag, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs"
                              >
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>
        </>
      ) : (
        <>
          {/* Discussion Thread View */}
          <div className="mb-6">
            <button
              onClick={() => setSelectedDiscussion(null)}
              className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Discussions
            </button>

            <div className="card">
              <div className="flex items-start gap-4 mb-4">
                <div className="flex flex-col items-center gap-1">
                  <button
                    onClick={() => handleUpvote(selectedDiscussion.id)}
                    className="p-2 hover:bg-gray-100 rounded"
                  >
                    <ThumbsUp className="w-5 h-5 text-gray-600" />
                  </button>
                  <span className="text-lg font-semibold text-gray-900">
                    {selectedDiscussion.upvotes}
                  </span>
                </div>

                <div className="flex-1">
                  <div className="flex items-start gap-2 mb-2">
                    {selectedDiscussion.is_pinned && (
                      <Pin className="w-5 h-5 text-primary-600" />
                    )}
                    {selectedDiscussion.is_resolved && (
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    )}
                    <h1 className="text-2xl font-bold text-gray-900 flex-1">
                      {selectedDiscussion.title}
                    </h1>
                    <span
                      className={`px-3 py-1 rounded text-sm ${
                        categoryColors[selectedDiscussion.category]
                      }`}
                    >
                      {selectedDiscussion.category.replace('_', ' ')}
                    </span>
                  </div>

                  <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
                    <span className="flex items-center gap-1">
                      <Eye className="w-4 h-4" />
                      {selectedDiscussion.views_count} views
                    </span>
                    <span>
                      {new Date(selectedDiscussion.created_at).toLocaleDateString()}
                    </span>
                  </div>

                  <p className="text-gray-700 whitespace-pre-wrap">
                    {selectedDiscussion.content}
                  </p>

                  {selectedDiscussion.tags && selectedDiscussion.tags.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-4">
                      {selectedDiscussion.tags.map((tag, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-sm"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Replies */}
          <div className="space-y-4 mb-6">
            <h2 className="text-xl font-semibold text-gray-900">
              {replies.length} {replies.length === 1 ? 'Reply' : 'Replies'}
            </h2>

            {replies.map((reply) => (
              <div key={reply.id} className="card">
                <div className="flex items-start gap-3">
                  <div className="flex flex-col items-center gap-1">
                    <ThumbsUp className="w-4 h-4 text-gray-400" />
                    <span className="text-sm text-gray-600">{reply.upvotes}</span>
                  </div>

                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      {reply.is_instructor_response && (
                        <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs font-semibold">
                          Instructor
                        </span>
                      )}
                      {reply.is_accepted_answer && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs font-semibold">
                          <CheckCircle className="w-3 h-3" />
                          Accepted Answer
                        </span>
                      )}
                      <span className="text-sm text-gray-600">
                        {new Date(reply.created_at).toLocaleDateString()}
                      </span>
                      {reply.is_edited && (
                        <span className="text-xs text-gray-500">(edited)</span>
                      )}
                    </div>
                    <p className="text-gray-700 whitespace-pre-wrap">{reply.content}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Reply Form */}
          {!selectedDiscussion.is_locked && (
            <form onSubmit={handleSubmitReply} className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Your Reply</h3>
              <textarea
                value={replyContent}
                onChange={(e) => setReplyContent(e.target.value)}
                className="input min-h-[120px] mb-3"
                placeholder="Share your thoughts..."
                rows={5}
                required
              />
              <button
                type="submit"
                disabled={submitting || !replyContent.trim()}
                className="btn-primary flex items-center gap-2"
              >
                <Send className="w-4 h-4" />
                {submitting ? 'Submitting...' : 'Submit Reply'}
              </button>
            </form>
          )}
        </>
      )}
    </div>
  );
}
