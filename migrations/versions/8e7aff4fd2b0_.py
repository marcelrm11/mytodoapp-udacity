"""empty message

Revision ID: 8e7aff4fd2b0
Revises: f8d36ce8cb4f
Create Date: 2023-01-17 18:50:07.067611

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e7aff4fd2b0'
down_revision = 'f8d36ce8cb4f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('todos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('completed', sa.Boolean(), nullable=True))
    op.execute('UPDATE todos SET completed = False WHERE completed IS NULL;')
    op.alter_column('todos', 'completed', nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('todos', schema=None) as batch_op:
        batch_op.drop_column('completed')

    # ### end Alembic commands ###
