"""add forward_messages_columns message_text file_id entities 

Revision ID: 6f10dd754570
Revises: b1d5bdb4189f
Create Date: 2024-01-13 15:34:59.687564

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f10dd754570'
down_revision = 'b1d5bdb4189f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('forwarded_messages', sa.Column('message_text', sa.String(), nullable=True))
    op.add_column('forwarded_messages', sa.Column('file_id', sa.String(), nullable=True))
    op.add_column('forwarded_messages', sa.Column('entities', sa.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('forwarded_messages', 'entities')
    op.drop_column('forwarded_messages', 'file_id')
    op.drop_column('forwarded_messages', 'message_text')
    # ### end Alembic commands ###