from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal
import secrets

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_current_active_instructor, get_current_admin
from app.models import (
    User,
    Course,
    Enrollment,
    SubscriptionPlan,
    UserSubscription,
    Payment,
    InstructorEarnings,
    InstructorPayout,
    CoursePricing,
    PaymentStatus,
    PayoutStatus
)
from app.schemas.monetization import (
    SubscriptionPlanCreate,
    SubscriptionPlanUpdate,
    SubscriptionPlanResponse,
    UserSubscriptionCreate,
    UserSubscriptionResponse,
    SubscriptionCancelRequest,
    PaymentCreate,
    PaymentResponse,
    PaymentIntentResponse,
    RefundRequest,
    CoursePricingCreate,
    CoursePricingUpdate,
    CoursePricingResponse,
    InstructorEarningsResponse,
    EarningsSummary,
    PayoutRequest,
    PayoutUpdate,
    InstructorPayoutResponse,
    CheckoutRequest,
    CheckoutResponse
)

router = APIRouter(prefix="/monetization", tags=["monetization"])


# ==================== SUBSCRIPTION PLANS ====================

@router.get('/plans', response_model=List[SubscriptionPlanResponse])
async def get_subscription_plans(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Get all subscription plans"""
    query = select(SubscriptionPlan)
    if active_only:
        query = query.where(SubscriptionPlan.is_active == True)
    query = query.order_by(SubscriptionPlan.display_order)
    
    result = await db.execute(query)
    plans = result.scalars().all()
    return plans


@router.post('/plans', response_model=SubscriptionPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription_plan(
    plan_data: SubscriptionPlanCreate,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new subscription plan (admin only)"""
    
    # Check if slug already exists
    result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.slug == plan_data.slug))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Plan slug already exists")
    
    new_plan = SubscriptionPlan(**plan_data.dict())
    db.add(new_plan)
    await db.commit()
    await db.refresh(new_plan)
    
    return new_plan


@router.put('/plans/{plan_id}', response_model=SubscriptionPlanResponse)
async def update_subscription_plan(
    plan_id: UUID,
    plan_data: SubscriptionPlanUpdate,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update a subscription plan (admin only)"""
    
    result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id))
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    
    update_data = plan_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(plan, field, value)
    
    await db.commit()
    await db.refresh(plan)
    
    return plan


# ==================== USER SUBSCRIPTIONS ====================

@router.post('/subscribe', response_model=UserSubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def subscribe_to_plan(
    subscription_data: UserSubscriptionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Subscribe to a plan"""
    
    # Check if plan exists
    result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == subscription_data.plan_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    
    # Check if user already has an active subscription
    result = await db.execute(
        select(UserSubscription).where(
            and_(UserSubscription.user_id == current_user.id, UserSubscription.is_active == True)
        )
    )
    existing_sub = result.scalar_one_or_none()
    if existing_sub:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already have an active subscription")
    
    # Calculate billing dates
    start_date = datetime.utcnow()
    if subscription_data.billing_cycle == "monthly":
        next_billing = start_date + timedelta(days=30)
        price = plan.price_monthly
    else:  # yearly
        next_billing = start_date + timedelta(days=365)
        price = plan.price_yearly or (plan.price_monthly * 12)
    
    # Create subscription
    new_subscription = UserSubscription(
        user_id=current_user.id,
        plan_id=subscription_data.plan_id,
        billing_cycle=subscription_data.billing_cycle,
        start_date=start_date,
        next_billing_date=next_billing,
        is_active=True
    )
    
    db.add(new_subscription)
    
    # Create payment record
    transaction_id = f"SUB-{secrets.token_hex(8).upper()}"
    new_payment = Payment(
        user_id=current_user.id,
        amount=price,
        status=PaymentStatus.COMPLETED,
        payment_method="stripe",
        subscription_id=new_subscription.id,
        transaction_id=transaction_id,
        description=f"Subscription to {plan.name} - {subscription_data.billing_cycle}"
    )
    
    db.add(new_payment)
    await db.commit()
    await db.refresh(new_subscription)
    
    return new_subscription


@router.get('/my-subscription', response_model=Optional[UserSubscriptionResponse])
async def get_my_subscription(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's subscription"""
    
    result = await db.execute(
        select(UserSubscription).where(
            and_(UserSubscription.user_id == current_user.id, UserSubscription.is_active == True)
        )
    )
    subscription = result.scalar_one_or_none()
    
    return subscription


@router.post('/cancel-subscription')
async def cancel_subscription(
    cancel_data: SubscriptionCancelRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel current subscription"""
    
    result = await db.execute(
        select(UserSubscription).where(
            and_(UserSubscription.user_id == current_user.id, UserSubscription.is_active == True)
        )
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active subscription found")
    
    subscription.is_cancelled = True
    subscription.cancelled_at = datetime.utcnow()
    subscription.auto_renew = False
    
    await db.commit()
    
    return {"message": "Subscription cancelled successfully", "ends_at": subscription.end_date or subscription.next_billing_date}


# ==================== PAYMENTS ====================

@router.post('/checkout', response_model=CheckoutResponse)
async def checkout(
    checkout_data: CheckoutRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Process checkout for course or subscription"""
    
    total_amount = Decimal("0.00")
    payment_description = ""
    
    if checkout_data.course_id:
        # Course purchase
        result = await db.execute(
            select(Course, CoursePricing).join(CoursePricing).where(Course.id == checkout_data.course_id)
        )
        row = result.one_or_none()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course or pricing not found")
        
        course, pricing = row
        
        if pricing.is_free:
            # Auto-enroll for free courses
            enrollment = Enrollment(
                user_id=current_user.id,
                course_id=course.id,
                enrolled_at=datetime.utcnow()
            )
            db.add(enrollment)
            await db.commit()
            
            return CheckoutResponse(
                total_amount=Decimal("0.00"),
                currency="USD",
                success=True,
                message="Enrolled successfully in free course"
            )
        
        # Calculate price
        if pricing.is_on_sale and pricing.sale_price:
            total_amount = pricing.sale_price
        else:
            total_amount = pricing.base_price
        
        payment_description = f"Purchase of course: {course.title}"
    
    elif checkout_data.subscription_plan_id:
        # Subscription purchase
        result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == checkout_data.subscription_plan_id))
        plan = result.scalar_one_or_none()
        if not plan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription plan not found")
        
        if checkout_data.billing_cycle == "monthly":
            total_amount = plan.price_monthly
        else:
            total_amount = plan.price_yearly or (plan.price_monthly * 12)
        
        payment_description = f"Subscription to {plan.name} - {checkout_data.billing_cycle}"
    
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Must provide course_id or subscription_plan_id")
    
    # Create payment record
    transaction_id = f"PAY-{secrets.token_hex(8).upper()}"
    new_payment = Payment(
        user_id=current_user.id,
        amount=total_amount,
        status=PaymentStatus.PENDING,
        payment_method=checkout_data.payment_method,
        course_id=checkout_data.course_id,
        transaction_id=transaction_id,
        description=payment_description
    )
    
    db.add(new_payment)
    await db.commit()
    await db.refresh(new_payment)
    
    # In a real app, you'd create a Stripe PaymentIntent here
    # For now, we'll simulate it
    client_secret = f"pi_test_{secrets.token_hex(16)}"
    
    return CheckoutResponse(
        payment_intent=PaymentIntentResponse(
            client_secret=client_secret,
            payment_id=new_payment.id
        ),
        total_amount=total_amount,
        currency="USD",
        success=True,
        message="Payment initiated successfully"
    )


@router.post('/payments/{payment_id}/complete', response_model=PaymentResponse)
async def complete_payment(
    payment_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark payment as completed (webhook simulation)"""
    
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    
    if payment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    payment.status = PaymentStatus.COMPLETED
    
    # If course purchase, create enrollment
    if payment.course_id:
        # Get pricing to calculate instructor share
        result = await db.execute(select(CoursePricing).where(CoursePricing.course_id == payment.course_id))
        pricing = result.scalar_one_or_none()
        
        if pricing:
            instructor_share = (payment.amount * pricing.instructor_revenue_percentage) / 100
            platform_fee = (payment.amount * pricing.platform_fee_percentage) / 100
            
            payment.instructor_share = instructor_share
            payment.platform_fee = platform_fee
            
            # Get course to find instructor
            result = await db.execute(select(Course).where(Course.id == payment.course_id))
            course = result.scalar_one()
            
            # Create instructor earnings record
            earnings = InstructorEarnings(
                instructor_id=course.created_by,
                payment_id=payment.id,
                course_id=payment.course_id,
                gross_amount=payment.amount,
                platform_fee_percentage=pricing.platform_fee_percentage,
                platform_fee_amount=platform_fee,
                net_amount=instructor_share
            )
            db.add(earnings)
        
        # Create enrollment
        enrollment = Enrollment(
            user_id=current_user.id,
            course_id=payment.course_id,
            enrolled_at=datetime.utcnow()
        )
        db.add(enrollment)
    
    await db.commit()
    await db.refresh(payment)
    
    return payment


@router.get('/payments/my', response_model=List[PaymentResponse])
async def get_my_payments(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's payment history"""
    
    result = await db.execute(
        select(Payment).where(Payment.user_id == current_user.id).order_by(Payment.created_at.desc())
    )
    payments = result.scalars().all()
    
    return payments


# ==================== COURSE PRICING ====================

@router.post('/course-pricing', response_model=CoursePricingResponse, status_code=status.HTTP_201_CREATED)
async def create_course_pricing(
    pricing_data: CoursePricingCreate,
    current_user: User = Depends(get_current_active_instructor),
    db: AsyncSession = Depends(get_db)
):
    """Create pricing for a course (instructor only)"""
    
    # Check if instructor owns the course
    result = await db.execute(select(Course).where(Course.id == pricing_data.course_id))
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    if course.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    # Check if pricing already exists
    result = await db.execute(select(CoursePricing).where(CoursePricing.course_id == pricing_data.course_id))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pricing already exists for this course")
    
    new_pricing = CoursePricing(**pricing_data.dict())
    db.add(new_pricing)
    await db.commit()
    await db.refresh(new_pricing)
    
    return new_pricing


@router.put('/course-pricing/{pricing_id}', response_model=CoursePricingResponse)
async def update_course_pricing(
    pricing_id: UUID,
    pricing_data: CoursePricingUpdate,
    current_user: User = Depends(get_current_active_instructor),
    db: AsyncSession = Depends(get_db)
):
    """Update course pricing (instructor only)"""
    
    result = await db.execute(select(CoursePricing, Course).join(Course).where(CoursePricing.id == pricing_id))
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pricing not found")
    
    pricing, course = row
    if course.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    update_data = pricing_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pricing, field, value)
    
    await db.commit()
    await db.refresh(pricing)
    
    return pricing


@router.get('/course-pricing/course/{course_id}', response_model=Optional[CoursePricingResponse])
async def get_course_pricing(
    course_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get pricing for a course"""
    
    result = await db.execute(select(CoursePricing).where(CoursePricing.course_id == course_id))
    pricing = result.scalar_one_or_none()
    
    return pricing


# ==================== INSTRUCTOR EARNINGS & PAYOUTS ====================

@router.get('/instructor/earnings', response_model=List[InstructorEarningsResponse])
async def get_instructor_earnings(
    current_user: User = Depends(get_current_active_instructor),
    db: AsyncSession = Depends(get_db)
):
    """Get instructor's earnings"""
    
    result = await db.execute(
        select(InstructorEarnings).where(InstructorEarnings.instructor_id == current_user.id).order_by(InstructorEarnings.earned_at.desc())
    )
    earnings = result.scalars().all()
    
    return earnings


@router.get('/instructor/earnings/summary', response_model=EarningsSummary)
async def get_earnings_summary(
    current_user: User = Depends(get_current_active_instructor),
    db: AsyncSession = Depends(get_db)
):
    """Get instructor's earnings summary"""
    
    result = await db.execute(
        select(
            func.sum(InstructorEarnings.net_amount).label('total'),
            func.sum(func.case((InstructorEarnings.is_paid_out == True, InstructorEarnings.net_amount), else_=0)).label('paid'),
            func.count(InstructorEarnings.id).label('count')
        ).where(InstructorEarnings.instructor_id == current_user.id)
    )
    row = result.one()
    
    total = row.total or Decimal("0.00")
    paid = row.paid or Decimal("0.00")
    pending = total - paid
    
    return EarningsSummary(
        total_earnings=total,
        paid_out=paid,
        pending=pending,
        total_sales=row.count,
        currency="USD"
    )


@router.post('/instructor/request-payout', response_model=InstructorPayoutResponse, status_code=status.HTTP_201_CREATED)
async def request_payout(
    payout_data: PayoutRequest,
    current_user: User = Depends(get_current_active_instructor),
    db: AsyncSession = Depends(get_db)
):
    """Request a payout (instructor only)"""
    
    # Check available balance
    result = await db.execute(
        select(func.sum(InstructorEarnings.net_amount)).where(
            and_(
                InstructorEarnings.instructor_id == current_user.id,
                InstructorEarnings.is_paid_out == False
            )
        )
    )
    available_balance = result.scalar() or Decimal("0.00")
    
    if payout_data.amount > available_balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Requested amount exceeds available balance of ${available_balance}"
        )
    
    # Create payout request
    new_payout = InstructorPayout(
        instructor_id=current_user.id,
        amount=payout_data.amount,
        payout_method=payout_data.payout_method,
        payout_details=payout_data.payout_details,
        status=PayoutStatus.PENDING
    )
    
    db.add(new_payout)
    await db.commit()
    await db.refresh(new_payout)
    
    return new_payout


@router.get('/instructor/payouts', response_model=List[InstructorPayoutResponse])
async def get_instructor_payouts(
    current_user: User = Depends(get_current_active_instructor),
    db: AsyncSession = Depends(get_db)
):
    """Get instructor's payout history"""
    
    result = await db.execute(
        select(InstructorPayout).where(InstructorPayout.instructor_id == current_user.id).order_by(InstructorPayout.requested_at.desc())
    )
    payouts = result.scalars().all()
    
    return payouts
