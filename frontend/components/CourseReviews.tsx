'use client';

import { useState, useEffect } from 'react';
import { Star, ThumbsUp, ThumbsDown, MessageSquare, Check } from 'lucide-react';
import { socialService, CourseReview, ReviewCreate } from '@/lib/social-service';

interface CourseReviewsProps {
  courseId: string;
  userEnrolled?: boolean;
}

export default function CourseReviews({ courseId, userEnrolled = false }: CourseReviewsProps) {
  const [reviews, setReviews] = useState<CourseReview[]>([]);
  const [loading, setLoading] = useState(true);
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [sortBy, setSortBy] = useState<'recent' | 'helpful' | 'rating'>('recent');
  
  const [formData, setFormData] = useState<ReviewCreate>({
    rating: 5,
    title: '',
    review_text: '',
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchReviews();
  }, [courseId, sortBy]);

  const fetchReviews = async () => {
    try {
      setLoading(true);
      const data = await socialService.getCourseReviews(courseId, sortBy);
      setReviews(data);
    } catch (error) {
      console.error('Failed to fetch reviews:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      await socialService.createReview(courseId, formData);
      setShowReviewForm(false);
      setFormData({ rating: 5, title: '', review_text: '' });
      await fetchReviews();
      alert('Review submitted successfully!');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to submit review');
    } finally {
      setSubmitting(false);
    }
  };

  const handleMarkHelpful = async (reviewId: string, helpful: boolean) => {
    try {
      await socialService.markReviewHelpful(reviewId, helpful);
      await fetchReviews();
    } catch (error) {
      console.error('Failed to mark review:', error);
    }
  };

  const renderStars = (rating: number, interactive = false, onChange?: (rating: number) => void) => {
    return (
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            onClick={() => interactive && onChange?.(star)}
            disabled={!interactive}
            className={interactive ? 'cursor-pointer' : 'cursor-default'}
          >
            <Star
              className={`w-5 h-5 ${
                star <= rating
                  ? 'fill-yellow-400 text-yellow-400'
                  : 'text-gray-300'
              }`}
            />
          </button>
        ))}
      </div>
    );
  };

  const calculateAverageRating = () => {
    if (reviews.length === 0) return 0;
    const sum = reviews.reduce((acc, review) => acc + review.rating, 0);
    return (sum / reviews.length).toFixed(1);
  };

  const getRatingDistribution = () => {
    const distribution = { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 };
    reviews.forEach((review) => {
      distribution[review.rating as keyof typeof distribution]++;
    });
    return distribution;
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const avgRating = calculateAverageRating();
  const distribution = getRatingDistribution();

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <div className="card">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Course Reviews</h2>
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1">
                {renderStars(Math.round(typeof avgRating === 'number' ? avgRating : parseFloat(avgRating)))}
              </div>
              <span className="text-3xl font-bold text-gray-900">{avgRating}</span>
              <span className="text-gray-600">({reviews.length} reviews)</span>
            </div>
          </div>
          {userEnrolled && (
            <button
              onClick={() => setShowReviewForm(!showReviewForm)}
              className="btn-primary"
            >
              Write a Review
            </button>
          )}
        </div>

        {/* Rating Distribution */}
        <div className="space-y-2 mb-6">
          {[5, 4, 3, 2, 1].map((rating) => {
            const count = distribution[rating as keyof typeof distribution];
            const percentage = reviews.length > 0 ? (count / reviews.length) * 100 : 0;
            
            return (
              <div key={rating} className="flex items-center gap-3">
                <span className="text-sm text-gray-600 w-12">{rating} stars</span>
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-yellow-400 h-2 rounded-full transition-all"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
                <span className="text-sm text-gray-600 w-12 text-right">{count}</span>
              </div>
            );
          })}
        </div>

        {/* Sort Options */}
        <div className="flex gap-2">
          <button
            onClick={() => setSortBy('recent')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              sortBy === 'recent'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Most Recent
          </button>
          <button
            onClick={() => setSortBy('helpful')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              sortBy === 'helpful'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Most Helpful
          </button>
          <button
            onClick={() => setSortBy('rating')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              sortBy === 'rating'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Highest Rating
          </button>
        </div>
      </div>

      {/* Review Form */}
      {showReviewForm && (
        <form onSubmit={handleSubmitReview} className="card">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Write Your Review</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Your Rating *
              </label>
              {renderStars(formData.rating, true, (rating) =>
                setFormData({ ...formData, rating })
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Review Title
              </label>
              <input
                type="text"
                value={formData.title || ''}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="input"
                placeholder="Sum up your experience"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Your Review
              </label>
              <textarea
                value={formData.review_text || ''}
                onChange={(e) =>
                  setFormData({ ...formData, review_text: e.target.value })
                }
                className="input min-h-[120px]"
                placeholder="Share your thoughts about this course..."
                rows={5}
              />
            </div>

            <div className="flex gap-3">
              <button type="submit" disabled={submitting} className="btn-primary">
                {submitting ? 'Submitting...' : 'Submit Review'}
              </button>
              <button
                type="button"
                onClick={() => setShowReviewForm(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </div>
        </form>
      )}

      {/* Reviews List */}
      <div className="space-y-4">
        {reviews.length === 0 ? (
          <div className="card text-center py-12 text-gray-500">
            No reviews yet. Be the first to review this course!
          </div>
        ) : (
          reviews.map((review) => (
            <div key={review.id} className="card">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  {renderStars(review.rating)}
                  {review.is_verified_purchase && (
                    <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded text-xs">
                      <Check className="w-3 h-3" />
                      Verified
                    </span>
                  )}
                </div>
                <span className="text-sm text-gray-500">
                  {new Date(review.created_at).toLocaleDateString()}
                </span>
              </div>

              {review.title && (
                <h4 className="font-semibold text-gray-900 mb-2">{review.title}</h4>
              )}

              {review.review_text && (
                <p className="text-gray-700 mb-4">{review.review_text}</p>
              )}

              {/* Instructor Response */}
              {review.instructor_response && (
                <div className="mt-4 p-4 bg-blue-50 border-l-4 border-blue-500 rounded">
                  <div className="flex items-center gap-2 mb-2">
                    <MessageSquare className="w-4 h-4 text-blue-600" />
                    <span className="font-semibold text-blue-900">Instructor Response:</span>
                  </div>
                  <p className="text-blue-800 text-sm">{review.instructor_response}</p>
                  <span className="text-xs text-blue-600 mt-1 block">
                    {new Date(review.instructor_response_at!).toLocaleDateString()}
                  </span>
                </div>
              )}

              {/* Helpful Buttons */}
              <div className="flex items-center gap-4 mt-4 pt-4 border-t border-gray-200">
                <button
                  onClick={() => handleMarkHelpful(review.id, true)}
                  className="flex items-center gap-2 text-sm text-gray-600 hover:text-green-600 transition-colors"
                >
                  <ThumbsUp className="w-4 h-4" />
                  Helpful ({review.helpful_count})
                </button>
                <button
                  onClick={() => handleMarkHelpful(review.id, false)}
                  className="flex items-center gap-2 text-sm text-gray-600 hover:text-red-600 transition-colors"
                >
                  <ThumbsDown className="w-4 h-4" />
                  Not Helpful ({review.not_helpful_count})
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
