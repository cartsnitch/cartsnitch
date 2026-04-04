"""Bootstrap users table on fresh databases.

On fresh databases, migrations 001-006 skip users-table operations because
the table does not exist yet. Base.metadata.create_all() in env.py is meant
to handle this, but if it fails (import errors, etc.) the table is never
created. This migration creates the users table with raw SQL as a safety net.

Revision ID: 007_bootstrap_users_table
Revises: 006_email_inbound_token_server_default
Create Date: 2026-04-04
"""

import sqlalchemy as sa
from sqlalchemy import text

from alembic import op

revision = "007_bootstrap_users_table"
down_revision = "006_email_inbound_token_server_default"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if inspector.has_table("users"):
        return  # Table already exists (non-fresh DB or create_all already ran)

    conn.execute(text("""
        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            hashed_password VARCHAR(255),
            display_name VARCHAR(100),
            email_verified BOOLEAN NOT NULL DEFAULT false,
            image TEXT,
            email_inbound_token VARCHAR(22) NOT NULL UNIQUE
                DEFAULT replace(replace(trim(trailing '=' from encode(gen_random_bytes(16), 'base64')), '+', '-'), '/', '_'),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """))


def downgrade() -> None:
    op.execute(text("DROP TABLE IF EXISTS users"))
