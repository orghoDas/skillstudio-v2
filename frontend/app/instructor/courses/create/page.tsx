'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Save, X } from 'lucide-react';
import { instructorCourseService, CourseCreate } from '@/lib/instructor-course-service';

export default function CreateCoursePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState<CourseCreate>({
    title: '',
    description: '',
    short_description: '',
    difficulty_level: 'beginner',
    estimated_duration_hours: 0,
    skills_taught: [],
    prerequisites: [],
    thumbnail_url: '',
  });

  const [skillInput, setSkillInput] = useState('');
  const [prerequisiteInput, setPrerequisiteInput] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const course = await instructorCourseService.createCourse(formData);
      router.push(`/instructor/courses/${course.id}/edit`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create course');
    } finally {
      setLoading(false);
    }
  };

  const addSkill = () => {
    if (skillInput.trim() && !formData.skills_taught.includes(skillInput.trim())) {
      setFormData({
        ...formData,
        skills_taught: [...formData.skills_taught, skillInput.trim()],
      });
      setSkillInput('');
    }
  };

  const removeSkill = (skill: string) => {
    setFormData({
      ...formData,
      skills_taught: formData.skills_taught.filter((s) => s !== skill),
    });
  };

  const addPrerequisite = () => {
    if (prerequisiteInput.trim() && !formData.prerequisites.includes(prerequisiteInput.trim())) {
      setFormData({
        ...formData,
        prerequisites: [...formData.prerequisites, prerequisiteInput.trim()],
      });
      setPrerequisiteInput('');
    }
  };

  const removePrerequisite = (prerequisite: string) => {
    setFormData({
      ...formData,
      prerequisites: formData.prerequisites.filter((p) => p !== prerequisite),
    });
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <Link
          href="/instructor/courses"
          className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Courses
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">Create New Course</h1>
        <p className="text-gray-600 mt-1">
          Fill in the details to create your course
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

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
                value={formData.title}
                onChange={(e) =>
                  setFormData({ ...formData, title: e.target.value })
                }
                className="input"
                placeholder="e.g., Introduction to Python Programming"
                required
                minLength={3}
                maxLength={200}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Short Description
              </label>
              <input
                type="text"
                value={formData.short_description}
                onChange={(e) =>
                  setFormData({ ...formData, short_description: e.target.value })
                }
                className="input"
                placeholder="A brief one-liner about your course"
                maxLength={500}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Full Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                className="input min-h-[120px]"
                placeholder="Provide a detailed description of what students will learn..."
                rows={5}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Difficulty Level *
                </label>
                <select
                  value={formData.difficulty_level}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      difficulty_level: e.target.value as any,
                    })
                  }
                  className="input"
                  required
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Estimated Duration (hours)
                </label>
                <input
                  type="number"
                  value={formData.estimated_duration_hours || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      estimated_duration_hours: parseInt(e.target.value) || 0,
                    })
                  }
                  className="input"
                  placeholder="e.g., 10"
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
                value={formData.thumbnail_url}
                onChange={(e) =>
                  setFormData({ ...formData, thumbnail_url: e.target.value })
                }
                className="input"
                placeholder="https://example.com/image.jpg"
              />
            </div>
          </div>
        </div>

        {/* Skills Taught */}
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
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addSkill();
                  }
                }}
                className="input flex-1"
                placeholder="Add a skill (e.g., Python, Data Analysis)"
              />
              <button
                type="button"
                onClick={addSkill}
                className="btn-secondary px-6"
              >
                Add
              </button>
            </div>

            {formData.skills_taught.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {formData.skills_taught.map((skill) => (
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
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addPrerequisite();
                  }
                }}
                className="input flex-1"
                placeholder="Add a prerequisite (e.g., Basic programming knowledge)"
              />
              <button
                type="button"
                onClick={addPrerequisite}
                className="btn-secondary px-6"
              >
                Add
              </button>
            </div>

            {formData.prerequisites.length > 0 && (
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
                      className="hover:text-gray-900"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-4">
          <button
            type="submit"
            disabled={loading}
            className="btn-primary flex items-center gap-2"
          >
            <Save className="w-5 h-5" />
            {loading ? 'Creating...' : 'Create Course'}
          </button>
          <Link href="/instructor/courses" className="btn-secondary">
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}
