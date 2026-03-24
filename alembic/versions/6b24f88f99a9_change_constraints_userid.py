"""change constraints userId

Revision ID: 6b24f88f99a9
Revises: 
Create Date: 2026-03-24 12:00:04.971870

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b24f88f99a9'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # add foreign key constraint
    op.create_foreign_key(
        constraint_name="fk_interview_user_id",
        source_table="interview_data",
        referent_table="user_data",
        local_cols=["userId"],
        remote_cols=["id"],
    )


def downgrade() -> None:
    # remove foreign key constraint
    op.drop_constraint(
        constraint_name="fk_interview_user_id",
        table_name="interview_data",
        type_="foreignkey"
    )