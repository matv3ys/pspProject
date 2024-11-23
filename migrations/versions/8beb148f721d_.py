"""empty message

Revision ID: 8beb148f721d
Revises: 9f76eab531be
Create Date: 2024-11-24 01:55:53.312918

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8beb148f721d'
down_revision: Union[str, None] = '9f76eab531be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('GroupTable', 'owner_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('UserGroupTable', 'status',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('UserGroupTable', 'status',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('GroupTable', 'owner_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
