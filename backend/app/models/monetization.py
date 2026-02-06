from sqlalchemy import Column, DateTime, Integer, String, Text, Boolean, ForeignKey, Enum as SQEnum, Numeric, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from app.core.database import Base


class PaymentStatus(str, enum.Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentMethod(str, enum.Enum):
    """Payment method enumeration"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    BANK_TRANSFER = "bank_transfer"


class SubscriptionPlan(Base):
    """Subscription plan model - defines pricing tiers"""

    __tablename__ = "subscription_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Plan details
    name = Column(String(100), nullable=False, unique=True)  # e.g., "Free", "Pro", "Premium"
    slug = Column(String(50), nullable=False, unique=True)  # e.g., "free", "pro", "premium"
    description = Column(Text, nullable=True)
    
    # Pricing
    price_monthly = Column(Numeric(10, 2), nullable=False)  # e.g., 0.00, 9.99, 29.99
    price_yearly = Column(Numeric(10, 2), nullable=True)  # e.g., 0.00, 99.00, 299.00
    
    # Features
    max_courses_access = Column(Integer, nullable=True)  # null = unlimited
    max_certificates = Column(Integer, nullable=True)  # null = unlimited
    has_ai_features = Column(Boolean, default=False)
    has_certificate_downloads = Column(Boolean, default=True)
    has_priority_support = Column(Boolean, default=False)
    has_offline_access = Column(Boolean, default=False)
    discount_percentage = Column(Integer, default=0)  # e.g., 20 for 20% off courses
    
    # Additional features as JSON
    features = Column(JSONB, default={}, nullable=False)  # Flexible feature list
    
    # Status
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)  # For sorting in UI
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user_subscriptions = relationship("UserSubscription", back_populates="plan")

    def __repr__(self):
        return f"<SubscriptionPlan {self.name}>"


class UserSubscription(Base):
    """User subscription model - tracks user's current subscription"""

    __tablename__ = "user_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.id"), nullable=False)
    
    # Subscription period
    billing_cycle = Column(String(20), nullable=False)  # "monthly" or "yearly"
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True), nullable=True)
    next_billing_date = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_cancelled = Column(Boolean, default=False)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Payment integration
    stripe_subscription_id = Column(String(255), nullable=True, unique=True)
    stripe_customer_id = Column(String(255), nullable=True)
    
    # Tracking
    auto_renew = Column(Boolean, default=True)
    trial_end_date = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="subscription")
    plan = relationship("SubscriptionPlan", back_populates="user_subscriptions")

    def __repr__(self):
        return f"<UserSubscription {self.user_id} - {self.plan_id}>"


class Payment(Base):
    """Payment model - tracks all transactions"""

    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Payment details
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    status = Column(SQEnum(PaymentStatus, name="payment_status"), nullable=False, default=PaymentStatus.PENDING)
    payment_method = Column(SQEnum(PaymentMethod, name="payment_method"), nullable=False)
    
    # What was purchased
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="SET NULL"), nullable=True)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("user_subscriptions.id", ondelete="SET NULL"), nullable=True)
    
    # Payment gateway integration
    stripe_payment_intent_id = Column(String(255), nullable=True, unique=True)
    stripe_charge_id = Column(String(255), nullable=True)
    paypal_order_id = Column(String(255), nullable=True)
    
    # Transaction details
    transaction_id = Column(String(100), unique=True, nullable=False)  # Our internal ID
    description = Column(Text, nullable=True)
    receipt_url = Column(String(512), nullable=True)
    
    # Instructor revenue share (if course purchase)
    instructor_share = Column(Numeric(10, 2), nullable=True)  # Amount that goes to instructor
    platform_fee = Column(Numeric(10, 2), nullable=True)  # Platform commission
    
    # Metadata
    payment_metadata = Column(JSONB, default={}, nullable=False)
    
    # Refund tracking
    refund_amount = Column(Numeric(10, 2), nullable=True)
    refund_reason = Column(Text, nullable=True)
    refunded_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="payments")
    course = relationship("Course", back_populates="payments")

    def __repr__(self):
        return f"<Payment {self.transaction_id}>"


class InstructorEarnings(Base):
    """Instructor earnings model - tracks revenue for instructors"""

    __tablename__ = "instructor_earnings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instructor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id", ondelete="SET NULL"), nullable=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="SET NULL"), nullable=True)
    
    # Earnings details
    gross_amount = Column(Numeric(10, 2), nullable=False)  # Student paid
    platform_fee_percentage = Column(Numeric(5, 2), nullable=False)  # e.g., 20.00 for 20%
    platform_fee_amount = Column(Numeric(10, 2), nullable=False)
    net_amount = Column(Numeric(10, 2), nullable=False)  # What instructor gets
    
    # Currency
    currency = Column(String(3), default="USD", nullable=False)
    
    # Payout status
    is_paid_out = Column(Boolean, default=False)
    payout_id = Column(UUID(as_uuid=True), ForeignKey("instructor_payouts.id", ondelete="SET NULL"), nullable=True)
    
    # Tracking
    earned_at = Column(DateTime(timezone=True), server_default=func.now())
    paid_out_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    instructor = relationship("User", foreign_keys=[instructor_id])
    payment = relationship("Payment")
    course = relationship("Course")
    payout = relationship("InstructorPayout", back_populates="earnings")

    def __repr__(self):
        return f"<InstructorEarnings {self.instructor_id} - ${self.net_amount}>"


class PayoutStatus(str, enum.Enum):
    """Payout status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class InstructorPayout(Base):
    """Instructor payout model - tracks payout requests"""

    __tablename__ = "instructor_payouts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instructor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Payout details
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    status = Column(SQEnum(PayoutStatus, name="payout_status"), nullable=False, default=PayoutStatus.PENDING)
    
    # Payment method
    payout_method = Column(String(50), nullable=False)  # e.g., "bank_transfer", "paypal", "stripe"
    payout_details = Column(JSONB, default={}, nullable=False)  # Account details (encrypted)
    
    # Gateway integration
    stripe_transfer_id = Column(String(255), nullable=True)
    paypal_payout_id = Column(String(255), nullable=True)
    
    # Transaction tracking
    transaction_reference = Column(String(100), nullable=True)
    processing_fee = Column(Numeric(10, 2), nullable=True)
    net_payout = Column(Numeric(10, 2), nullable=True)  # After processing fees
    
    # Status tracking
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    failed_reason = Column(Text, nullable=True)
    
    # Admin notes
    admin_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    instructor = relationship("User", foreign_keys=[instructor_id])
    earnings = relationship("InstructorEarnings", back_populates="payout")

    def __repr__(self):
        return f"<InstructorPayout {self.transaction_reference}>"


class CoursePricing(Base):
    """Course pricing model - allows flexible pricing strategies"""

    __tablename__ = "course_pricing"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Pricing
    base_price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    
    # Discounts
    is_on_sale = Column(Boolean, default=False)
    sale_price = Column(Numeric(10, 2), nullable=True)
    sale_start_date = Column(DateTime(timezone=True), nullable=True)
    sale_end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Free vs Paid
    is_free = Column(Boolean, default=False)
    
    # Revenue sharing
    instructor_revenue_percentage = Column(Numeric(5, 2), default=80.00)  # e.g., 80% to instructor
    platform_fee_percentage = Column(Numeric(5, 2), default=20.00)  # e.g., 20% platform fee
    
    # Subscription access
    included_in_subscriptions = Column(JSONB, default=[], nullable=False)  # List of plan slugs
    
    # Lifetime access
    lifetime_access = Column(Boolean, default=True)
    access_duration_days = Column(Integer, nullable=True)  # null = lifetime
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    course = relationship("Course", back_populates="pricing")

    def __repr__(self):
        return f"<CoursePricing {self.course_id} - ${self.base_price}>"
