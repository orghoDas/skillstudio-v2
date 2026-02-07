'use client';

import React, { useState } from 'react';
import { Download, Award, CheckCircle } from 'lucide-react';
import api from '@/lib/api';

interface CertificateDisplayProps {
  enrollmentId: string;
  courseTitle: string;
  completionDate?: string;
  certificateUrl?: string | null;
}

export default function CertificateDisplay({
  enrollmentId,
  courseTitle,
  completionDate,
  certificateUrl: initialCertificateUrl
}: CertificateDisplayProps) {
  const [certificateUrl, setCertificateUrl] = useState<string | null>(initialCertificateUrl || null);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerateCertificate = async () => {
    setGenerating(true);
    setError(null);

    try {
      const response = await api.post(`/certificates/generate/${enrollmentId}`);
      setCertificateUrl(response.data.certificate_url);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate certificate');
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = async () => {
    try {
      const response = await api.get(`/certificates/download/${enrollmentId}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `certificate_${courseTitle.replace(/\s+/g, '_')}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err: any) {
      setError('Failed to download certificate');
    }
  };

  if (!certificateUrl) {
    return (
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6">
        <div className="flex items-center gap-4">
          <Award className="w-12 h-12 text-purple-600" />
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 mb-1">
              Congratulations on completing this course!
            </h3>
            <p className="text-gray-600 text-sm">
              Generate your certificate to showcase your achievement
            </p>
          </div>
          <button
            onClick={handleGenerateCertificate}
            disabled={generating}
            className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 font-medium"
          >
            {generating ? 'Generating...' : 'Generate Certificate'}
          </button>
        </div>

        {error && (
          <p className="mt-4 text-red-600 text-sm">{error}</p>
        )}
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-lg p-6">
      <div className="flex items-start gap-4">
        <div className="p-3 bg-green-100 rounded-full">
          <CheckCircle className="w-8 h-8 text-green-600" />
        </div>
        
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
            <Award className="w-5 h-5 text-green-600" />
            Certificate Available
          </h3>
          
          <p className="text-gray-600 mb-4">
            Course: <strong>{courseTitle}</strong>
            {completionDate && (
              <span className="text-gray-500"> • Completed on {completionDate}</span>
            )}
          </p>

          <div className="flex gap-3">
            <button
              onClick={handleDownload}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
            >
              <Download className="w-4 h-4" />
              Download Certificate
            </button>
            
            <a
              href={certificateUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 bg-white border border-green-600 text-green-600 rounded-lg hover:bg-green-50 font-medium"
            >
              View Online
            </a>
          </div>

          <p className="mt-3 text-sm text-gray-500">
            Share your achievement on LinkedIn and other platforms!
          </p>
        </div>
      </div>

      {error && (
        <p className="mt-4 text-red-600 text-sm">{error}</p>
      )}
    </div>
  );
}
