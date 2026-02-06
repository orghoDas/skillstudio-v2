'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import {
  ArrowLeft,
  Save,
  Eye,
  FileText,
  Play,
  Code,
  Brain,
  X,
  Plus,
} from 'lucide-react';
import { instructorCourseService, Lesson, LessonCreate } from '@/lib/instructor-course-service';

export default function LessonEditorPage() {
  const params = useParams();
  const router = useRouter();
  const moduleId = params.moduleId as string;
  const lessonId = params.lessonId as string;

  const [isEdit, setIsEdit] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  const [formData, setFormData] = useState<Partial<LessonCreate>>({
    title: '',
    content_type: 'article',
    content_body: '',
    content_url: '',
    content_metadata: {},
    estimated_minutes: 0,
    difficulty_score: 5,
    prerequisites: [],
    skill_tags: [],
    learning_objectives: [],
    sequence_order: 1,
  });

  const [skillInput, setSkillInput] = useState('');
  const [objectiveInput, setObjectiveInput] = useState('');

  useEffect(() => {
    if (lessonId && lessonId !== 'new') {
      setIsEdit(true);
      fetchLesson();
    } else {
      setLoading(false);
      determineNextSequence();
    }
  }, [lessonId]);

  const determineNextSequence = async () => {
    try {
      const lessons = await instructorCourseService.getLessons(moduleId);
      setFormData((prev) => ({
        ...prev,
        sequence_order: lessons.length + 1,
      }));
    } catch (error) {
      console.error('Failed to determine sequence:', error);
    }
  };

  const fetchLesson = async () => {
    try {
      setLoading(true);
      // Note: Need to implement getLesson in service
      // For now, we'll get all lessons and find the one we want
      const lessons = await instructorCourseService.getLessons(moduleId);
      const lesson = lessons.find((l) => l.id === lessonId);
      if (lesson) {
        setFormData({
          title: lesson.title,
          content_type: lesson.content_type,
          content_body: lesson.content_body || '',
          content_url: lesson.content_url || '',
          content_metadata: lesson.content_metadata || {},
          estimated_minutes: lesson.estimated_minutes || 0,
          difficulty_score: lesson.difficulty_score || 5,
          prerequisites: lesson.prerequisites || [],
          skill_tags: lesson.skill_tags || [],
          learning_objectives: lesson.learning_objectives || [],
          sequence_order: lesson.sequence_order,
        });
      }
    } catch (error) {
      console.error('Failed to fetch lesson:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      if (isEdit) {
        await instructorCourseService.updateLesson(lessonId, formData);
        alert('Lesson updated successfully!');
      } else {
        await instructorCourseService.createLesson(moduleId, formData as LessonCreate);
        alert('Lesson created successfully!');
        router.back();
      }
    } catch (error) {
      console.error('Failed to save lesson:', error);
      alert('Failed to save lesson');
    } finally {
      setSaving(false);
    }
  };

  const addSkill = () => {
    if (skillInput.trim() && !formData.skill_tags?.includes(skillInput.trim())) {
      setFormData({
        ...formData,
        skill_tags: [...(formData.skill_tags || []), skillInput.trim()],
      });
      setSkillInput('');
    }
  };

  const removeSkill = (skill: string) => {
    setFormData({
      ...formData,
      skill_tags: formData.skill_tags?.filter((s) => s !== skill),
    });
  };

  const addObjective = () => {
    if (objectiveInput.trim() && !formData.learning_objectives?.includes(objectiveInput.trim())) {
      setFormData({
        ...formData,
        learning_objectives: [...(formData.learning_objectives || []), objectiveInput.trim()],
      });
      setObjectiveInput('');
    }
  };

  const removeObjective = (objective: string) => {
    setFormData({
      ...formData,
      learning_objectives: formData.learning_objectives?.filter((o) => o !== objective),
    });
  };

  const contentTypes = [
    { value: 'article', label: 'Article', icon: FileText },
    { value: 'video', label: 'Video', icon: Play },
    { value: 'quiz', label: 'Quiz', icon: Brain },
    { value: 'code_exercise', label: 'Code Exercise', icon: Code },
  ];

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="mb-8">
        <Link
          href="#"
          onClick={() => router.back()}
          className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back
        </Link>
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900">
            {isEdit ? 'Edit Lesson' : 'Create New Lesson'}
          </h1>
          <div className="flex gap-3">
            <button
              onClick={() => setShowPreview(!showPreview)}
              className="btn-secondary flex items-center gap-2"
            >
              <Eye className="w-5 h-5" />
              {showPreview ? 'Edit' : 'Preview'}
            </button>
            <button
              onClick={handleSave}
              disabled={saving || !formData.title}
              className="btn-primary flex items-center gap-2"
            >
              <Save className="w-5 h-5" />
              {saving ? 'Saving...' : 'Save Lesson'}
            </button>
          </div>
        </div>
      </div>

      {showPreview ? (
        /* Preview Mode */
        <div className="bg-white rounded-lg border border-gray-200 p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">{formData.title}</h2>
          
          {formData.learning_objectives && formData.learning_objectives.length > 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <h3 className="font-semibold text-blue-900 mb-2">Learning Objectives</h3>
              <ul className="space-y-1">
                {formData.learning_objectives.map((objective, idx) => (
                  <li key={idx} className="text-blue-800 text-sm">
                    • {objective}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {formData.content_type === 'video' && formData.content_url && (
            <div className="mb-6">
              <div className="aspect-video bg-gray-900 rounded-lg overflow-hidden">
                <iframe
                  src={formData.content_url}
                  className="w-full h-full"
                  allowFullScreen
                />
              </div>
            </div>
          )}

          {formData.content_body && (
            <div
              className="prose max-w-none"
              dangerouslySetInnerHTML={{ __html: formData.content_body }}
            />
          )}

          {formData.skill_tags && formData.skill_tags.length > 0 && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <h4 className="text-sm font-semibold text-gray-700 mb-2">Skills Covered:</h4>
              <div className="flex flex-wrap gap-2">
                {formData.skill_tags.map((tag) => (
                  <span key={tag} className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        /* Edit Mode */
        <div className="space-y-6">
          {/* Basic Info */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Basic Information</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Lesson Title *
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="input"
                  placeholder="e.g., Introduction to Variables"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Content Type *
                </label>
                <div className="grid grid-cols-4 gap-3">
                  {contentTypes.map((type) => {
                    const Icon = type.icon;
                    return (
                      <button
                        key={type.value}
                        type="button"
                        onClick={() => setFormData({ ...formData, content_type: type.value as any })}
                        className={`p-4 border-2 rounded-lg transition-all ${
                          formData.content_type === type.value
                            ? 'border-primary-600 bg-primary-50 text-primary-700'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <Icon className="w-6 h-6 mx-auto mb-2" />
                        <div className="text-sm font-medium">{type.label}</div>
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Estimated Minutes
                  </label>
                  <input
                    type="number"
                    value={formData.estimated_minutes || ''}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        estimated_minutes: parseInt(e.target.value) || 0,
                      })
                    }
                    className="input"
                    min="0"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Difficulty (1-10)
                  </label>
                  <input
                    type="number"
                    value={formData.difficulty_score || ''}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        difficulty_score: parseInt(e.target.value) || 5,
                      })
                    }
                    className="input"
                    min="1"
                    max="10"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Sequence Order
                  </label>
                  <input
                    type="number"
                    value={formData.sequence_order || ''}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        sequence_order: parseInt(e.target.value) || 1,
                      })
                    }
                    className="input"
                    min="1"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Lesson Content</h2>

            {formData.content_type === 'video' && (
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Video URL (YouTube, Vimeo, or direct link)
                </label>
                <input
                  type="url"
                  value={formData.content_url || ''}
                  onChange={(e) => setFormData({ ...formData, content_url: e.target.value })}
                  className="input"
                  placeholder="https://www.youtube.com/watch?v=..."
                />
                <p className="text-sm text-gray-500 mt-1">
                  For YouTube, paste the full watch URL. It will be embedded automatically.
                </p>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Content Body
                {formData.content_type === 'article' && ' *'}
              </label>
              <textarea
                value={formData.content_body || ''}
                onChange={(e) => setFormData({ ...formData, content_body: e.target.value })}
                className="input min-h-[300px] font-mono text-sm"
                placeholder="Write your lesson content here. You can use HTML for formatting..."
              />
              <p className="text-sm text-gray-500 mt-1">
                Tip: You can use basic HTML tags like &lt;h2&gt;, &lt;p&gt;, &lt;ul&gt;, &lt;strong&gt;, etc.
              </p>
            </div>
          </div>

          {/* Learning Objectives */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Learning Objectives</h2>
            
            <div className="space-y-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={objectiveInput}
                  onChange={(e) => setObjectiveInput(e.target.value)}
                  onKeyPress={(e) =>
                    e.key === 'Enter' && (e.preventDefault(), addObjective())
                  }
                  className="input flex-1"
                  placeholder="Add a learning objective"
                />
                <button type="button" onClick={addObjective} className="btn-secondary">
                  Add
                </button>
              </div>

              {formData.learning_objectives && formData.learning_objectives.length > 0 && (
                <ul className="space-y-2">
                  {formData.learning_objectives.map((objective, idx) => (
                    <li
                      key={idx}
                      className="flex items-start gap-2 p-3 bg-gray-50 rounded-lg"
                    >
                      <span className="flex-1 text-gray-900">{objective}</span>
                      <button
                        type="button"
                        onClick={() => removeObjective(objective)}
                        className="text-gray-400 hover:text-red-600"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {/* Skills Covered */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Skills Covered</h2>
            
            <div className="space-y-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={skillInput}
                  onChange={(e) => setSkillInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
                  className="input flex-1"
                  placeholder="Add a skill tag"
                />
                <button type="button" onClick={addSkill} className="btn-secondary">
                  Add
                </button>
              </div>

              {formData.skill_tags && formData.skill_tags.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {formData.skill_tags.map((skill) => (
                    <span
                      key={skill}
                      className="inline-flex items-center gap-1 px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm"
                    >
                      {skill}
                      <button
                        type="button"
                        onClick={() => removeSkill(skill)}
                        className="hover:text-primary-900"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
