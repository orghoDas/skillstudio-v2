'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { authService } from '@/lib/auth';
import { courseService, Course, Module, Lesson, Enrollment, LessonProgress } from '@/lib/course-service';
import { 
  BookOpen,
  CheckCircle,
  Circle,
  ChevronLeft,
  ChevronRight,
  Loader2,
  AlertCircle,
  ArrowLeft,
  Play,
  FileText,
  Code,
  Video,
  Lock,
  Clock
} from 'lucide-react';

export default function CourseLearningPage() {
  const router = useRouter();
  const params = useParams();
  const courseId = params.id as string;

  const [course, setCourse] = useState<Course | null>(null);
  const [modules, setModules] = useState<Module[]>([]);
  const [currentModule, setCurrentModule] = useState<Module | null>(null);
  const [currentLesson, setCurrentLesson] = useState<Lesson | null>(null);
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [enrollment, setEnrollment] = useState<Enrollment | null>(null);
  const [lessonProgress, setLessonProgress] = useState<Map<string, LessonProgress>>(new Map());
  const [loading, setLoading] = useState(true);
  const [savingProgress, setSavingProgress] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    if (!authService.isAuthenticated()) {
      router.push('/login');
      return;
    }

    loadCourseContent();
  }, [router, courseId]);

  const loadCourseContent = async () => {
    try {
      setError(null);
      setLoading(true);
      
      const [courseData, modulesData, enrollmentsData] = await Promise.all([
        courseService.getCourse(courseId),
        courseService.getModules(courseId),
        courseService.getMyEnrollments(),
      ]);

      setCourse(courseData);
      setModules(modulesData);
      
      // Check enrollment
      const userEnrollment = enrollmentsData.find(e => e.course_id === courseId);
      if (!userEnrollment) {
        alert('You must enroll in this course first');
        router.push(`/dashboard/courses/${courseId}`);
        return;
      }
      setEnrollment(userEnrollment);

      // Load first module and its lessons
      if (modulesData.length > 0) {
        const firstModule = modulesData[0];
        setCurrentModule(firstModule);
        await loadLessons(firstModule.id);
      }
      
    } catch (error: any) {
      console.error('Failed to load course content:', error);
      setError(error.message || 'Failed to load course');
    } finally {
      setLoading(false);
    }
  };

  const loadLessons = async (moduleId: string) => {
    try {
      const lessonsData = await courseService.getLessons(moduleId);
      setLessons(lessonsData);
      
      // Set first lesson as current if none selected
      if (lessonsData.length > 0 && !currentLesson) {
        setCurrentLesson(lessonsData[0]);
      }
    } catch (error: any) {
      console.error('Failed to load lessons:', error);
    }
  };

  const handleModuleClick = async (module: Module) => {
    setCurrentModule(module);
    setCurrentLesson(null);
    await loadLessons(module.id);
  };

  const handleLessonClick = (lesson: Lesson) => {
    setCurrentLesson(lesson);
  };

  const markLessonComplete = async () => {
    if (!currentLesson) return;

    setSavingProgress(true);
    try {
      await courseService.updateLessonProgress(currentLesson.id, {
        status: 'completed',
        completion_percentage: 100,
        time_spent_seconds: 0 // Track this in real implementation
      });

      // Update local progress
      const newProgress = new Map(lessonProgress);
      newProgress.set(currentLesson.id, {
        id: currentLesson.id,
        lesson_id: currentLesson.id,
        user_id: authService.getCurrentUser()?.id || '',
        status: 'completed',
        completion_percentage: 100,
        time_spent_seconds: 0,
        first_accessed: new Date().toISOString(),
        last_accessed: new Date().toISOString(),
        completed_at: new Date().toISOString()
      });
      setLessonProgress(newProgress);

      // Auto-advance to next lesson
      const currentIndex = lessons.findIndex(l => l.id === currentLesson.id);
      if (currentIndex < lessons.length - 1) {
        setCurrentLesson(lessons[currentIndex + 1]);
      } else {
        // Check if there's a next module
        const moduleIndex = modules.findIndex(m => m.id === currentModule?.id);
        if (moduleIndex < modules.length - 1) {
          await handleModuleClick(modules[moduleIndex + 1]);
        }
      }
    } catch (error: any) {
      console.error('Failed to save progress:', error);
      alert('Failed to save progress: ' + error.message);
    } finally {
      setSavingProgress(false);
    }
  };

  const goToPreviousLesson = () => {
    if (!currentLesson) return;
    const currentIndex = lessons.findIndex(l => l.id === currentLesson.id);
    if (currentIndex > 0) {
      setCurrentLesson(lessons[currentIndex - 1]);
    } else {
      // Go to previous module
      const moduleIndex = modules.findIndex(m => m.id === currentModule?.id);
      if (moduleIndex > 0) {
        handleModuleClick(modules[moduleIndex - 1]);
      }
    }
  };

  const goToNextLesson = () => {
    if (!currentLesson) return;
    const currentIndex = lessons.findIndex(l => l.id === currentLesson.id);
    if (currentIndex < lessons.length - 1) {
      setCurrentLesson(lessons[currentIndex + 1]);
    } else {
      // Go to next module
      const moduleIndex = modules.findIndex(m => m.id === currentModule?.id);
      if (moduleIndex < modules.length - 1) {
        handleModuleClick(modules[moduleIndex + 1]);
      }
    }
  };

  const getLessonIcon = (contentType: string) => {
    switch (contentType.toLowerCase()) {
      case 'video': return <Video className="w-5 h-5" />;
      case 'text': return <FileText className="w-5 h-5" />;
      case 'code': return <Code className="w-5 h-5" />;
      case 'quiz': return <BookOpen className="w-5 h-5" />;
      default: return <Circle className="w-5 h-5" />;
    }
  };

  const isLessonComplete = (lessonId: string) => {
    const progress = lessonProgress.get(lessonId);
    return progress?.status === 'completed';
  };

  const renderLessonContent = () => {
    if (!currentLesson) {
      return (
        <div className="flex items-center justify-center h-full text-gray-500">
          <div className="text-center">
            <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p>Select a lesson to start learning</p>
          </div>
        </div>
      );
    }

    const contentType = currentLesson.content_type.toLowerCase();

    return (
      <div className="h-full flex flex-col">
        {/* Lesson Header */}
        <div className="bg-white border-b border-gray-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-3">
              {getLessonIcon(contentType)}
              <h1 className="text-2xl font-bold text-gray-900">
                {String(currentLesson.title)}
              </h1>
            </div>
            {isLessonComplete(currentLesson.id) && (
              <CheckCircle className="w-6 h-6 text-green-600" />
            )}
          </div>
          <div className="flex items-center gap-4 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4" />
              <span>{currentLesson.estimated_minutes} minutes</span>
            </div>
            <span className="px-2 py-1 bg-gray-100 rounded text-xs font-medium uppercase">
              {contentType}
            </span>
          </div>
        </div>

        {/* Lesson Content */}
        <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
          <div className="max-w-4xl mx-auto">
            {contentType === 'video' && currentLesson.content_url && (
              <div className="bg-black rounded-lg overflow-hidden mb-6">
                <video controls className="w-full" src={String(currentLesson.content_url)}>
                  Your browser does not support the video tag.
                </video>
              </div>
            )}

            {contentType === 'text' && currentLesson.content_body && (
              <div className="bg-white rounded-lg p-8 shadow-sm">
                <div className="prose max-w-none">
                  <div className="whitespace-pre-line text-gray-700 leading-relaxed">
                    {String(currentLesson.content_body)}
                  </div>
                </div>
              </div>
            )}

            {contentType === 'code' && currentLesson.content_body && (
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <pre className="bg-gray-900 text-gray-100 p-6 rounded-lg overflow-x-auto">
                  <code>{String(currentLesson.content_body)}</code>
                </pre>
              </div>
            )}

            {/* Learning Objectives */}
            {currentLesson.learning_objectives && currentLesson.learning_objectives.length > 0 && (
              <div className="bg-white rounded-lg p-6 shadow-sm mt-6">
                <h3 className="font-bold text-gray-900 mb-4">Learning Objectives</h3>
                <ul className="space-y-2">
                  {currentLesson.learning_objectives.map((obj, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-gray-700">
                      <CheckCircle className="w-5 h-5 text-primary-600 mt-0.5 flex-shrink-0" />
                      <span>{typeof obj === 'string' ? obj : String(obj)}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Skill Tags */}
            {currentLesson.skill_tags && currentLesson.skill_tags.length > 0 && (
              <div className="bg-white rounded-lg p-6 shadow-sm mt-6">
                <h3 className="font-bold text-gray-900 mb-4">Skills Covered</h3>
                <div className="flex flex-wrap gap-2">
                  {currentLesson.skill_tags.map((skill, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-primary-50 text-primary-700 rounded-lg text-sm font-medium"
                    >
                      {typeof skill === 'string' ? skill : String(skill)}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Navigation Footer */}
        <div className="bg-white border-t border-gray-200 p-4">
          <div className="max-w-4xl mx-auto flex items-center justify-between">
            <button
              onClick={goToPreviousLesson}
              disabled={modules[0]?.id === currentModule?.id && lessons[0]?.id === currentLesson.id}
              className="btn-secondary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-5 h-5" />
              Previous
            </button>

            {!isLessonComplete(currentLesson.id) && (
              <button
                onClick={markLessonComplete}
                disabled={savingProgress}
                className="btn-primary flex items-center gap-2"
              >
                {savingProgress ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-5 h-5" />
                    Mark Complete
                  </>
                )}
              </button>
            )}

            <button
              onClick={goToNextLesson}
              disabled={modules[modules.length - 1]?.id === currentModule?.id && 
                       lessons[lessons.length - 1]?.id === currentLesson.id}
              className="btn-secondary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  if (error || !course) {
    return (
      <div className="p-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 flex items-start gap-4">
            <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-lg font-semibold text-red-900 mb-2">Failed to Load Course</h3>
              <p className="text-red-700 mb-4">{error || 'Course not found'}</p>
              <button onClick={() => router.push('/dashboard/courses')} className="btn-primary">
                Back to Courses
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-80' : 'w-0'} transition-all duration-300 bg-white border-r border-gray-200 overflow-hidden flex flex-col`}>
        {/* Course Header */}
        <div className="p-4 border-b border-gray-200">
          <button
            onClick={() => router.push(`/dashboard/courses/${courseId}`)}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-3 text-sm"
          >
            <ArrowLeft className="w-4 h-4" />
            Course Details
          </button>
          <h2 className="font-bold text-gray-900 line-clamp-2">{String(course.title)}</h2>
          {enrollment && (
            <div className="mt-2">
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-gray-600">Progress</span>
                <span className="font-medium text-primary-600">{enrollment.progress_percentage}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${enrollment.progress_percentage}%` }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Modules & Lessons */}
        <div className="flex-1 overflow-y-auto">
          {modules.map((module, moduleIdx) => (
            <div key={module.id} className="border-b border-gray-200">
              <button
                onClick={() => handleModuleClick(module)}
                className={`w-full p-4 text-left hover:bg-gray-50 transition-colors ${
                  currentModule?.id === module.id ? 'bg-primary-50' : ''
                }`}
              >
                <div className="font-semibold text-gray-900 mb-1">
                  Module {moduleIdx + 1}: {String(module.title)}
                </div>
                <div className="text-sm text-gray-600">{module.est_duration_minutes} min</div>
              </button>

              {currentModule?.id === module.id && lessons.length > 0 && (
                <div className="bg-gray-50">
                  {lessons.map((lesson, lessonIdx) => (
                    <button
                      key={lesson.id}
                      onClick={() => handleLessonClick(lesson)}
                      className={`w-full p-3 pl-8 text-left hover:bg-gray-100 transition-colors flex items-center gap-3 ${
                        currentLesson?.id === lesson.id ? 'bg-primary-100 border-l-4 border-primary-600' : ''
                      }`}
                    >
                      <div className="flex-shrink-0">
                        {isLessonComplete(lesson.id) ? (
                          <CheckCircle className="w-5 h-5 text-green-600" />
                        ) : currentLesson?.id === lesson.id ? (
                          <Play className="w-5 h-5 text-primary-600" />
                        ) : (
                          <Circle className="w-5 h-5 text-gray-400" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-gray-900 line-clamp-2">
                          {lessonIdx + 1}. {String(lesson.title)}
                        </div>
                        <div className="text-xs text-gray-600 mt-1">
                          {lesson.estimated_minutes} min • {lesson.content_type}
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}

          {modules.length === 0 && (
            <div className="p-8 text-center text-gray-500">
              <BookOpen className="w-12 h-12 text-gray-300 mx-auto mb-2" />
              <p>No modules available</p>
            </div>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Toggle Sidebar Button */}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="absolute top-4 left-4 z-10 p-2 bg-white rounded-lg shadow-lg hover:shadow-xl transition-shadow"
        >
          {sidebarOpen ? <ChevronLeft className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
        </button>

        {renderLessonContent()}
      </div>
    </div>
  );
}
