from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from app.models.monetization import PaymentStatus, PaymentMethod, PayoutStatus


# ==================== SUBSCRIPTION PLANS ====================

class SubscriptionPlanBase(BaseModel):
    """Base schema for subscription plans"""
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    price_monthly: Decimal = Field(..., ge=0)
    price_yearly: Optional[Decimal] = Field(None, ge=0)
    max_courses_access: Optional[int] = Field(None, ge=0)
    max_certificates: Optional[int] = Field(None, ge=0)
    has_ai_features: bool = False
    has_certificate_downloads: bool = True
    has_priority_support: bool = False
    has_offline_access: bool = False
    discount_percentage: int = Field(0, ge=0, le=100)
    features: Dict[str, Any] = {}


class SubscriptionPlanCreate(SubscriptionPlanBase):
    """Schema for creating a subscription plan"""
    pass


class SubscriptionPlanUpdate(BaseModel):
    """Schema for updating a subscription plan"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    price_monthly: Optional[Decimal] = Field(None, ge=0)
    price_yearly: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None
    features: Optional[Dict[str, Any]] = None


class SubscriptionPlanResponse(SubscriptionPlanBase):
    """Schema for subscription plan response"""
    id: UUID
    is_active: bool
    display_order: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== USER SUBSCRIPTIONS ====================

class UserSubscriptionCreate(BaseModel):
    """Schema for creating a user subscription"""
    plan_id: UUID
    billing_cycle: str = Field(..., pattern="^(monthly|yearly)$")
    stripe_payment_method_id: Optional[str] = None


class UserSubscriptionResponse(BaseModel):
    """Schema for user subscription response"""
    id: UUID
    user_id: UUID
    plan_id: UUID
    billing_cycle: str
    start_date: datetime
    end_date: Optional[datetime]
    next_billing_date: Optional[datetime]
    is_active: bool
    is_cancelled: bool
    cancelled_at: Optional[datetime]
    auto_renew: bool
    trial_end_date: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class SubscriptionCancelRequest(BaseModel):
    """Schema for cancelling a subscription"""
    reason: Optional[str] = None


# ==================== PAYMENTS ====================

class PaymentCreate(BaseModel):
    """Schema for creating a payment"""
    amount: Decimal = Field(..., gt=0)
    currency: str = Field("USD", min_length=3, max_length=3)
    payment_method: PaymentMethod
    course_id: Optional[UUID] = None
    subscription_id: Optional[UUID] = None
    stripe_payment_method_id: Optional[str] = None
    description: Optional[str] = None


class PaymentResponse(BaseModel):
    """Schema for payment response"""
    id: UUID
    user_id: UUID
    amount: Decimal
    currency: str
    status: PaymentStatus
    payment_method: PaymentMethod
    course_id: Optional[UUID]
    subscription_id: Optional[UUID]
    transaction_id: str
    description: Optional[str]
    receipt_url: Optional[str]
    instructor_share: Optional[Decimal]
    platform_fee: Optional[Decimal]
    refund_amount: Optional[Decimal]
    refund_reason: Optional[str]
    refunded_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PaymentIntentResponse(BaseModel):
    """Schema for Stripe payment intent"""
    client_secret: str
    payment_id: UUID


class RefundRequest(BaseModel):
    """Schema for refund request"""
    reason: str = Field(..., min_length=10)
    amount: Optional[Decimal] = Field(None, gt=0)


# ==================== COURSE PRICING ====================

class CoursePricingBase(BaseModel):
    """Base schema for course pricing"""
    base_price: Decimal = Field(..., ge=0)
    currency: str = Field("USD", min_length=3, max_length=3)
    is_free: bool = False
    is_on_sale: bool = False
    sale_price: Optional[Decimal] = Field(None, ge=0)
    sale_start_date: Optional[datetime] = None
    sale_end_date: Optional[datetime] = None
    instructor_revenue_percentage: Decimal = Field(80.00, ge=0, le=100)
    platform_fee_percentage: Decimal = Field(20.00, ge=0, le=100)
    included_in_subscriptions: List[str] = []
    lifetime_access: bool = True
    access_duration_days: Optional[int] = Field(None, gt=0)


class CoursePricingCreate(CoursePricingBase):
    """Schema for creating course pricing"""
    course_id: UUID


class CoursePricingUpdate(BaseModel):
    """Schema for updating course pricing"""
    base_price: Optional[Decimal] = Field(None, ge=0)
    is_free: Optional[bool] = None
    is_on_sale: Optional[bool] = None
    sale_price: Optional[Decimal] = Field(None, ge=0)
    sale_start_date: Optional[datetime] = None
    sale_end_date: Optional[datetime] = None
    included_in_subscriptions: Optional[List[str]] = None


class CoursePricingResponse(CoursePricingBase):
    """Schema for course pricing response"""
    id: UUID
    course_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== INSTRUCTOR EARNINGS ====================

class InstructorEarningsResponse(BaseModel):
    """Schema for instructor earnings response"""
    id: UUID
    instructor_id: UUID
    payment_id: Optional[UUID]
    course_id: Optional[UUID]
    gross_amount: Decimal
    platform_fee_percentage: Decimal
    platform_fee_amount: Decimal
    net_amount: Decimal
    currency: str
    is_paid_out: bool
    payout_id: Optional[UUID]
    earned_at: datetime
    paid_out_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class EarningsSummary(BaseModel):
    """Summary of instructor earnings"""
    total_earnings: Decimal
    paid_out: Decimal
    pending: Decimal
    total_sales: int
    currency: str


# ==================== INSTRUCTOR PAYOUTS ====================

class PayoutRequest(BaseModel):
    """Schema for requesting a payout"""
    amount: Decimal = Field(..., gt=0)
    payout_method: str = Field(..., pattern="^(bank_transfer|paypal|stripe)$")
    payout_details: Dict[str, Any] = {}


class PayoutUpdate(BaseModel):
    """Schema for updating payout status (admin only)"""
    status: PayoutStatus
    transaction_reference: Optional[str] = None
    processing_fee: Optional[Decimal] = None
    failed_reason: Optional[str] = None
    admin_notes: Optional[str] = None


class InstructorPayoutResponse(BaseModel):
    """Schema for instructor payout response"""
    id: UUID
    instructor_id: UUID
    amount: Decimal
    currency: str
    status: PayoutStatus
    payout_method: str
    transaction_reference: Optional[str]
    processing_fee: Optional[Decimal]
    net_payout: Optional[Decimal]
    requested_at: datetime
    processed_at: Optional[datetime]
    completed_at: Optional[datetime]
    failed_reason: Optional[str]
    
    class Config:
        from_attributes = True


# ==================== CHECKOUT ====================

class CheckoutRequest(BaseModel):
    """Schema for checkout request"""
    course_id: Optional[UUID] = None
    subscription_plan_id: Optional[UUID] = None
    billing_cycle: Optional[str] = Field(None, pattern="^(monthly|yearly)$")
    payment_method: PaymentMethod = PaymentMethod.STRIPE
    
    @validator('billing_cycle')
    def validate_billing_cycle(cls, v, values):
        if values.get('subscription_plan_id') and not v:
            raise ValueError('billing_cycle is required for subscription purchases')
        return v


class CheckoutResponse(BaseModel):
    """Schema for checkout response"""
    payment_intent: Optional[PaymentIntentResponse] = None
    subscription: Optional[UserSubscriptionResponse] = None
    total_amount: Decimal
    currency: str
    success: bool
    message: str
