"""Add GIN index on normalized_products.upc_variants for fast JSON containment lookups.

Revision ID: 002_add_normalized_products_upc_variants_index
Revises: 001_add_email_inbound_token
Create Date: 2026-04-14
"""

from collections.abc import Sequence

from alembic import op

revision: str = "002_add_normalized_products_upc_variants_index"
down_revision: str | None = "001_add_email_inbound_token"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_normalized_products_upc_variants",
        "normalized_products",
        ["upc_variants"],
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index("ix_normalized_products_upc_variants", table_name="normalized_products")
