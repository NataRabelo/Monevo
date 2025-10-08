"""Atualizando table user

Revision ID: 76784373be35
Revises: 09d43b99536e
Create Date: 2025-10-07 18:58:32.941493

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76784373be35'
down_revision = '09d43b99536e'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.add_column(sa.Column('nome', sa.String(length=200), nullable=False))
        batch_op.add_column(sa.Column('sobrenome', sa.String(length=200), nullable=False))
        batch_op.add_column(sa.Column('celular', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('cpf', sa.String(length=50), nullable=False))
        batch_op.create_unique_constraint('uq_usuarios_cpf', ['cpf'])
        batch_op.drop_column('nome_completo')


def downgrade():
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.add_column(sa.Column('nome_completo', sa.VARCHAR(length=200), nullable=False))
        batch_op.drop_constraint('uq_usuarios_cpf', type_='unique')
        batch_op.drop_column('cpf')
        batch_op.drop_column('celular')
        batch_op.drop_column('sobrenome')
        batch_op.drop_column('nome')
