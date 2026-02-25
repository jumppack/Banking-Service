"""add check constraint for positive balance

Revision ID: 2059d330d1fb
Revises: 1ae2a579ecf6
Create Date: 2026-02-25 01:00:27.011008

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2059d330d1fb'
down_revision: Union[str, Sequence[str], None] = '1ae2a579ecf6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('accounts') as batch_op:
        batch_op.create_check_constraint(
            "ck_accounts_balance_nonnegative",
            "balance >= 0"
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('accounts') as batch_op:
        batch_op.drop_constraint("ck_accounts_balance_nonnegative", type_="check")
