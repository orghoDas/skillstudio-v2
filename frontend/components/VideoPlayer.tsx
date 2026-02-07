"use client";

import React, { useEffect, useRef, useState } from 'react';
import Hls from 'hls.js';
import { Play, Pause, Volume2, VolumeX, Maximize, Settings } from 'lucide-react';
import { trackVideoWatch } from '@/lib/video-service';

interface VideoPlayerProps {
  videoUrl: string;
  thumbnailUrl?: string;
  onTimeUpdate?: (currentTime: number, duration: number) => void;
  onEnded?: () => void;
  lessonId: string;
}

export default function VideoPlayer({
  videoUrl,
  thumbnailUrl,
  onTimeUpdate,
  onEnded,
  lessonId
}: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const hlsRef = useRef<Hls | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [showControls, setShowControls] = useState(true);
  const [quality, setQuality] = useState<string>('auto');
  const [availableQualities, setAvailableQualities] = useState<string[]>([]);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [watchStartTime, setWatchStartTime] = useState(Date.now());
  const [totalWatchedSeconds, setTotalWatchedSeconds] = useState(0);

  // Initialize HLS player
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    if (Hls.isSupported() && videoUrl.includes('.m3u8')) {
      const hls = new Hls({
        enableWorker: true
      });

      hls.loadSource(videoUrl);
      hls.attachMedia(video);

      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        const qualities = hls.levels.map((level: any) => `${level.height}p`);
        setAvailableQualities(['auto', ...qualities]);
      });

      hls.on(Hls.Events.ERROR, (_event: any, data: any) => {
        if (data.fatal) {
          console.error('HLS fatal error:', data);
        }
      });

      hlsRef.current = hls;

      return () => {
        hls.destroy();
      };
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
      // iOS devices
      video.src = videoUrl;
    }
  }, [videoUrl]);

  // Track watch analytics
  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (isPlaying) {
      interval = setInterval(() => {
        const watchedSec = (Date.now() - watchStartTime) / 1000;
        setTotalWatchedSeconds(prev => prev + 1);
      }, 1000);
    }

    return () => clearInterval(interval);
  }, [isPlaying, watchStartTime]);

  // Send analytics on unmount or when user leaves
  useEffect(() => {
    const sendAnalytics = async () => {
      if (totalWatchedSeconds > 5 && duration > 0) {
        try {
          const completionPercentage = (currentTime / duration) * 100;
          await trackVideoWatch({
            lesson_id: lessonId,
            watch_duration_seconds: Math.floor(totalWatchedSeconds),
            completion_percentage: Math.min(completionPercentage, 100),
            playback_speed: playbackSpeed,
            quality_selected: quality,
            device_type: /Mobile|Android|iPhone/.test(navigator.userAgent) ? 'mobile' : 'desktop'
          });
        } catch (error) {
          console.error('Failed to send video analytics:', error);
        }
      }
    };

    window.addEventListener('beforeunload', sendAnalytics);
    return () => {
      sendAnalytics();
      window.removeEventListener('beforeunload', sendAnalytics);
    };
  }, [totalWatchedSeconds, currentTime, duration, lessonId, playbackSpeed, quality]);

  const togglePlay = () => {
    const video = videoRef.current;
    if (!video) return;

    if (isPlaying) {
      video.pause();
    } else {
      video.play();
      setWatchStartTime(Date.now());
    }
    setIsPlaying(!isPlaying);
  };

  const toggleMute = () => {
    const video = videoRef.current;
    if (!video) return;

    video.muted = !video.muted;
    setIsMuted(!video.muted);
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const video = videoRef.current;
    if (!video) return;

    const newVolume = parseFloat(e.target.value);
    video.volume = newVolume;
    setVolume(newVolume);
    setIsMuted(newVolume === 0);
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const video = videoRef.current;
    if (!video) return;

    const newTime = parseFloat(e.target.value);
    video.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const handleTimeUpdate = () => {
    const video = videoRef.current;
    if (!video) return;

    setCurrentTime(video.currentTime);
    setDuration(video.duration);

    if (onTimeUpdate) {
      onTimeUpdate(video.currentTime, video.duration);
    }
  };

  const handleEnded = () => {
    setIsPlaying(false);
    if (onEnded) onEnded();
  };

  const changeQuality = (qualityLevel: string) => {
    const hls = hlsRef.current;
    if (!hls) return;

    if (qualityLevel === 'auto') {
      hls.currentLevel = -1;
    } else {
      const levelIndex = hls.levels.findIndex(
        (level: any) => `${level.height}p` === qualityLevel
      );
      if (levelIndex !== -1) {
        hls.currentLevel = levelIndex;
      }
    }
    setQuality(qualityLevel);
  };

  const changePlaybackSpeed = (speed: number) => {
    const video = videoRef.current;
    if (!video) return;

    video.playbackRate = speed;
    setPlaybackSpeed(speed);
  };

  const toggleFullscreen = () => {
    const video = videoRef.current;
    if (!video) return;

    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else {
      video.requestFullscreen();
    }
  };

  const formatTime = (seconds: number) => {
    if (isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div 
      className="relative w-full bg-black rounded-lg overflow-hidden"
      onMouseEnter={() => setShowControls(true)}
      onMouseLeave={() => setShowControls(false)}
    >
      <video
        ref={videoRef}
        className="w-full h-auto"
        poster={thumbnailUrl}
        onTimeUpdate={handleTimeUpdate}
        onEnded={handleEnded}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
      />

      {/* Controls overlay */}
      <div
        className={`absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4 transition-opacity ${
          showControls ? 'opacity-100' : 'opacity-0'
        }`}
      >
        {/* Progress bar */}
        <input
          type="range"
          min="0"
          max={duration || 0}
          value={currentTime}
          onChange={handleSeek}
          className="w-full mb-2 accent-blue-500"
        />

        <div className="flex items-center justify-between text-white">
          {/* Left controls */}
          <div className="flex items-center gap-3">
            <button onClick={togglePlay} className="hover:text-blue-400">
              {isPlaying ? <Pause size={24} /> : <Play size={24} />}
            </button>

            <button onClick={toggleMute} className="hover:text-blue-400">
              {isMuted || volume === 0 ? <VolumeX size={20} /> : <Volume2 size={20} />}
            </button>

            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={volume}
              onChange={handleVolumeChange}
              className="w-20 accent-blue-500"
            />

            <span className="text-sm">
              {formatTime(currentTime)} / {formatTime(duration)}
            </span>
          </div>

          {/* Right controls */}
          <div className="flex items-center gap-3">
            {/* Playback speed */}
            <select
              value={playbackSpeed}
              onChange={(e) => changePlaybackSpeed(parseFloat(e.target.value))}
              className="bg-transparent text-sm border border-gray-600 rounded px-2 py-1"
            >
              <option value="0.5">0.5x</option>
              <option value="0.75">0.75x</option>
              <option value="1">1x</option>
              <option value="1.25">1.25x</option>
              <option value="1.5">1.5x</option>
              <option value="2">2x</option>
            </select>

            {/* Quality selector */}
            {availableQualities.length > 0 && (
              <select
                value={quality}
                onChange={(e) => changeQuality(e.target.value)}
                className="bg-transparent text-sm border border-gray-600 rounded px-2 py-1"
              >
                {availableQualities.map(q => (
                  <option key={q} value={q}>{q}</option>
                ))}
              </select>
            )}

            <button onClick={toggleFullscreen} className="hover:text-blue-400">
              <Maximize size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
