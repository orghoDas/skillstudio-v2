/**
 * Video Processing Service
 * Handles video upload, transcoding, and analytics
 */

import api from './api';

export interface VideoUploadInit {
  upload_url: string;
  fields: Record<string, string>;
  s3_key: string;
}

export interface TranscodingStatus {
  status: string;
  progress?: number;
  hls_url?: string;
  thumbnail_url?: string;
  error?: string;
}

export interface VideoAnalytics {
  total_views: number;
  unique_viewers: number;
  total_watch_time_seconds: number;
  average_completion_percentage: number;
  quality_distribution: Record<string, number>;
}

/**
 * Initialize video upload - get presigned S3 URL
 */
export async function initiateVideoUpload(lessonId: string, filename: string): Promise<VideoUploadInit> {
  const response = await api.post('/video/upload/init', {
    lesson_id: lessonId,
    filename
  });
  return response.data;
}

/**
 * Start video transcoding job
 */
export async function startTranscoding(lessonId: string, s3Key: string): Promise<{ job_id: string }> {
  const response = await api.post('/video/transcode/start', {
    lesson_id: lessonId,
    s3_key: s3Key
  });
  return response.data;
}

/**
 * Check transcoding status
 */
export async function checkTranscodingStatus(lessonId: string): Promise<TranscodingStatus> {
  const response = await api.get(`/video/transcode/status/${lessonId}`);
  return response.data;
}

/**
 * Track video watch analytics
 */
export async function trackVideoWatch(data: {
  lesson_id: string;
  watch_duration_seconds: number;
  completion_percentage: number;
  playback_speed?: number;
  quality_selected?: string;
  device_type?: string;
}): Promise<void> {
  await api.post('/video/track-watch', data);
}

/**
 * Get video analytics for a lesson (instructor only)
 */
export async function getVideoAnalytics(lessonId: string): Promise<VideoAnalytics> {
  const response = await api.get(`/video/analytics/${lessonId}`);
  return response.data;
}

export default {
  initiateVideoUpload,
  startTranscoding,
  checkTranscodingStatus,
  trackVideoWatch,
  getVideoAnalytics
};
