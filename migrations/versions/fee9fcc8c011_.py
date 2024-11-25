"""empty message

Revision ID: fee9fcc8c011
Revises: 719fca2ff741
Create Date: 2024-11-25 19:08:38.124896

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fee9fcc8c011'
down_revision: Union[str, None] = '719fca2ff741'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('TaskTable',
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('time_limit', sa.Float(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('input_info', sa.String(), nullable=False),
    sa.Column('output_info', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.PrimaryKeyConstraint('task_id')
    )
    op.create_table('TestTable',
    sa.Column('test_id', sa.Integer(), nullable=False),
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.Column('input_data', sa.String(), nullable=False),
    sa.Column('output_data', sa.String(), nullable=False),
    sa.Column('is_open', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.ForeignKeyConstraint(['task_id'], ['TaskTable.task_id'], ),
    sa.PrimaryKeyConstraint('test_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('TestTable')
    op.drop_table('TaskTable')
    # ### end Alembic commands ###
