"""Update for new db

Revision ID: 16b91fc95973
Revises: 76784373be35
Create Date: 2025-10-09 21:02:36.864250
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '16b91fc95973'
down_revision = '76784373be35'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # ✅ Criação da nova tabela 'cartoes' apenas se não existir
    if 'cartoes' not in existing_tables:
        op.create_table(
            'cartoes',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False),
            sa.Column('nome_cartao', sa.String(length=100), nullable=False),
            sa.Column('bandeira', sa.String(length=50), nullable=True),
            sa.Column('limite', sa.Float(), nullable=False),
            sa.Column('dia_fechamento_fatura', sa.Integer(), nullable=False),
            sa.Column('dia_vencimento_fatura', sa.Integer(), nullable=False),
            sa.Column('criado_em', sa.DateTime(), nullable=True)
        )

    # ✅ Ajustes na tabela 'transacoes'
    existing_fks = {fk['name']: fk for fk in inspector.get_foreign_keys('transacoes')}

    with op.batch_alter_table('transacoes', schema=None) as batch_op:
        # Adiciona nova coluna 'cartao_id' se ainda não existir
        existing_cols = [c['name'] for c in inspector.get_columns('transacoes')]
        if 'cartao_id' not in existing_cols:
            batch_op.add_column(sa.Column('cartao_id', sa.Integer(), nullable=True))

        # Permite conta_id ser nulo
        batch_op.alter_column('conta_id', existing_type=sa.INTEGER(), nullable=True)

        # ✅ Remove constraints antigas, somente se tiver nome
        for fk_name, fk in existing_fks.items():
            if fk['referred_table'] in ['contas', 'categorias'] and fk_name:
                batch_op.drop_constraint(fk_name, type_='foreignkey')

        # ✅ Cria novas FKs com nomes explícitos
        batch_op.create_foreign_key('fk_transacoes_conta', 'contas', ['conta_id'], ['id'], ondelete='SET NULL')
        batch_op.create_foreign_key('fk_transacoes_cartao', 'cartoes', ['cartao_id'], ['id'], ondelete='SET NULL')
        batch_op.create_foreign_key('fk_transacoes_categoria', 'categorias', ['categoria_id'], ['id'], ondelete='SET NULL')


def downgrade():
    with op.batch_alter_table('transacoes', schema=None) as batch_op:
        # Remove as novas FKs criadas
        for fk_name in ['fk_transacoes_conta', 'fk_transacoes_cartao', 'fk_transacoes_categoria']:
            try:
                batch_op.drop_constraint(fk_name, type_='foreignkey')
            except Exception:
                pass  # Ignora se já não existir

        # Restaura constraints originais
        batch_op.create_foreign_key('fk_transacoes_conta_old', 'contas', ['conta_id'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key('fk_transacoes_categoria_old', 'categorias', ['categoria_id'], ['id'], ondelete='CASCADE')

        batch_op.alter_column('conta_id', existing_type=sa.INTEGER(), nullable=False)

        # Remove a coluna 'cartao_id' se existir
        existing_cols = [c['name'] for c in sa.inspect(op.get_bind()).get_columns('transacoes')]
        if 'cartao_id' in existing_cols:
            batch_op.drop_column('cartao_id')

    # Exclui a tabela 'cartoes' se ela existir
    conn = op.get_bind()
    if 'cartoes' in sa.inspect(conn).get_table_names():
        op.drop_table('cartoes')
