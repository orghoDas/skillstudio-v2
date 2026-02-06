import { getAuthToken } from './auth';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Types
export interface SubscriptionPlan {
  id: string;
  name: string;
  slug: string;
  description?: string;
  price_monthly: number;
  price_yearly?: number;
  max_courses_access?: number;
  max_certificates?: number;
  has_ai_features: boolean;
  has_certificate_downloads: boolean;
  has_priority_support: boolean;
  has_offline_access: boolean;
  discount_percentage: number;
  features: Record<string, any>;
  is_active: boolean;
  display_order: number;
  created_at: string;
  updated_at: string;
}

export interface UserSubscription {
  id: string;
  user_id: string;
  plan_id: string;
  billing_cycle: 'monthly' | 'yearly';
  start_date: string;
  end_date?: string;
  next_billing_date?: string;
  is_active: boolean;
  is_cancelled: boolean;
  cancelled_at?: string;
  stripe_subscription_id?: string;
  stripe_customer_id?: string;
  auto_renew: boolean;
  trial_end_date?: string;
  created_at: string;
  updated_at: string;
  plan?: SubscriptionPlan;
}

export interface Payment {
  id: string;
  user_id: string;
  amount: number;
  currency: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'refunded' | 'cancelled';
  payment_method: 'credit_card' | 'debit_card' | 'paypal' | 'stripe' | 'bank_transfer';
  course_id?: string;
  subscription_id?: string;
  stripe_payment_intent_id?: string;
  stripe_charge_id?: string;
  paypal_order_id?: string;
  transaction_id: string;
  description?: string;
  receipt_url?: string;
  instructor_share?: number;
  platform_fee?: number;
  payment_metadata: Record<string, any>;
  refund_amount?: number;
  refund_reason?: string;
  refunded_at?: string;
  created_at: string;
  updated_at: string;
}

export interface CoursePricing {
  id: string;
  course_id: string;
  base_price: number;
  currency: string;
  is_on_sale: boolean;
  sale_price?: number;
  sale_start_date?: string;
  sale_end_date?: string;
  is_free: boolean;
  instructor_revenue_percentage: number;
  platform_fee_percentage: number;
  included_in_subscriptions: string[];
  lifetime_access: boolean;
  access_duration_days?: number;
  created_at: string;
  updated_at: string;
}

export interface InstructorEarnings {
  id: string;
  instructor_id: string;
  payment_id?: string;
  course_id?: string;
  gross_amount: number;
  platform_fee_percentage: number;
  platform_fee_amount: number;
  net_amount: number;
  currency: string;
  is_paid_out: boolean;
  payout_id?: string;
  earned_at: string;
  paid_out_at?: string;
  created_at: string;
}

export interface EarningsSummary {
  total_earnings: number;
  paid_out: number;
  pending: number;
  total_sales: number;
  currency: string;
}

export interface InstructorPayout {
  id: string;
  instructor_id: string;
  amount: number;
  currency: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  payout_method: string;
  payout_details: Record<string, any>;
  stripe_transfer_id?: string;
  paypal_payout_id?: string;
  transaction_reference?: string;
  processing_fee?: number;
  net_payout?: number;
  requested_at: string;
  processed_at?: string;
  completed_at?: string;
  failed_reason?: string;
  admin_notes?: string;
  created_at: string;
  updated_at: string;
}

export interface CheckoutRequest {
  item_type: 'course' | 'subscription';
  item_id: string;
  billing_cycle?: 'monthly' | 'yearly';
  payment_method: 'credit_card' | 'debit_card' | 'paypal' | 'stripe' | 'bank_transfer';
  return_url?: string;
  cancel_url?: string;
}

export interface CheckoutResponse {
  payment: Payment;
  client_secret?: string;
  redirect_url?: string;
  message: string;
}

// API Functions

// Subscription Plans
export async function getSubscriptionPlans(): Promise<SubscriptionPlan[]> {
  const response = await fetch(`${API_BASE_URL}/api/monetization/plans`);
  if (!response.ok) {
    throw new Error('Failed to fetch subscription plans');
  }
  return response.json();
}

export async function createSubscriptionPlan(data: Partial<SubscriptionPlan>): Promise<SubscriptionPlan> {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/api/monetization/plans`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error('Failed to create subscription plan');
  }
  return response.json();
}

// User Subscriptions
export async function subscribeToplan(planId: string, billingCycle: 'monthly' | 'yearly'): Promise<UserSubscription> {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/api/monetization/subscribe`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ plan_id: planId, billing_cycle: billingCycle }),
  });
  if (!response.ok) {
    throw new Error('Failed to subscribe to plan');
  }
  return response.json();
}

export async function getMySubscription(): Promise<UserSubscription | null> {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/api/monetization/my-subscription`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    throw new Error('Failed to fetch subscription');
  }
  return response.json();
}

export async function cancelSubscription(): Promise<UserSubscription> {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/api/monetization/cancel-subscription`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  if (!response.ok) {
    throw new Error('Failed to cancel subscription');
  }
  return response.json();
}

// Payments
export async function createCheckout(data: CheckoutRequest): Promise<CheckoutResponse> {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/api/monetization/checkout`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error('Failed to create checkout');
  }
  return response.json();
}

export async function completePayment(paymentId: string, paymentIntentId?: string): Promise<Payment> {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/api/monetization/payments/${paymentId}/complete`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ payment_intent_id: paymentIntentId }),
  });
  if (!response.ok) {
    throw new Error('Failed to complete payment');
  }
  return response.json();
}

export async function getMyPayments(): Promise<Payment[]> {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/api/monetization/payments/my`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  if (!response.ok) {
    throw new Error('Failed to fetch payments');
  }
  return response.json();
}

// Course Pricing
export async function createCoursePricing(data: Partial<CoursePricing>): Promise<CoursePricing> {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/api/monetization/course-pricing`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error('Failed to create course pricing');
  }
  return response.json();
}

export async function updateCoursePricing(pricingId: string, data: Partial<CoursePricing>): Promise<CoursePricing> {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/api/monetization/course-pricing/${pricingId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error('Failed to update course pricing');
  }
  return response.json();
}

export async function getCoursePricing(courseId: string): Promise<CoursePricing | null> {
  const response = await fetch(`${API_BASE_URL}/api/monetization/course-pricing/course/${courseId}`);
  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    throw new Error('Failed to fetch course pricing');
  }
  return response.json();
}

// Instructor Earnings
export async function getInstructorEarnings(): Promise<InstructorEarnings[]> {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/api/monetization/instructor/earnings`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  if (!response.ok) {
    throw new Error('Failed to fetch earnings');
  }
  return response.json();
}

export async function getEarningsSummary(): Promise<EarningsSummary> {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/api/monetization/instructor/earnings/summary`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  if (!response.ok) {
    throw new Error('Failed to fetch earnings summary');
  }
  return response.json();
}

// Instructor Payouts
export async function requestPayout(amount: number, payoutMethod: string, payoutDetails: Record<string, any>): Promise<InstructorPayout> {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/api/monetization/instructor/request-payout`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({
      amount,
      payout_method: payoutMethod,
      payout_details: payoutDetails,
    }),
  });
  if (!response.ok) {
    throw new Error('Failed to request payout');
  }
  return response.json();
}

export async function getInstructorPayouts(): Promise<InstructorPayout[]> {
  const token = getAuthToken();
  const response = await fetch(`${API_BASE_URL}/api/monetization/instructor/payouts`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  if (!response.ok) {
    throw new Error('Failed to fetch payouts');
  }
  return response.json();
}
