"""add indexes to jobs table

Revision ID: 39f74ce1e016
Revises: ea42c506280a
Create Date: 2026-06-02 10:43:43.782995

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '39f74ce1e016'
down_revision: Union[str, Sequence[str], None] = 'ea42c506280a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('ix_jobs_client_id', 'jobs', ['client_id'], unique=False)
    op.create_index('ix_jobs_status', 'jobs', ['status'], unique=False)

def downgrade() -> None:
    op.drop_index('ix_jobs_status', table_name='jobs')
    op.drop_index('ix_jobs_client_id', table_name='jobs')
