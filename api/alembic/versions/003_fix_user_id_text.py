"""Change users.id and FK columns from uuid to text.

Better-Auth generates nanoid-style text IDs (e.g. pGud2ln2WAFHC0KYjBVKR4Rc7mM8OcTI),
but the users table was using PostgreSQL uuid type, causing INSERT failures.

Revision ID: 003_fix_user_id_text
Revises: 002_better_auth_tables
Create Date: 2026-03-31
"""

import sqlalchemy as sa
from sqlalchemy import text

from alembic import op

revision = "003_fix_user_id_text"
down_revision = "002_better_auth_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Step 1: Drop FK constraints that reference users.id
    op.execute(text("ALTER TABLE user_store_accounts DROP CONSTRAINT IF EXISTS user_store_accounts_user_id_fkey"))
    op.execute(text("ALTER TABLE purchases DROP CONSTRAINT IF EXISTS purchases_user_id_fkey"))

    # Step 2: Alter users.id from uuid to text
    op.alter_column("users", "id", existing_type=sa.UUID(), type_=sa.Text(), existing_nullable=False, postgresql_using="id::text")

    # Step 3: Alter user_store_accounts.user_id from uuid to text
    op.alter_column("user_store_accounts", "user_id", existing_type=sa.UUID(), type_=sa.Text(), existing_nullable=False, postgresql_using="user_id::text")

    # Step 4: Alter purchases.user_id from uuid to text
    op.alter_column("purchases", "user_id", existing_type=sa.UUID(), type_=sa.Text(), existing_nullable=False, postgresql_using="user_id::text")

    # Step 5: Re-add FK constraints
    op.execute(text("ALTER TABLE user_store_accounts ADD CONSTRAINT user_store_accounts_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id)"))
    op.execute(text("ALTER TABLE purchases ADD CONSTRAINT purchases_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id)"))


def downgrade() -> None:
    # Drop FK constraints
    op.execute(text("ALTER TABLE purchases DROP CONSTRAINT IF EXISTS purchases_user_id_fkey"))
    op.execute(text("ALTER TABLE user_store_accounts DROP CONSTRAINT IF EXISTS user_store_accounts_user_id_fkey"))

    # Alter back to UUID
    op.alter_column("purchases", "user_id", existing_type=sa.Text(), type_=sa.UUID(), existing_nullable=False, postgresql_using="user_id::uuid")
    op.alter_column("user_store_accounts", "user_id", existing_type=sa.Text(), type_=sa.UUID(), existing_nullable=False, postgresql_using="user_id::uuid")
    op.alter_column("users", "id", existing_type=sa.Text(), type_=sa.UUID(), existing_nullable=False, postgresql_using="id::uuid")

    # Re-add FK constraints
    op.execute(text("ALTER TABLE user_store_accounts ADD CONSTRAINT user_store_accounts_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id)"))
    op.execute(text("ALTER TABLE purchases ADD CONSTRAINT purchases_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id)"))
