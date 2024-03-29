"""init

Revision ID: 1bb26a08633e
Revises: 
Create Date: 2024-01-07 16:21:40.081493

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1bb26a08633e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chat_settings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('variable_name', sa.String(), nullable=False),
    sa.Column('value', sa.String(), nullable=False),
    sa.Column('chat_id', sa.BigInteger(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('forwarded_messages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('from_chat_id', sa.BigInteger(), nullable=False),
    sa.Column('from_user', sa.BigInteger(), nullable=False),
    sa.Column('from_message_id', sa.BigInteger(), nullable=True),
    sa.Column('to_chat_id', sa.BigInteger(), nullable=False),
    sa.Column('to_chat_message_id', sa.BigInteger(), nullable=True),
    sa.Column('model_type', sa.String(), nullable=False),
    sa.Column('is_private', sa.Boolean(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('from_chat_id', 'from_message_id', name='unq_messages_from_chat_id_from_message_id'),
    sa.UniqueConstraint('from_message_id')
    )
    op.create_table('hashtag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('from_chat_id', sa.BigInteger(), nullable=False),
    sa.Column('to_chat_id', sa.BigInteger(), nullable=False),
    sa.Column('hashtag_name', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('from_chat_id', 'hashtag_name', name='unq_hashtags_from_chat_id_to_chat_id_hashtag_name')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('hashtag')
    op.drop_table('forwarded_messages')
    op.drop_table('chat_settings')
    # ### end Alembic commands ###
