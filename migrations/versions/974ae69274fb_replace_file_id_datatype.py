"""replace file id datatype

Revision ID: 974ae69274fb
Revises: f7e5e73975f4
Create Date: 2024-02-09 02:13:12.794541

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '974ae69274fb'
down_revision = 'f7e5e73975f4'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        ALTER TABLE forwarded_messages
        ADD COLUMN IF NOT EXISTS file_ids text[];
    """)
    op.execute("""
        UPDATE forwarded_messages
        SET file_ids = array_append(file_ids::text[], file_id::text)
        WHERE file_id IS NOT NULL;
    """)
    op.drop_column('forwarded_messages', 'file_id')


def downgrade():
    # should not drop file_ids table because media group data will be lost
    op.add_column('forwarded_messages', sa.Column('file_id', sa.String(), nullable=True))
