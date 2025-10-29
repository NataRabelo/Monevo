"""Adicionar conta_id em cartoes

Revision ID: 15d9c64ee406
Revises: 16b91fc95973
Create Date: 2025-10-28 22:08:31.806539
"""
from alembic import op
import sqlalchemy as sa


revision = '15d9c64ee406'
down_revision = '16b91fc95973'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('cartoes', schema=None) as batch_op:
        # Criar coluna já como NOT NULL
        batch_op.add_column(sa.Column('conta_id', sa.Integer(), nullable=False))

        # Criar FK com nome fixo
        batch_op.create_foreign_key(
            'fk_cartoes_conta',       # nome da constraint
            'contas',                 # tabela referenciada
            ['conta_id'],             # coluna local
            ['id'],                   # coluna remota
            ondelete='CASCADE'
        )


def downgrade():
    with op.batch_alter_table('cartoes', schema=None) as batch_op:
        batch_op.drop_constraint('fk_cartoes_conta', type_='foreignkey')
        batch_op.drop_column('conta_id')
