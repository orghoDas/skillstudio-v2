'use client';

import { useState, useEffect } from 'react';
import { Award, Download, Share2, ExternalLink, Check } from 'lucide-react';
import { socialService, Certificate } from '@/lib/social-service';

export default function MyCertificatesPage() {
  const [certificates, setCertificates] = useState<Certificate[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCertificates();
  }, []);

  const fetchCertificates = async () => {
    try {
      setLoading(true);
      const data = await socialService.getMyCertificates();
      setCertificates(data);
    } catch (error) {
      console.error('Failed to fetch certificates:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleShare = (cert: Certificate) => {
    if (navigator.share) {
      navigator.share({
        title: `Certificate - ${cert.certificate_number}`,
        text: `Check out my certificate!`,
        url: cert.verification_url || '',
      });
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(cert.verification_url || '');
      alert('Verification link copied to clipboard!');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">My Certificates</h1>
        <p className="text-gray-600 mt-2">
          Your learning achievements and credentials
        </p>
      </div>

      {certificates.length === 0 ? (
        <div className="card text-center py-16">
          <Award className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            No Certificates Yet
          </h2>
          <p className="text-gray-600 mb-6">
            Complete a course to earn your first certificate!
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {certificates.map((cert) => (
            <div
              key={cert.id}
              className="card hover:shadow-lg transition-shadow relative overflow-hidden"
            >
              {/* Decorative Corner */}
              <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-bl from-primary-100 to-transparent"></div>
              
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0">
                  <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
                    <Award className="w-8 h-8 text-white" />
                  </div>
                </div>

                <div className="flex-1">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h3 className="font-semibold text-gray-900 text-lg">
                        Course Completion Certificate
                      </h3>
                      <p className="text-sm text-gray-600 font-mono">
                        {cert.certificate_number}
                      </p>
                    </div>
                    <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded text-xs">
                      <Check className="w-3 h-3" />
                      Verified
                    </span>
                  </div>

                  <div className="space-y-2 mb-4">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Completion:</span>
                      <span className="font-semibold text-gray-900">
                        {cert.completion_percentage}%
                      </span>
                    </div>
                    {cert.final_grade && (
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Final Grade:</span>
                        <span className="font-semibold text-gray-900">
                          {cert.final_grade}%
                        </span>
                      </div>
                    )}
                    {cert.total_hours_spent && (
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Time Spent:</span>
                        <span className="font-semibold text-gray-900">
                          {cert.total_hours_spent} hours
                        </span>
                      </div>
                    )}
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Issued:</span>
                      <span className="font-semibold text-gray-900">
                        {new Date(cert.issued_date).toLocaleDateString()}
                      </span>
                    </div>
                  </div>

                  {cert.skills_achieved && cert.skills_achieved.length > 0 && (
                    <div className="mb-4">
                      <p className="text-xs text-gray-600 mb-2">Skills Achieved:</p>
                      <div className="flex flex-wrap gap-1">
                        {cert.skills_achieved.map((skill, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-1 bg-primary-100 text-primary-700 rounded text-xs"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="flex gap-2">
                    {cert.certificate_url && (
                      <a
                        href={cert.certificate_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn-secondary text-sm flex items-center gap-2"
                      >
                        <Download className="w-4 h-4" />
                        Download
                      </a>
                    )}
                    <button
                      onClick={() => handleShare(cert)}
                      className="btn-secondary text-sm flex items-center gap-2"
                    >
                      <Share2 className="w-4 h-4" />
                      Share
                    </button>
                    {cert.verification_url && (
                      <a
                        href={cert.verification_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn-secondary text-sm flex items-center gap-2"
                      >
                        <ExternalLink className="w-4 h-4" />
                        Verify
                      </a>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Stats Summary */}
      {certificates.length > 0 && (
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="card text-center">
            <div className="text-3xl font-bold text-primary-600 mb-1">
              {certificates.length}
            </div>
            <div className="text-sm text-gray-600">Certificates Earned</div>
          </div>
          <div className="card text-center">
            <div className="text-3xl font-bold text-primary-600 mb-1">
              {Math.round(
                certificates.reduce((sum, cert) => sum + (cert.total_hours_spent || 0), 0)
              )}h
            </div>
            <div className="text-sm text-gray-600">Total Learning Time</div>
          </div>
          <div className="card text-center">
            <div className="text-3xl font-bold text-primary-600 mb-1">
              {Math.round(
                certificates.reduce(
                  (sum, cert) => sum + (cert.final_grade || cert.completion_percentage),
                  0
                ) / certificates.length  
              )}%
            </div>
            <div className="text-sm text-gray-600">Average Performance</div>
          </div>
        </div>
      )}
    </div>
  );
}
