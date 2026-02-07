"""fix_score_percentage_typo

Revision ID: c4b9a5e3cc72
Revises: f8269958cf68
Create Date: 2026-02-06 21:57:54.317930

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4b9a5e3cc72'
down_revision: Union[str, None] = 'f8269958cf68'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new column as nullable first
    op.add_column('assessment_attempts', sa.Column('score_percentage', sa.Numeric(precision=5, scale=2), nullable=True))
    
    # Copy data from old misspelled column to new one
    op.execute('UPDATE assessment_attempts SET score_percentage = score_percecntage')
    
    # Now make it NOT NULL
    op.alter_column('assessment_attempts', 'score_percentage', nullable=False)
    
    # Drop the old misspelled column
    op.drop_column('assessment_attempts', 'score_percecntage')


def downgrade() -> None:
    # Add back the old misspelled column
    op.add_column('assessment_attempts', sa.Column('score_percecntage', sa.NUMERIC(precision=5, scale=2), nullable=True))
    
    # Copy data back
    op.execute('UPDATE assessment_attempts SET score_percecntage = score_percentage')
    
    # Make it NOT NULL
    op.alter_column('assessment_attempts', 'score_percecntage', nullable=False)
    
    # Drop the new column
    op.drop_column('assessment_attempts', 'score_percentage')
