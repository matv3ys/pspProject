"""empty message

Revision ID: 70f67df9c9f5
Revises: f798438b1e8b
Create Date: 2024-11-25 21:57:03.358396

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '70f67df9c9f5'
down_revision: Union[str, None] = 'f798438b1e8b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('TaskTable', sa.Column('author_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'TaskTable', 'UserTable', ['author_id'], ['user_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'TaskTable', type_='foreignkey')
    op.drop_column('TaskTable', 'author_id')
    # ### end Alembic commands ###
