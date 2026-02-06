'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { getCoursePricing, type CoursePricing } from '@/lib/monetization-service';

interface CoursePriceDisplayProps {
  courseId: string;
  showButton?: boolean;
}

export default function CoursePriceDisplay({ courseId, showButton = true }: CoursePriceDisplayProps) {
  const router = useRouter();
  const [pricing, setPricing] = useState<CoursePricing | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPricing();
  }, [courseId]);

  async function loadPricing() {
    try {
      setLoading(true);
      const data = await getCoursePricing(courseId);
      setPricing(data);
    } catch (err) {
      console.error('Failed to load pricing:', err);
    } finally {
      setLoading(false);
    }
  }

  const getCurrentPrice = () => {
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

  const handleBuyNow = () => {
    router.push(`/dashboard/checkout?courseId=${courseId}`);
  };

  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-24"></div>
      </div>
    );
  }

  if (!pricing) {
    return null;
  }

  const currentPrice = getCurrentPrice();
  const onSale = isOnSale();

  return (
    <div className="flex items-center justify-between">
      <div>
        {pricing.is_free ? (
          <span className="text-2xl font-bold text-green-600">Free</span>
        ) : (
          <div>
            {onSale && (
              <span className="text-lg text-gray-400 line-through mr-2">
                ${pricing.base_price.toFixed(2)}
              </span>
            )}
            <span className={`text-2xl font-bold ${onSale ? 'text-green-600' : 'text-gray-900'}`}>
              ${currentPrice.toFixed(2)}
            </span>
            {onSale && (
              <span className="ml-2 bg-red-100 text-red-800 text-xs font-semibold px-2 py-1 rounded">
                Sale
              </span>
            )}
          </div>
        )}
        {pricing.included_in_subscriptions && pricing.included_in_subscriptions.length > 0 && (
          <p className="text-xs text-gray-600 mt-1">
            Included in subscription plans
          </p>
        )}
      </div>

      {showButton && (
        <button
          onClick={handleBuyNow}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
        >
          {pricing.is_free ? 'Enroll Free' : 'Buy Now'}
        </button>
      )}
    </div>
  );
}
