"""Add server_default to users.email_inbound_token.

Revision ID: 006_email_inbound_token_server_default
Revises: 005_add_email_inbound_token
Create Date: 2026-04-04
"""

import sqlalchemy as sa
from alembic import op

revision = "006_email_inbound_token_server_default"
down_revision = "005_add_email_inbound_token"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    # Guard: on a fresh DB Base.metadata.create_all already sets the server_default
    if not inspector.has_table("users"):
        return
    cols = {c["name"]: c for c in inspector.get_columns("users")}
    if "email_inbound_token" not in cols:
        return
    if cols["email_inbound_token"].get("default") is not None:
        return
    op.alter_column(
        "users",
        "email_inbound_token",
        server_default=sa.text(
            "replace(replace(trim(trailing '=' from encode(gen_random_bytes(16), 'base64')), '+', '-'), '/', '_')"
        ),
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "email_inbound_token",
        server_default=None,
    )
