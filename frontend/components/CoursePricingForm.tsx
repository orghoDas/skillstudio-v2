'use client';

import { useState, useEffect } from 'react';
import {
  getCoursePricing,
  createCoursePricing,
  updateCoursePricing,
  getSubscriptionPlans,
  type CoursePricing,
  type SubscriptionPlan,
} from '@/lib/monetization-service';

interface CoursePricingFormProps {
  courseId: string;
  onSaved?: () => void;
}

export default function CoursePricingForm({ courseId, onSaved }: CoursePricingFormProps) {
  const [pricing, setPricing] = useState<CoursePricing | null>(null);
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [formData, setFormData] = useState({
    base_price: '0.00',
    currency: 'USD',
    is_free: false,
    is_on_sale: false,
    sale_price: '',
    sale_start_date: '',
    sale_end_date: '',
    instructor_revenue_percentage: '80.00',
    platform_fee_percentage: '20.00',
    included_in_subscriptions: [] as string[],
    lifetime_access: true,
    access_duration_days: '',
  });

  useEffect(() => {
    loadData();
  }, [courseId]);

  async function loadData() {
    try {
      setLoading(true);
      const [pricingData, plansData] = await Promise.all([
        getCoursePricing(courseId),
        getSubscriptionPlans(),
      ]);

      if (pricingData) {
        setPricing(pricingData);
        setFormData({
          base_price: pricingData.base_price.toString(),
          currency: pricingData.currency,
          is_free: pricingData.is_free,
          is_on_sale: pricingData.is_on_sale,
          sale_price: pricingData.sale_price?.toString() || '',
          sale_start_date: pricingData.sale_start_date
            ? new Date(pricingData.sale_start_date).toISOString().split('T')[0]
            : '',
          sale_end_date: pricingData.sale_end_date
            ? new Date(pricingData.sale_end_date).toISOString().split('T')[0]
            : '',
          instructor_revenue_percentage: pricingData.instructor_revenue_percentage.toString(),
          platform_fee_percentage: pricingData.platform_fee_percentage.toString(),
          included_in_subscriptions: pricingData.included_in_subscriptions,
          lifetime_access: pricingData.lifetime_access,
          access_duration_days: pricingData.access_duration_days?.toString() || '',
        });
      }

      setPlans(plansData.filter(p => p.is_active));
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    
    try {
      setSaving(true);
      setError('');
      setSuccess('');

      const data = {
        course_id: courseId,
        base_price: parseFloat(formData.base_price),
        currency: formData.currency,
        is_free: formData.is_free,
        is_on_sale: formData.is_on_sale,
        sale_price: formData.sale_price ? parseFloat(formData.sale_price) : undefined,
        sale_start_date: formData.sale_start_date || undefined,
        sale_end_date: formData.sale_end_date || undefined,
        instructor_revenue_percentage: parseFloat(formData.instructor_revenue_percentage),
        platform_fee_percentage: parseFloat(formData.platform_fee_percentage),
        included_in_subscriptions: formData.included_in_subscriptions,
        lifetime_access: formData.lifetime_access,
        access_duration_days: formData.access_duration_days
          ? parseInt(formData.access_duration_days)
          : undefined,
      };

      if (pricing) {
        await updateCoursePricing(pricing.id, data);
      } else {
        await createCoursePricing(data);
      }

      setSuccess('Pricing saved successfully!');
      await loadData();
      onSaved?.();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  const handlePlanToggle = (planId: string) => {
    setFormData({
      ...formData,
      included_in_subscriptions: formData.included_in_subscriptions.includes(planId)
        ? formData.included_in_subscriptions.filter(id => id !== planId)
        : [...formData.included_in_subscriptions, planId],
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Course Pricing</h2>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {success && (
        <div className="mb-4 bg-green-50 border border-green-200 rounded-lg p-4">
          <p className="text-sm text-green-800">{success}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Free Course Toggle */}
        <div className="flex items-center">
          <input
            type="checkbox"
            id="is_free"
            checked={formData.is_free}
            onChange={(e) => setFormData({ ...formData, is_free: e.target.checked })}
            className="h-4 w-4 text-blue-600 rounded"
          />
          <label htmlFor="is_free" className="ml-2 text-sm font-medium text-gray-700">
            Make this course free
          </label>
        </div>

        {!formData.is_free && (
          <>
            {/* Base Price */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Base Price *
              </label>
              <div className="flex">
                <span className="inline-flex items-center px-3 rounded-l-md border border-r-0 border-gray-300 bg-gray-50 text-gray-500 text-sm">
                  $
                </span>
                <input
                  type="number"
                  step="0.01"
                  required={!formData.is_free}
                  value={formData.base_price}
                  onChange={(e) => setFormData({ ...formData, base_price: e.target.value })}
                  className="flex-1 border border-gray-300 rounded-r-md px-3 py-2"
                  placeholder="99.99"
                />
              </div>
            </div>

            {/* Sale Settings */}
            <div className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center mb-4">
                <input
                  type="checkbox"
                  id="is_on_sale"
                  checked={formData.is_on_sale}
                  onChange={(e) => setFormData({ ...formData, is_on_sale: e.target.checked })}
                  className="h-4 w-4 text-blue-600 rounded"
                />
                <label htmlFor="is_on_sale" className="ml-2 text-sm font-medium text-gray-700">
                  Put this course on sale
                </label>
              </div>

              {formData.is_on_sale && (
                <div className="space-y-4 mt-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Sale Price *
                    </label>
                    <div className="flex">
                      <span className="inline-flex items-center px-3 rounded-l-md border border-r-0 border-gray-300 bg-gray-50 text-gray-500 text-sm">
                        $
                      </span>
                      <input
                        type="number"
                        step="0.01"
                        required={formData.is_on_sale}
                        value={formData.sale_price}
                        onChange={(e) => setFormData({ ...formData, sale_price: e.target.value })}
                        className="flex-1 border border-gray-300 rounded-r-md px-3 py-2"
                        placeholder="79.99"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Sale Start Date
                      </label>
                      <input
                        type="date"
                        value={formData.sale_start_date}
                        onChange={(e) => setFormData({ ...formData, sale_start_date: e.target.value })}
                        className="w-full border border-gray-300 rounded-md px-3 py-2"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Sale End Date
                      </label>
                      <input
                        type="date"
                        value={formData.sale_end_date}
                        onChange={(e) => setFormData({ ...formData, sale_end_date: e.target.value })}
                        className="w-full border border-gray-300 rounded-md px-3 py-2"
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Revenue Split */}
            <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
              <h3 className="font-medium text-gray-900 mb-3">Revenue Split</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Instructor Share (%)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.instructor_revenue_percentage}
                    onChange={(e) => {
                      const instructorPct = parseFloat(e.target.value);
                      const platformPct = 100 - instructorPct;
                      setFormData({
                        ...formData,
                        instructor_revenue_percentage: e.target.value,
                        platform_fee_percentage: platformPct.toFixed(2),
                      });
                    }}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Platform Fee (%)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={formData.platform_fee_percentage}
                    readOnly
                    className="w-full border border-gray-300 rounded-md px-3 py-2 bg-gray-100"
                  />
                </div>
              </div>
            </div>
          </>
        )}

        {/* Subscription Plans */}
        {plans.length > 0 && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Include in Subscription Plans
            </label>
            <div className="space-y-2">
              {plans.map((plan) => (
                <label key={plan.id} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.included_in_subscriptions.includes(plan.id)}
                    onChange={() => handlePlanToggle(plan.id)}
                    className="h-4 w-4 text-blue-600 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">{plan.name}</span>
                </label>
              ))}
            </div>
          </div>
        )}

        {/* Access Duration */}
        <div>
          <div className="flex items-center mb-2">
            <input
              type="checkbox"
              id="lifetime_access"
              checked={formData.lifetime_access}
              onChange={(e) => setFormData({ ...formData, lifetime_access: e.target.checked })}
              className="h-4 w-4 text-blue-600 rounded"
            />
            <label htmlFor="lifetime_access" className="ml-2 text-sm font-medium text-gray-700">
              Lifetime Access
            </label>
          </div>

          {!formData.lifetime_access && (
            <div className="mt-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Access Duration (Days)
              </label>
              <input
                type="number"
                value={formData.access_duration_days}
                onChange={(e) => setFormData({ ...formData, access_duration_days: e.target.value })}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                placeholder="365"
              />
            </div>
          )}
        </div>

        {/* Submit Button */}
        <div className="flex justify-end space-x-3 pt-4 border-t">
          <button
            type="submit"
            disabled={saving}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? 'Saving...' : pricing ? 'Update Pricing' : 'Save Pricing'}
          </button>
        </div>
      </form>
    </div>
  );
}
