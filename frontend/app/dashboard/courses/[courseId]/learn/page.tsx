'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  ChevronLeft,
  ChevronRight,
  CheckCircle,
  Circle,
  BookOpen,
  Play,
  FileText,
  Code,
  Brain,
  Clock,
  Award,
} from 'lucide-react';
import { instructorCourseService, Course, Module } from '@/lib/instructor-course-service';
import { lessonService, Lesson, LessonProgress } from '@/lib/lesson-service';

export default function LearnCoursePage() {
  const params = useParams();
  const router = useRouter();
  const courseId = params.courseId as string;

  const [course, setCourse] = useState<Course | null>(null);
  const [modules, setModules] = useState<Module[]>([]);
  const [allLessons, setAllLessons] = useState<Lesson[]>([]);
  const [currentLesson, setCurrentLesson] = useState<Lesson | null>(null);
  const [progress, setProgress] = useState<LessonProgress | null>(null);
  const [loading, setLoading] = useState(true);
  const [startTime, setStartTime] = useState<Date>(new Date());
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    fetchCourseData();
  }, [courseId]);

  useEffect(() => {
    if (currentLesson) {
      fetchLessonProgress();
      setStartTime(new Date());
    }
  }, [currentLesson]);

  const fetchCourseData = async () => {
    try {
      setLoading(true);
      const [courseData, modulesData] = await Promise.all([
        instructorCourseService.getCourse(courseId),
        instructorCourseService.getModules(courseId),
      ]);

      setCourse(courseData);
      setModules(modulesData);

      // Fetch all lessons for all modules
      const lessonsPromises = modulesData.map((module) =>
        lessonService.getModuleLessons(module.id)
      );
      const lessonsArrays = await Promise.all(lessonsPromises);
      const lessons = lessonsArrays.flat().sort((a, b) => a.sequence_order - b.sequence_order);
      
      setAllLessons(lessons);

      // Set first lesson as current if none selected
      if (lessons.length > 0 && !currentLesson) {
        setCurrentLesson(lessons[0]);
      }
    } catch (error) {
      console.error('Failed to fetch course data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchLessonProgress = async () => {
    if (!currentLesson) return;
    
    try {
      const progressData = await lessonService.getLessonProgress(currentLesson.id);
      setProgress(progressData);
    } catch (error) {
      console.error('Failed to fetch lesson progress:', error);
    }
  };

  const handleMarkComplete = async () => {
    if (!currentLesson) return;

    const timeSpent = Math.floor((new Date().getTime() - startTime.getTime()) / 1000);

    try {
      await lessonService.markComplete(currentLesson.id, timeSpent);
      await fetchLessonProgress();
      
      // Move to next lesson
      const currentIndex = allLessons.findIndex((l) => l.id === currentLesson.id);
      if (currentIndex < allLessons.length - 1) {
        setCurrentLesson(allLessons[currentIndex + 1]);
      }
    } catch (error) {
      console.error('Failed to mark complete:', error);
    }
  };

  const navigateLesson = (direction: 'prev' | 'next') => {
    const currentIndex = allLessons.findIndex((l) => l.id === currentLesson?.id);
    if (direction === 'prev' && currentIndex > 0) {
      setCurrentLesson(allLessons[currentIndex - 1]);
    } else if (direction === 'next' && currentIndex < allLessons.length - 1) {
      setCurrentLesson(allLessons[currentIndex + 1]);
    }
  };

  const getContentIcon = (type: string) => {
    switch (type) {
      case 'video':
        return Play;
      case 'article':
        return FileText;
      case 'quiz':
        return Brain;
      case 'code_exercise':
        return Code;
      default:
        return BookOpen;
    }
  };

  if (loading || !course) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const currentIndex = allLessons.findIndex((l) => l.id === currentLesson?.id);
  const hasPrev = currentIndex > 0;
  const hasNext = currentIndex < allLessons.length - 1;
  const isCompleted = progress?.completion_percentage === 100;

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar - Course Navigation */}
      <aside
        className={`${
          sidebarOpen ? 'w-80' : 'w-0'
        } bg-white border-r border-gray-200 overflow-y-auto transition-all duration-300`}
      >
        <div className="p-6">
          <Link
            href="/dashboard/my-courses"
            className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 mb-4"
          >
            <ChevronLeft className="w-4 h-4" />
            Back to My Courses
          </Link>

          <h2 className="text-xl font-bold text-gray-900 mb-2">{course.title}</h2>
          <div className="flex items-center gap-4 text-sm text-gray-600 mb-6">
            <span className="flex items-center gap-1">
              <BookOpen className="w-4 h-4" />
              {allLessons.length} lessons
            </span>
            <span className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              {course.estimated_duration_hours}h
            </span>
          </div>

          {/* Module List */}
          <div className="space-y-4">
            {modules.map((module) => {
              const moduleLessons = allLessons.filter((l) => l.module_id === module.id);
              return (
                <div key={module.id} className="border-b border-gray-100 pb-4">
                  <h3 className="font-semibold text-gray-900 mb-2">
                    {module.sequence_order}. {module.title}
                  </h3>
                  <div className="space-y-1">
                    {moduleLessons.map((lesson) => {
                      const Icon = getContentIcon(lesson.content_type);
                      const isCurrent = currentLesson?.id === lesson.id;
                      
                      return (
                        <button
                          key={lesson.id}
                          onClick={() => setCurrentLesson(lesson)}
                          className={`w-full flex items-center gap-2 p-2 rounded-lg text-sm transition-colors ${
                            isCurrent
                              ? 'bg-primary-50 text-primary-700'
                              : 'hover:bg-gray-50 text-gray-700'
                          }`}
                        >
                          <Icon className="w-4 h-4 flex-shrink-0" />
                          <span className="flex-1 text-left truncate">{lesson.title}</span>
                          {isCompleted && <CheckCircle className="w-4 h-4 text-green-500" />}
                        </button>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        {currentLesson ? (
          <div className="max-w-4xl mx-auto p-8">
            {/* Lesson Header */}
            <div className="mb-8">
              <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
                <span>Lesson {currentIndex + 1} of {allLessons.length}</span>
                {currentLesson.estimated_minutes && (
                  <>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      {currentLesson.estimated_minutes} min
                    </span>
                  </>
                )}
              </div>
              <h1 className="text-3xl font-bold text-gray-900 mb-4">
                {currentLesson.title}
              </h1>

              {currentLesson.learning_objectives.length > 0 && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h3 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
                    <Award className="w-5 h-5" />
                    Learning Objectives
                  </h3>
                  <ul className="space-y-1">
                    {currentLesson.learning_objectives.map((objective, idx) => (
                      <li key={idx} className="text-blue-800 text-sm flex items-start gap-2">
                        <span className="text-blue-400 mt-1">•</span>
                        {objective}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Lesson Content */}
            <div className="bg-white rounded-lg border border-gray-200 p-8 mb-8">
              {currentLesson.content_type === 'video' && currentLesson.content_url ? (
                <div className="mb-6">
                  <div className="aspect-video bg-gray-900 rounded-lg overflow-hidden">
                    {currentLesson.content_url.includes('youtube.com') || 
                     currentLesson.content_url.includes('youtu.be') ? (
                      <iframe
                        src={currentLesson.content_url.replace('watch?v=', 'embed/')}
                        className="w-full h-full"
                        allowFullScreen
                      />
                    ) : (
                      <video src={currentLesson.content_url} controls className="w-full h-full" />
                    )}
                  </div>
                </div>
              ) : null}

              {currentLesson.content_body ? (
                <div 
                  className="prose max-w-none"
                  dangerouslySetInnerHTML={{ __html: currentLesson.content_body }}
                />
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <p>No content available for this lesson yet.</p>
                </div>
              )}

              {currentLesson.skill_tags.length > 0 && (
                <div className="mt-8 pt-6 border-t border-gray-200">
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">Skills Covered:</h4>
                  <div className="flex flex-wrap gap-2">
                    {currentLesson.skill_tags.map((tag) => (
                      <span
                        key={tag}
                        className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Navigation & Actions */}
            <div className="flex items-center justify-between">
              <button
                onClick={() => navigateLesson('prev')}
                disabled={!hasPrev}
                className="btn-secondary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-5 h-5" />
                Previous Lesson
              </button>

              {!isCompleted && (
                <button
                  onClick={handleMarkComplete}
                  className="btn-primary flex items-center gap-2"
                >
                  <CheckCircle className="w-5 h-5" />
                  Mark as Complete
                </button>
              )}

              {isCompleted && hasNext && (
                <button
                  onClick={() => navigateLesson('next')}
                  className="btn-primary flex items-center gap-2"
                >
                  Next Lesson
                  <ChevronRight className="w-5 h-5" />
                </button>
              )}

              {isCompleted && !hasNext && (
                <div className="flex items-center gap-2 text-green-600">
                  <CheckCircle className="w-5 h-5" />
                  <span className="font-semibold">Course Complete!</span>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto p-8 text-center">
            <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">No lessons yet</h2>
            <p className="text-gray-600">This course doesn't have any lessons yet.</p>
          </div>
        )}
      </main>
    </div>
  );
}
