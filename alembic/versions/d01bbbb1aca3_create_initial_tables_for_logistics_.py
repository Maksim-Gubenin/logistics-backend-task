"""Create initial tables for logistics system

Revision ID: d01bbbb1aca3
Revises:
Create Date: 2026-02-07 00:22:25.251712

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "d01bbbb1aca3"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table("categories",
    sa.Column("name", sa.String(length=255), nullable=False),
    sa.Column("parent_id", sa.BigInteger(), nullable=True),
    sa.Column("id", sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(
        ["parent_id"],
        ["categories.id"],
        name=op.f("fk_categories_parent_id_categories"),
        ondelete="CASCADE"
    ),
    sa.PrimaryKeyConstraint("id", name=op.f("pk_categories"))
    )
    op.create_table("clients",
    sa.Column("name", sa.String(length=255), nullable=False),
    sa.Column("address", sa.String(length=500), nullable=False),
    sa.Column("id", sa.BigInteger(), nullable=False),
    sa.PrimaryKeyConstraint("id", name=op.f("pk_clients"))
    )
    op.create_table("nomenclatures",
    sa.Column("name", sa.String(length=255), nullable=False),
    sa.Column("quantity", sa.Integer(), nullable=False),
    sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column("category_id", sa.BigInteger(), nullable=False),
    sa.Column("id", sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(
        ["category_id"],
        ["categories.id"],
        name=op.f("fk_nomenclatures_category_id_categories")
    ),
    sa.PrimaryKeyConstraint("id", name=op.f("pk_nomenclatures"))
    )
    op.create_table("orders",
    sa.Column("client_id", sa.BigInteger(), nullable=False),
    sa.Column("order_date", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    sa.Column("id", sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(["client_id"], ["clients.id"], name=op.f("fk_orders_client_id_clients")),
    sa.PrimaryKeyConstraint("id", name=op.f("pk_orders"))
    )
    op.create_table("order_items",
    sa.Column("order_id", sa.BigInteger(), nullable=False),
    sa.Column("nomenclature_id", sa.BigInteger(), nullable=False),
    sa.Column("quantity", sa.Integer(), nullable=False),
    sa.Column("price_at_purchase", sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column("id", sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(
        ["nomenclature_id"],
        ["nomenclatures.id"],
        name=op.f("fk_order_items_nomenclature_id_nomenclatures")
    ),
    sa.ForeignKeyConstraint(["order_id"], ["orders.id"], name=op.f("fk_order_items_order_id_orders")),
    sa.PrimaryKeyConstraint("id", name=op.f("pk_order_items"))
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("nomenclatures")
    op.drop_table("clients")
    op.drop_table("categories")
