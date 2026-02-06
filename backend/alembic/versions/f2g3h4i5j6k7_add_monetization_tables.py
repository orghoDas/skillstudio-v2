"""add_monetization_tables

Revision ID: f2g3h4i5j6k7
Revises: e1f2g3h4i5j6
Create Date: 2026-02-06 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f2g3h4i5j6k7'
down_revision = 'e1f2g3h4i5j6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enums
    op.execute("CREATE TYPE payment_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'refunded', 'cancelled')")
    op.execute("CREATE TYPE payment_method AS ENUM ('credit_card', 'debit_card', 'paypal', 'stripe', 'bank_transfer')")
    op.execute("CREATE TYPE payout_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'cancelled')")
    
    # Create subscription_plans table
    op.create_table('subscription_plans',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price_monthly', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('price_yearly', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('max_courses_access', sa.Integer(), nullable=True),
        sa.Column('max_certificates', sa.Integer(), nullable=True),
        sa.Column('has_ai_features', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('has_certificate_downloads', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('has_priority_support', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('has_offline_access', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('discount_percentage', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('features', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('display_order', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug')
    )
    
    # Create user_subscriptions table
    op.create_table('user_subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('plan_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('billing_cycle', sa.String(length=20), nullable=False),
        sa.Column('start_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_billing_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_cancelled', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_customer_id', sa.String(length=255), nullable=True),
        sa.Column('auto_renew', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('trial_end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['plan_id'], ['subscription_plans.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stripe_subscription_id')
    )
    op.create_index('ix_user_subscriptions_user_id', 'user_subscriptions', ['user_id'])
    
    # Create payments table
    op.create_table('payments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='USD'),
        sa.Column('status', sa.Enum('pending', 'processing', 'completed', 'failed', 'refunded', 'cancelled', name='payment_status'), nullable=False, server_default='pending'),
        sa.Column('payment_method', sa.Enum('credit_card', 'debit_card', 'paypal', 'stripe', 'bank_transfer', name='payment_method'), nullable=False),
        sa.Column('course_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('subscription_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('stripe_payment_intent_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_charge_id', sa.String(length=255), nullable=True),
        sa.Column('paypal_order_id', sa.String(length=255), nullable=True),
        sa.Column('transaction_id', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('receipt_url', sa.String(length=512), nullable=True),
        sa.Column('instructor_share', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('platform_fee', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('payment_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('refund_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('refund_reason', sa.Text(), nullable=True),
        sa.Column('refunded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['subscription_id'], ['user_subscriptions.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('transaction_id'),
        sa.UniqueConstraint('stripe_payment_intent_id')
    )
    op.create_index('ix_payments_user_id', 'payments', ['user_id'])
    op.create_index('ix_payments_status', 'payments', ['status'])
    
    # Create course_pricing table
    op.create_table('course_pricing',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('course_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('base_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='USD'),
        sa.Column('is_on_sale', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('sale_price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('sale_start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sale_end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_free', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('instructor_revenue_percentage', sa.Numeric(precision=5, scale=2), nullable=True, server_default='80.00'),
        sa.Column('platform_fee_percentage', sa.Numeric(precision=5, scale=2), nullable=True, server_default='20.00'),
        sa.Column('included_in_subscriptions', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('lifetime_access', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('access_duration_days', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('course_id')
    )
    
    # Create instructor_payouts table (must be created before instructor_earnings)
    op.create_table('instructor_payouts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('instructor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='USD'),
        sa.Column('status', sa.Enum('pending', 'processing', 'completed', 'failed', 'cancelled', name='payout_status'), nullable=False, server_default='pending'),
        sa.Column('payout_method', sa.String(length=50), nullable=False),
        sa.Column('payout_details', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('stripe_transfer_id', sa.String(length=255), nullable=True),
        sa.Column('paypal_payout_id', sa.String(length=255), nullable=True),
        sa.Column('transaction_reference', sa.String(length=100), nullable=True),
        sa.Column('processing_fee', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('net_payout', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('requested_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_reason', sa.Text(), nullable=True),
        sa.Column('admin_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['instructor_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_instructor_payouts_instructor_id', 'instructor_payouts', ['instructor_id'])
    op.create_index('ix_instructor_payouts_status', 'instructor_payouts', ['status'])
    
    # Create instructor_earnings table
    op.create_table('instructor_earnings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('instructor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('payment_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('course_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('gross_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('platform_fee_percentage', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('platform_fee_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('net_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='USD'),
        sa.Column('is_paid_out', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('payout_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('earned_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('paid_out_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['instructor_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['payment_id'], ['payments.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['payout_id'], ['instructor_payouts.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_instructor_earnings_instructor_id', 'instructor_earnings', ['instructor_id'])
    op.create_index('ix_instructor_earnings_is_paid_out', 'instructor_earnings', ['is_paid_out'])


def downgrade() -> None:
    op.drop_index('ix_instructor_earnings_is_paid_out', table_name='instructor_earnings')
    op.drop_index('ix_instructor_earnings_instructor_id', table_name='instructor_earnings')
    op.drop_table('instructor_earnings')
    
    op.drop_index('ix_instructor_payouts_status', table_name='instructor_payouts')
    op.drop_index('ix_instructor_payouts_instructor_id', table_name='instructor_payouts')
    op.drop_table('instructor_payouts')
    
    op.drop_table('course_pricing')
    
    op.drop_index('ix_payments_status', table_name='payments')
    op.drop_index('ix_payments_user_id', table_name='payments')
    op.drop_table('payments')
    
    op.drop_index('ix_user_subscriptions_user_id', table_name='user_subscriptions')
    op.drop_table('user_subscriptions')
    
    op.drop_table('subscription_plans')
    
    op.execute('DROP TYPE payout_status')
    op.execute('DROP TYPE payment_method')
    op.execute('DROP TYPE payment_status')
