'use client';

import Link from 'next/link';
import { XCircle, ArrowLeft, RefreshCw } from 'lucide-react';

export default function CheckoutCancelPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-50 flex items-center justify-center px-4 py-12">
      <div className="max-w-2xl w-full">
        {/* Cancel Card */}
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          {/* Cancel Icon */}
          <div className="bg-gradient-to-r from-red-500 to-orange-500 px-6 py-12 text-center">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-white rounded-full mb-4">
              <XCircle className="w-12 h-12 text-red-500" />
            </div>
            <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">
              Payment Cancelled
            </h1>
            <p className="text-red-100 text-lg">
              Your payment was not completed
            </p>
          </div>

          {/* Details */}
          <div className="px-6 py-8 md:px-8">
            <div className="text-center mb-8">
              <p className="text-gray-600 mb-4">
                Your payment was cancelled and no charges were made to your account.
              </p>
              <p className="text-sm text-gray-500">
                You can try again whenever you're ready, or browse other courses.
              </p>
            </div>

            {/* Reasons */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
              <h3 className="font-semibold text-blue-900 mb-3">Common Reasons for Cancellation:</h3>
              <ul className="space-y-2 text-sm text-blue-800">
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 mt-0.5">•</span>
                  <span>Changed your mind about the purchase</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 mt-0.5">•</span>
                  <span>Payment information wasn't ready</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 mt-0.5">•</span>
                  <span>Want to explore more options first</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 mt-0.5">•</span>
                  <span>Technical issues during checkout</span>
                </li>
              </ul>
            </div>

            {/* Action Buttons */}
            <div className="space-y-3">
              <Link
                href="/dashboard/courses"
                className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-purple-700 hover:to-blue-700 transition-all shadow-md hover:shadow-lg"
              >
                <RefreshCw className="w-5 h-5" />
                <span>Browse Courses</span>
              </Link>

              <Link
                href="/dashboard"
                className="w-full flex items-center justify-center gap-2 bg-white border-2 border-gray-300 text-gray-700 py-3 px-6 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
                <span>Back to Dashboard</span>
              </Link>
            </div>
          </div>
        </div>

        {/* Help Section */}
        <div className="mt-8 bg-white rounded-xl shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Need Assistance?</h3>
          <div className="space-y-3">
            <p className="text-sm text-gray-600">
              If you encountered any issues during checkout or have questions about our courses:
            </p>
            <div className="flex flex-col sm:flex-row gap-3">
              <Link
                href="/support"
                className="flex-1 text-center px-4 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors font-medium text-sm"
              >
                Contact Support
              </Link>
              <Link
                href="/faq"
                className="flex-1 text-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium text-sm"
              >
                View FAQ
              </Link>
            </div>
          </div>
        </div>

        {/* Alternative Options */}
        <div className="mt-6 bg-gradient-to-r from-purple-100 to-blue-100 rounded-lg p-6">
          <h3 className="font-semibold text-gray-900 mb-3">Explore Free Options</h3>
          <p className="text-sm text-gray-700 mb-4">
            Not ready to purchase? Check out our free courses and resources to get started with your learning journey.
          </p>
          <Link
            href="/dashboard/courses?filter=free"
            className="inline-flex items-center gap-2 text-purple-700 hover:text-purple-900 font-medium text-sm"
          >
            <span>View Free Courses</span>
            <ArrowLeft className="w-4 h-4 rotate-180" />
          </Link>
        </div>
      </div>
    </div>
  );
}
