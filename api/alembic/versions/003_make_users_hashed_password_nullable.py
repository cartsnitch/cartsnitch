"""Make users.hashed_password nullable.

Better-Auth inserts users without hashed_password (passwords live in the
accounts table). This column is now purely optional.

Revision ID: 003_make_users_hashed_password_nullable
Revises: 002_better_auth_tables
Create Date: 2026-03-30
"""

import sqlalchemy as sa

from alembic import op

revision = "003_make_users_hashed_password_nullable"
down_revision = "002_better_auth_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # Fresh DB — nothing to alter
    if not inspector.has_table("users"):
        return

    cols = {c["name"]: c for c in inspector.get_columns("users")}
    if "hashed_password" in cols and not cols["hashed_password"]["nullable"]:
        op.alter_column("users", "hashed_password", existing_type=sa.String(255), nullable=True)


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if not inspector.has_table("users"):
        return

    cols = {c["name"]: c for c in inspector.get_columns("users")}
    if "hashed_password" in cols and cols["hashed_password"]["nullable"]:
        op.alter_column("users", "hashed_password", existing_type=sa.String(255), nullable=False)
