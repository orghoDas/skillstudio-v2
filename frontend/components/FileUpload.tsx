'use client';

import React, { useState, useRef } from 'react';
import { Upload, X, File, CheckCircle, AlertCircle } from 'lucide-react';
import { api } from '@/lib/api';

interface FileUploadProps {
  onUploadComplete?: (url: string) => void;
  acceptedTypes?: string;
  maxSize?: number; // in MB
  uploadType?: 'video' | 'image' | 'document';
}

export default function FileUpload({
  onUploadComplete,
  acceptedTypes = "*",
  maxSize = 100,
  uploadType = 'document'
}: FileUploadProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [error, setError] = useState<string | null>(null);
  const [uploadedUrl, setUploadedUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file size
    if (file.size > maxSize * 1024 * 1024) {
      setError(`File size must be less than ${maxSize}MB`);
      return;
    }

    setSelectedFile(file);
    setError(null);
    setUploadStatus('idle');
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setUploadStatus('uploading');
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      // Determine upload endpoint
      const endpoint = `/upload/${uploadType}`;

      // Simulate progress (you can implement real progress with axios onUploadProgress)
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 300);

      const response = await api.post(endpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      clearInterval(progressInterval);
      setUploadProgress(100);
      setUploadStatus('success');
      setUploadedUrl(response.data.url);

      if (onUploadComplete) {
        onUploadComplete(response.data.url);
      }

      // Reset after 3 seconds
      setTimeout(() => {
        setSelectedFile(null);
        setUploadProgress(0);
        setUploadStatus('idle');
      }, 3000);

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed');
      setUploadStatus('error');
    } finally {
      setUploading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setUploadProgress(0);
    setUploadStatus('idle');
    setError(null);
    setUploadedUrl(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getIconColor = () => {
    switch (uploadStatus) {
      case 'success':
        return 'text-green-500';
      case 'error':
        return 'text-red-500';
      default:
        return 'text-blue-500';
    }
  };

  return (
    <div className="w-full">
      <div
        onClick={() => fileInputRef.current?.click()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${uploadStatus === 'success' ? 'border-green-500 bg-green-50' : ''}
          ${uploadStatus === 'error' ? 'border-red-500 bg-red-50' : ''}
          ${uploadStatus === 'idle' ? 'border-gray-300 hover:border-blue-500 hover:bg-blue-50' : ''}
          ${uploadStatus === 'uploading' ? 'border-blue-500 bg-blue-50' : ''}
        `}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={acceptedTypes}
          onChange={handleFileSelect}
          className="hidden"
        />

        {!selectedFile ? (
          <div>
            <Upload className={`w-12 h-12 mx-auto mb-4 ${getIconColor()}`} />
            <p className="text-gray-700 font-medium mb-2">
              Click to upload {uploadType}
            </p>
            <p className="text-gray-500 text-sm">
              Maximum file size: {maxSize}MB
            </p>
          </div>
        ) : (
          <div>
            {uploadStatus === 'success' ? (
              <CheckCircle className="w-12 h-12 mx-auto mb-4 text-green-500" />
            ) : uploadStatus === 'error' ? (
              <AlertCircle className="w-12 h-12 mx-auto mb-4 text-red-500" />
            ) : (
              <File className="w-12 h-12 mx-auto mb-4 text-blue-500" />
            )}

            <p className="text-gray-700 font-medium mb-2">{selectedFile.name}</p>
            <p className="text-gray-500 text-sm mb-4">
              {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
            </p>

            {uploadStatus === 'uploading' && (
              <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            )}

            {uploadStatus === 'success' && uploadedUrl && (
              <div className="mb-4">
                <p className="text-green-600 font-medium">Upload successful!</p>
                <a
                  href={uploadedUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline text-sm"
                >
                  View uploaded file
                </a>
              </div>
            )}

            {error && (
              <p className="text-red-600 text-sm mb-4">{error}</p>
            )}

            <div className="flex gap-2 justify-center">
              {uploadStatus === 'idle' && (
                <>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleUpload();
                    }}
                    disabled={uploading}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    Upload
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleReset();
                    }}
                    className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                  >
                    Cancel
                  </button>
                </>
              )}

              {uploadStatus === 'uploading' && (
                <p className="text-blue-600">Uploading...</p>
              )}

              {(uploadStatus === 'success' || uploadStatus === 'error') && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleReset();
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Upload Another
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
