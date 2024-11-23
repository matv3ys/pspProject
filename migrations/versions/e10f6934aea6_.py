"""empty message

Revision ID: e10f6934aea6
Revises: d9dfa8c2fbc5
Create Date: 2024-11-23 20:47:39.235561

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e10f6934aea6'
down_revision: Union[str, None] = 'd9dfa8c2fbc5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('UserTable', sa.Column('is_organizer', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('UserTable', 'is_organizer')
    # ### end Alembic commands ###