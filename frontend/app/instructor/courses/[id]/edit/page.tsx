'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import {
  ArrowLeft,
  Save,
  X,
  Plus,
  Trash2,
  Edit2,
  GripVertical,
  ChevronDown,
  ChevronRight,
  Eye,
  EyeOff,
} from 'lucide-react';
import {
  instructorCourseService,
  Course,
  Module,
  Lesson,
  CourseUpdate,
  ModuleCreate,
  LessonCreate,
} from '@/lib/instructor-course-service';

export default function EditCoursePage() {
  const router = useRouter();
  const params = useParams();
  const courseId = params.id as string;

  const [course, setCourse] = useState<Course | null>(null);
  const [modules, setModules] = useState<Module[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  // Form states
  const [formData, setFormData] = useState<CourseUpdate>({});
  const [skillInput, setSkillInput] = useState('');
  const [prerequisiteInput, setPrerequisiteInput] = useState('');

  // Module/Lesson management states
  const [expandedModules, setExpandedModules] = useState<Set<string>>(new Set());
  const [moduleLessons, setModuleLessons] = useState<Record<string, Lesson[]>>({});
  const [showModuleForm, setShowModuleForm] = useState(false);
  const [editingModule, setEditingModule] = useState<Module | null>(null);

  useEffect(() => {
    fetchCourseData();
  }, [courseId]);

  const fetchCourseData = async () => {
    try {
      setLoading(true);
      const [courseData, modulesData] = await Promise.all([
        instructorCourseService.getCourse(courseId),
        instructorCourseService.getModules(courseId),
      ]);
      setCourse(courseData);
      setModules(modulesData);
      setFormData({
        title: courseData.title,
        description: courseData.description,
        short_description: courseData.short_description,
        difficulty_level: courseData.difficulty_level,
        estimated_duration_hours: courseData.estimated_duration_hours,
        skills_taught: courseData.skills_taught,
        prerequisites: courseData.prerequisites,
        thumbnail_url: courseData.thumbnail_url,
        is_published: courseData.is_published,
      });
    } catch (err) {
      setError('Failed to load course data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveCourse = async () => {
    try {
      setSaving(true);
      setError('');
      await instructorCourseService.updateCourse(courseId, formData);
      alert('Course updated successfully!');
      await fetchCourseData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update course');
    } finally {
      setSaving(false);
    }
  };

  const togglePublish = async () => {
    try {
      if (course?.is_published) {
        await instructorCourseService.unpublishCourse(courseId);
      } else {
        await instructorCourseService.publishCourse(courseId);
      }
      await fetchCourseData();
    } catch (err) {
      alert('Failed to toggle publish status');
    }
  };

  const addSkill = () => {
    if (skillInput.trim() && !formData.skills_taught?.includes(skillInput.trim())) {
      setFormData({
        ...formData,
        skills_taught: [...(formData.skills_taught || []), skillInput.trim()],
      });
      setSkillInput('');
    }
  };

  const removeSkill = (skill: string) => {
    setFormData({
      ...formData,
      skills_taught: formData.skills_taught?.filter((s) => s !== skill),
    });
  };

  const addPrerequisite = () => {
    if (prerequisiteInput.trim() && !formData.prerequisites?.includes(prerequisiteInput.trim())) {
      setFormData({
        ...formData,
        prerequisites: [...(formData.prerequisites || []), prerequisiteInput.trim()],
      });
      setPrerequisiteInput('');
    }
  };

  const removePrerequisite = (prerequisite: string) => {
    setFormData({
      ...formData,
      prerequisites: formData.prerequisites?.filter((p) => p !== prerequisite),
    });
  };

  const toggleModuleExpand = async (moduleId: string) => {
    const newExpanded = new Set(expandedModules);
    if (newExpanded.has(moduleId)) {
      newExpanded.delete(moduleId);
    } else {
      newExpanded.add(moduleId);
      // Fetch lessons if not already loaded
      if (!moduleLessons[moduleId]) {
        try {
          const lessons = await instructorCourseService.getLessons(moduleId);
          setModuleLessons((prev) => ({ ...prev, [moduleId]: lessons }));
        } catch (err) {
          console.error('Failed to fetch lessons:', err);
        }
      }
    }
    setExpandedModules(newExpanded);
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!course) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Course not found</p>
        <Link href="/instructor/courses" className="btn-primary mt-4">
          Back to Courses
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <Link
          href="/instructor/courses"
          className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Courses
        </Link>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{course.title}</h1>
            <p className="text-gray-600 mt-1">Edit course details and content</p>
          </div>
          <div className="flex gap-2">
            <button onClick={togglePublish} className="btn-secondary flex items-center gap-2">
              {course.is_published ? (
                <>
                  <EyeOff className="w-5 h-5" />
                  Unpublish
                </>
              ) : (
                <>
                  <Eye className="w-5 h-5" />
                  Publish
                </>
              )}
            </button>
            <button
              onClick={handleSaveCourse}
              disabled={saving}
              className="btn-primary flex items-center gap-2"
            >
              <Save className="w-5 h-5" />
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Course Details Form */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Information */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Basic Information
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Course Title *
                </label>
                <input
                  type="text"
                  value={formData.title || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, title: e.target.value })
                  }
                  className="input"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Short Description
                </label>
                <input
                  type="text"
                  value={formData.short_description || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, short_description: e.target.value })
                  }
                  className="input"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Full Description
                </label>
                <textarea
                  value={formData.description || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                  className="input min-h-[120px]"
                  rows={5}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Difficulty Level
                  </label>
                  <select
                    value={formData.difficulty_level || 'beginner'}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        difficulty_level: e.target.value as any,
                      })
                    }
                    className="input"
                  >
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Duration (hours)
                  </label>
                  <input
                    type="number"
                    value={formData.estimated_duration_hours || 0}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        estimated_duration_hours: parseInt(e.target.value) || 0,
                      })
                    }
                    className="input"
                    min="0"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Thumbnail URL
                </label>
                <input
                  type="url"
                  value={formData.thumbnail_url || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, thumbnail_url: e.target.value })
                  }
                  className="input"
                />
              </div>
            </div>
          </div>

          {/* Skills */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Skills Taught
            </h2>
            <div className="space-y-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={skillInput}
                  onChange={(e) => setSkillInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
                  className="input flex-1"
                  placeholder="Add a skill"
                />
                <button type="button" onClick={addSkill} className="btn-secondary">
                  Add
                </button>
              </div>
              {formData.skills_taught && formData.skills_taught.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {formData.skills_taught.map((skill) => (
                    <span
                      key={skill}
                      className="inline-flex items-center gap-1 px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm"
                    >
                      {skill}
                      <button type="button" onClick={() => removeSkill(skill)}>
                        <X className="w-4 h-4" />
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Prerequisites */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Prerequisites
            </h2>
            <div className="space-y-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={prerequisiteInput}
                  onChange={(e) => setPrerequisiteInput(e.target.value)}
                  onKeyPress={(e) =>
                    e.key === 'Enter' && (e.preventDefault(), addPrerequisite())
                  }
                  className="input flex-1"
                  placeholder="Add a prerequisite"
                />
                <button
                  type="button"
                  onClick={addPrerequisite}
                  className="btn-secondary"
                >
                  Add
                </button>
              </div>
              {formData.prerequisites && formData.prerequisites.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {formData.prerequisites.map((prerequisite) => (
                    <span
                      key={prerequisite}
                      className="inline-flex items-center gap-1 px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                    >
                      {prerequisite}
                      <button
                        type="button"
                        onClick={() => removePrerequisite(prerequisite)}
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

        {/* Course Structure Sidebar */}
        <div className="lg:col-span-1">
          <div className="card sticky top-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">
                Course Content
              </h2>
              <button
                onClick={() => setShowModuleForm(true)}
                className="btn-secondary text-sm flex items-center gap-1"
              >
                <Plus className="w-4 h-4" />
                Module
              </button>
            </div>

            {modules.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p className="mb-4">No modules yet</p>
                <button
                  onClick={() => setShowModuleForm(true)}
                  className="btn-primary text-sm"
                >
                  Add First Module
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                {modules.map((module) => (
                  <ModuleItem
                    key={module.id}
                    module={module}
                    courseId={courseId}
                    isExpanded={expandedModules.has(module.id)}
                    lessons={moduleLessons[module.id]}
                    onToggle={() => toggleModuleExpand(module.id)}
                    onEdit={() => setEditingModule(module)}
                    onDelete={async () => {
                      if (confirm('Delete this module?')) {
                        await instructorCourseService.deleteModule(module.id);
                        await fetchCourseData();
                      }
                    }}
                    onLessonDelete={async (lessonId: string) => {
                      if (confirm('Delete this lesson?')) {
                        await instructorCourseService.deleteLesson(lessonId);
                        // Refresh lessons for this module
                        const lessons = await instructorCourseService.getLessons(module.id);
                        setModuleLessons((prev) => ({ ...prev, [module.id]: lessons }));
                      }
                    }}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Module Form Modal */}
      {showModuleForm && (
        <ModuleFormModal
          courseId={courseId}
          onClose={() => setShowModuleForm(false)}
          onSuccess={() => {
            setShowModuleForm(false);
            fetchCourseData();
          }}
          nextSequence={modules.length + 1}
        />
      )}
    </div>
  );
}

function ModuleItem({
  module,
  courseId,
  isExpanded,
  lessons = [],
  onToggle,
  onEdit,
  onDelete,
  onLessonDelete,
}: {
  module: Module;
  courseId: string;
  isExpanded: boolean;
  lessons?: Lesson[];
  onToggle: () => void;
  onEdit: () => void;
  onDelete: () => void;
  onLessonDelete: (lessonId: string) => void;
}) {
  const router = useRouter();

  return (
    <div className="border border-gray-200 rounded-lg">
      <div className="flex items-center gap-2 p-3">
        <button onClick={onToggle} className="text-gray-400 hover:text-gray-600">
          {isExpanded ? (
            <ChevronDown className="w-4 h-4" />
          ) : (
            <ChevronRight className="w-4 h-4" />
          )}
        </button>
        <div className="flex-1 min-w-0">
          <p className="font-medium text-sm text-gray-900 truncate">
            {module.sequence_order}. {module.title}
          </p>
          {lessons && lessons.length > 0 && (
            <p className="text-xs text-gray-500">{lessons.length} lessons</p>
          )}
        </div>
        <button
          onClick={onEdit}
          className="text-gray-400 hover:text-gray-600"
        >
          <Edit2 className="w-3 h-3" />
        </button>
        <button onClick={onDelete} className="text-gray-400 hover:text-red-600">
          <Trash2 className="w-3 h-3" />
        </button>
      </div>

      {isExpanded && (
        <div className="border-t border-gray-200 bg-gray-50 p-3 space-y-2">
          {lessons && lessons.length > 0 ? (
            lessons.map((lesson) => (
              <div
                key={lesson.id}
                className="flex items-center gap-2 p-2 bg-white rounded border border-gray-200 hover:border-primary-300 transition-colors"
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-900 truncate">{lesson.title}</p>
                  <p className="text-xs text-gray-500">
                    {lesson.content_type} • {lesson.estimated_minutes || 0} min
                  </p>
                </div>
                <Link
                  href={`/instructor/courses/${courseId}/modules/${module.id}/lessons/${lesson.id}/edit`}
                  className="text-primary-600 hover:text-primary-700"
                >
                  <Edit2 className="w-3 h-3" />
                </Link>
                <button
                  onClick={() => onLessonDelete(lesson.id)}
                  className="text-gray-400 hover:text-red-600"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            ))
          ) : (
            <p className="text-sm text-gray-500 text-center py-2">No lessons yet</p>
          )}
          <Link
            href={`/instructor/courses/${courseId}/modules/${module.id}/lessons/new/edit`}
            className="btn-secondary w-full text-sm flex items-center justify-center gap-1"
          >
            <Plus className="w-4 h-4" />
            Add Lesson
          </Link>
        </div>
      )}
    </div>
  );
}

function ModuleFormModal({
  courseId,
  onClose,
  onSuccess,
  nextSequence,
}: {
  courseId: string;
  onClose: () => void;
  onSuccess: () => void;
  nextSequence: number;
}) {
  const [formData, setFormData] = useState<ModuleCreate>({
    title: '',
    description: '',
    sequence_order: nextSequence,
    est_duration_minutes: 0,
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      await instructorCourseService.createModule(courseId, formData);
      onSuccess();
    } catch (err) {
      alert('Failed to create module');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-md w-full p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold">Add Module</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Module Title *
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="input"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              className="input"
              rows={3}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Sequence Order
              </label>
              <input
                type="number"
                value={formData.sequence_order}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    sequence_order: parseInt(e.target.value),
                  })
                }
                className="input"
                min="1"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Duration (min)
              </label>
              <input
                type="number"
                value={formData.est_duration_minutes || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    est_duration_minutes: parseInt(e.target.value) || 0,
                  })
                }
                className="input"
                min="0"
              />
            </div>
          </div>

          <div className="flex gap-2 pt-4">
            <button
              type="submit"
              disabled={loading}
              className="btn-primary flex-1"
            >
              {loading ? 'Creating...' : 'Create Module'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
