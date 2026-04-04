"""Add Better-Auth tables and extend users table.

Creates sessions, accounts, and verifications tables for Better-Auth.
Adds email_verified and image columns to existing users table.
Migrates password hashes from users.hashed_password to accounts.password.

Revision ID: 002_better_auth_tables
Revises: 001_encrypt_session_data
Create Date: 2026-03-28
"""

import sqlalchemy as sa
from sqlalchemy import text

from alembic import op

revision = "002_better_auth_tables"
down_revision = "001_encrypt_session_data"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # --- Extend users table for Better-Auth compatibility ---
    # Guard: on a fresh DB Base.metadata.create_all (called in env.py after migrations)
    # creates the users table with all columns, so migration 002 must not re-run add_column.
    if inspector.has_table("users"):
        existing_user_cols = [c["name"] for c in inspector.get_columns("users")]
        if "email_verified" not in existing_user_cols:
            op.add_column("users", sa.Column("email_verified", sa.Boolean(), nullable=False, server_default="false"))
        if "image" not in existing_user_cols:
            op.add_column("users", sa.Column("image", sa.Text(), nullable=True))

    # --- Create sessions table ---
    if not inspector.has_table("sessions"):
        op.create_table(
            "sessions",
            sa.Column("id", sa.Text(), nullable=False),
            sa.Column("token", sa.Text(), nullable=False),
            sa.Column("user_id", sa.Text(), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("ip_address", sa.Text(), nullable=True),
            sa.Column("user_agent", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_sessions_token", "sessions", ["token"], unique=True)
        op.create_index("ix_sessions_user_id", "sessions", ["user_id"])

    # --- Create accounts table ---
    if not inspector.has_table("accounts"):
        op.create_table(
            "accounts",
            sa.Column("id", sa.Text(), nullable=False),
            sa.Column("user_id", sa.Text(), nullable=False),
            sa.Column("account_id", sa.Text(), nullable=False),
            sa.Column("provider_id", sa.Text(), nullable=False),
            sa.Column("access_token", sa.Text(), nullable=True),
            sa.Column("refresh_token", sa.Text(), nullable=True),
            sa.Column("access_token_expires_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("refresh_token_expires_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("scope", sa.Text(), nullable=True),
            sa.Column("id_token", sa.Text(), nullable=True),
            sa.Column("password", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_accounts_user_id", "accounts", ["user_id"])

    # --- Create verifications table ---
    if not inspector.has_table("verifications"):
        op.create_table(
            "verifications",
            sa.Column("id", sa.Text(), nullable=False),
            sa.Column("identifier", sa.Text(), nullable=False),
            sa.Column("value", sa.Text(), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )

    # --- Migrate existing password hashes to accounts table ---
    # Only run on existing (non-fresh) DBs that already have users table with data
    if inspector.has_table("users"):
        users = conn.execute(
            text("SELECT id, hashed_password FROM users WHERE hashed_password IS NOT NULL")
        ).fetchall()

        for user_id, hashed_password in users:
            user_id_str = str(user_id)
            conn.execute(
                text(
                    "INSERT INTO accounts (id, user_id, account_id, provider_id, password, created_at, updated_at) "
                    "VALUES (gen_random_uuid()::text, :user_id, :account_id, 'credential', :password, now(), now())"
                ),
                {"user_id": user_id_str, "account_id": user_id_str, "password": hashed_password},
            )


def downgrade() -> None:
    op.execute(text("DROP INDEX IF EXISTS ix_accounts_user_id"))
    op.execute(text("DROP TABLE IF EXISTS verifications"))
    op.execute(text("DROP TABLE IF EXISTS accounts"))
    op.execute(text("DROP INDEX IF EXISTS ix_sessions_user_id"))
    op.execute(text("DROP INDEX IF EXISTS ix_sessions_token"))
    op.execute(text("DROP TABLE IF EXISTS sessions"))
    op.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS image"))
    op.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS email_verified"))
