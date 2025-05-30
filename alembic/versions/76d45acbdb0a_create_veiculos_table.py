"""create veiculos table

Revision ID: 76d45acbdb0a
Revises: 
Create Date: 2025-05-28 00:22:49.878402

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '76d45acbdb0a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('veiculos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('veiculo', sa.String(length=255), nullable=True),
    sa.Column('marca', sa.String(length=255), nullable=True),
    sa.Column('ano', sa.Integer(), nullable=True),
    sa.Column('descricao', sa.String(length=255), nullable=True),
    sa.Column('vendido', sa.Boolean(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_veiculos_ano'), 'veiculos', ['ano'], unique=False)
    op.create_index(op.f('ix_veiculos_id'), 'veiculos', ['id'], unique=False)
    op.create_index(op.f('ix_veiculos_marca'), 'veiculos', ['marca'], unique=False)
    op.create_index(op.f('ix_veiculos_veiculo'), 'veiculos', ['veiculo'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_veiculos_veiculo'), table_name='veiculos')
    op.drop_index(op.f('ix_veiculos_marca'), table_name='veiculos')
    op.drop_index(op.f('ix_veiculos_id'), table_name='veiculos')
    op.drop_index(op.f('ix_veiculos_ano'), table_name='veiculos')
    op.drop_table('veiculos')
    # ### end Alembic commands ###
