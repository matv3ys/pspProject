"""empty message

Revision ID: 719fca2ff741
Revises: f571727cd51b
Create Date: 2024-11-25 18:59:06.609671

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '719fca2ff741'
down_revision: Union[str, None] = 'f571727cd51b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('GroupTable', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False,
               existing_server_default=sa.text("timezone('utc'::text, now())"))
    op.alter_column('UserTable', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False,
               existing_server_default=sa.text("timezone('utc'::text, now())"))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('UserTable', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True,
               existing_server_default=sa.text("timezone('utc'::text, now())"))
    op.alter_column('GroupTable', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True,
               existing_server_default=sa.text("timezone('utc'::text, now())"))
    # ### end Alembic commands ###