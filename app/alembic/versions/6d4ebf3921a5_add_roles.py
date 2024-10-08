"""add roles

Revision ID: 6d4ebf3921a5
Revises: 09c010cfc27b
Create Date: 2024-08-23 23:36:44.498755+10:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6d4ebf3921a5"
down_revision = "09c010cfc27b"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    role_table = op.create_table(
        "role",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.bulk_insert(
        role_table,
        [
            {"name": "admin"},
            {"name": "user"},
        ],
    )
    op.create_index(op.f("ix_role_id"), "role", ["id"], unique=False)
    op.create_index(op.f("ix_role_name"), "role", ["name"], unique=True)
    op.add_column("user", sa.Column("role_id", sa.Integer(), server_default="2", nullable=False))
    op.create_index(op.f("ix_user_role_id"), "user", ["role_id"], unique=False)
    op.create_foreign_key(None, "user", "role", ["role_id"], ["id"])
    user_table = sa.table("user", sa.column("username", sa.String), sa.column("role_id", sa.Integer))
    op.execute(user_table.update().where(user_table.c.username == op.inline_literal('admin')).values({'role_id': 1}))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "user", type_="foreignkey")
    op.drop_index(op.f("ix_user_role_id"), table_name="user")
    op.drop_column("user", "role_id")
    op.drop_index(op.f("ix_role_name"), table_name="role")
    op.drop_index(op.f("ix_role_id"), table_name="role")
    op.drop_table("role")
    # ### end Alembic commands ###
