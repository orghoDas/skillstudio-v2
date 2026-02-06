'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { createCheckout, getCoursePricing, type CoursePricing } from '@/lib/monetization-service';
import { getCourseById, type Course } from '@/lib/course-service';

export default function CheckoutPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const courseId = searchParams.get('courseId');
  const subscriptionId = searchParams.get('subscriptionId');
  const billingCycle = searchParams.get('billingCycle') as 'monthly' | 'yearly' || 'monthly';

  const [course, setCourse] = useState<Course | null>(null);
  const [pricing, setPricing] = useState<CoursePricing | null>(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState('');
  const [paymentMethod, setPaymentMethod] = useState<'stripe' | 'paypal'>('stripe');

  useEffect(() => {
    if (courseId) {
      loadCourseData();
    } else if (subscriptionId) {
      setLoading(false);
    }
  }, [courseId, subscriptionId]);

  async function loadCourseData() {
    if (!courseId) return;

    try {
      setLoading(true);
      const [courseData, pricingData] = await Promise.all([
        getCourseById(courseId),
        getCoursePricing(courseId),
      ]);
      setCourse(courseData);
      setPricing(pricingData);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleCheckout() {
    try {
      setProcessing(true);
      setError('');

      const checkoutData = {
        item_type: courseId ? 'course' : 'subscription',
        item_id: (courseId || subscriptionId)!,
        billing_cycle: courseId ? undefined : billingCycle,
        payment_method: paymentMethod,
        return_url: `${window.location.origin}/dashboard/checkout/success`,
        cancel_url: `${window.location.origin}/dashboard/checkout`,
      };

      const response = await createCheckout(checkoutData as any);

      // If there's a redirect URL (for PayPal), redirect there
      if (response.redirect_url) {
        window.location.href = response.redirect_url;
        return;
      }

      // If there's a client secret (for Stripe), handle Stripe checkout
      if (response.client_secret) {
        // In a real implementation, you would use Stripe Elements here
        // For now, we'll just redirect to success page
        router.push('/dashboard/checkout/success?payment_id=' + response.payment.id);
        return;
      }

      // Otherwise, show success message
      router.push('/dashboard/checkout/success?payment_id=' + response.payment.id);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setProcessing(false);
    }
  }

  const getPrice = () => {
    if (!pricing) return 0;
    if (pricing.is_free) return 0;
    if (pricing.is_on_sale && pricing.sale_price) {
      const now = new Date();
      const saleStart = pricing.sale_start_date ? new Date(pricing.sale_start_date) : null;
      const saleEnd = pricing.sale_end_date ? new Date(pricing.sale_end_date) : null;
      
      if ((!saleStart || now >= saleStart) && (!saleEnd || now <= saleEnd)) {
        return pricing.sale_price;
      }
    }
    return pricing.base_price;
  };

  const isOnSale = () => {
    if (!pricing) return false;
    if (!pricing.is_on_sale || !pricing.sale_price) return false;
    
    const now = new Date();
    const saleStart = pricing.sale_start_date ? new Date(pricing.sale_start_date) : null;
    const saleEnd = pricing.sale_end_date ? new Date(pricing.sale_end_date) : null;
    
    return (!saleStart || now >= saleStart) && (!saleEnd || now <= saleEnd);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading checkout...</p>
        </div>
      </div>
    );
  }

  if (!courseId && !subscriptionId) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Invalid Checkout</h1>
          <p className="text-gray-600 mb-4">No course or subscription selected.</p>
          <button
            onClick={() => router.push('/dashboard/courses')}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
          >
            Browse Courses
          </button>
        </div>
      </div>
    );
  }

  const price = getPrice();
  const onSale = isOnSale();

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="px-8 py-6 bg-gray-50 border-b border-gray-200">
            <h1 className="text-3xl font-bold text-gray-900">Checkout</h1>
          </div>

          <div className="p-8">
            {error && (
              <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}

            <div className="grid md:grid-cols-2 gap-8">
              {/* Order Summary */}
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Order Summary</h2>
                
                {course && (
                  <div className="border border-gray-200 rounded-lg p-4">
                    {course.thumbnail_url && (
                      <img
                        src={course.thumbnail_url}
                        alt={course.title}
                        className="w-full h-40 object-cover rounded-lg mb-4"
                      />
                    )}
                    <h3 className="font-semibold text-lg text-gray-900 mb-2">{course.title}</h3>
                    <p className="text-gray-600 text-sm mb-4">{course.description}</p>
                    
                    <div className="border-t border-gray-200 pt-4">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-gray-600">Price:</span>
                        <span className={`font-semibold ${onSale ? 'line-through text-gray-400' : 'text-gray-900'}`}>
                          ${pricing?.base_price.toFixed(2)}
                        </span>
                      </div>
                      {onSale && (
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-gray-600">Sale Price:</span>
                          <span className="font-semibold text-green-600">
                            ${price.toFixed(2)}
                          </span>
                        </div>
                      )}
                      <div className="flex justify-between items-center text-lg font-bold border-t border-gray-200 pt-2 mt-2">
                        <span>Total:</span>
                        <span className="text-blue-600">${price.toFixed(2)}</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Payment Method */}
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Payment Method</h2>
                
                <div className="space-y-4 mb-6">
                  <label className="flex items-center p-4 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                    <input
                      type="radio"
                      name="paymentMethod"
                      value="stripe"
                      checked={paymentMethod === 'stripe'}
                      onChange={(e) => setPaymentMethod(e.target.value as 'stripe')}
                      className="h-4 w-4 text-blue-600"
                    />
                    <div className="ml-3">
                      <div className="flex items-center">
                        <span className="font-medium text-gray-900">Credit/Debit Card</span>
                        <span className="ml-2 text-xs text-gray-500">(Stripe)</span>
                      </div>
                      <p className="text-sm text-gray-600">Pay securely with your card</p>
                    </div>
                  </label>

                  <label className="flex items-center p-4 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                    <input
                      type="radio"
                      name="paymentMethod"
                      value="paypal"
                      checked={paymentMethod === 'paypal'}
                      onChange={(e) => setPaymentMethod(e.target.value as 'paypal')}
                      className="h-4 w-4 text-blue-600"
                    />
                    <div className="ml-3">
                      <div className="flex items-center">
                        <span className="font-medium text-gray-900">PayPal</span>
                      </div>
                      <p className="text-sm text-gray-600">Pay with your PayPal account</p>
                    </div>
                  </label>
                </div>

                {/* Security Info */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                  <div className="flex">
                    <svg className="h-5 w-5 text-blue-600 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                    </svg>
                    <div>
                      <h4 className="text-sm font-semibold text-blue-900">Secure Payment</h4>
                      <p className="text-sm text-blue-700 mt-1">
                        Your payment information is encrypted and secure. We never store your card details.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Checkout Button */}
                <button
                  onClick={handleCheckout}
                  disabled={processing || (pricing?.is_free === false && price === 0)}
                  className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {processing ? 'Processing...' : `Pay $${price.toFixed(2)}`}
                </button>

                <p className="text-xs text-gray-500 text-center mt-4">
                  By completing this purchase, you agree to our Terms of Service and Privacy Policy
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Money-back Guarantee */}
        <div className="mt-8 text-center">
          <div className="inline-flex items-center text-gray-600">
            <svg className="h-5 w-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span className="text-sm font-medium">30-day money-back guarantee</span>
          </div>
        </div>
      </div>
    </div>
  );
}
