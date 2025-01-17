"""empty message

Revision ID: f571727cd51b
Revises: 8beb148f721d
Create Date: 2024-11-25 18:57:58.876694

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f571727cd51b'
down_revision: Union[str, None] = '8beb148f721d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('GroupTable', sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=True))
    op.alter_column('UserTable', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True,
               existing_server_default=sa.text("timezone('utc'::text, now())"))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('UserTable', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False,
               existing_server_default=sa.text("timezone('utc'::text, now())"))
    op.drop_column('GroupTable', 'created_at')
    # ### end Alembic commands ###
