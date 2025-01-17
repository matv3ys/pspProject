"""empty message

Revision ID: df7f97b8b727
Revises: 70f67df9c9f5
Create Date: 2024-11-29 19:15:27.350945

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df7f97b8b727'
down_revision: Union[str, None] = '70f67df9c9f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ContestTable',
    sa.Column('contest_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.Column('end_time', sa.DateTime(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['UserTable.user_id'], ),
    sa.PrimaryKeyConstraint('contest_id')
    )
    op.create_table('ContestTaskTable',
    sa.Column('contest_id', sa.Integer(), nullable=False),
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.Column('num', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['contest_id'], ['ContestTable.contest_id'], ),
    sa.ForeignKeyConstraint(['task_id'], ['TaskTable.task_id'], ),
    sa.PrimaryKeyConstraint('contest_id', 'task_id'),
    sa.UniqueConstraint('num')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ContestTaskTable')
    op.drop_table('ContestTable')
    # ### end Alembic commands ###
