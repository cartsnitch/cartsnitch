"""Change users.id and user_id FKs from uuid to text.

Revision ID: 003_fix_user_id_text
Revises:
Create Date: 2026-03-31
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "003_fix_user_id_text"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop FK constraints first
    op.execute("ALTER TABLE user_store_accounts DROP CONSTRAINT IF EXISTS user_store_accounts_user_id_fkey")
    op.execute("ALTER TABLE purchases DROP CONSTRAINT IF EXISTS purchases_user_id_fkey")

    # Alter users.id from uuid to text
    op.execute("ALTER TABLE users ALTER COLUMN id TYPE text USING id::text")

    # Alter user_id columns from uuid to text
    op.execute("ALTER TABLE user_store_accounts ALTER COLUMN user_id TYPE text USING user_id::text")
    op.execute("ALTER TABLE purchases ALTER COLUMN user_id TYPE text USING user_id::text")

    # Re-add FK constraints
    op.execute(
        "ALTER TABLE user_store_accounts ADD CONSTRAINT user_store_accounts_user_id_fkey "
        "FOREIGN KEY (user_id) REFERENCES users(id)"
    )
    op.execute(
        "ALTER TABLE purchases ADD CONSTRAINT purchases_user_id_fkey "
        "FOREIGN KEY (user_id) REFERENCES users(id)"
    )


def downgrade() -> None:
    # Drop FK constraints
    op.execute("ALTER TABLE user_store_accounts DROP CONSTRAINT IF EXISTS user_store_accounts_user_id_fkey")
    op.execute("ALTER TABLE purchases DROP CONSTRAINT IF EXISTS purchases_user_id_fkey")

    # Alter back to uuid
    op.execute("ALTER TABLE users ALTER COLUMN id TYPE uuid USING id::uuid")
    op.execute("ALTER TABLE user_store_accounts ALTER COLUMN user_id TYPE uuid USING user_id::uuid")
    op.execute("ALTER TABLE purchases ALTER COLUMN user_id TYPE uuid USING user_id::uuid")

    # Re-add FK constraints
    op.execute(
        "ALTER TABLE user_store_accounts ADD CONSTRAINT user_store_accounts_user_id_fkey "
        "FOREIGN KEY (user_id) REFERENCES users(id)"
    )
    op.execute(
        "ALTER TABLE purchases ADD CONSTRAINT purchases_user_id_fkey "
        "FOREIGN KEY (user_id) REFERENCES users(id)"
    )
