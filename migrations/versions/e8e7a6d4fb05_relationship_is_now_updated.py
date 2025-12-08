"""relationship is now updated

Revision ID: e8e7a6d4fb05
Revises: b5860cd54ac6
Create Date: 2025-12-08 17:07:49.553035

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8e7a6d4fb05'
down_revision = 'b5860cd54ac6'
branch_labels = None
depends_on = None


def _drop_all_fks_on_table(conn, table_name):
    inspector = sa.inspect(conn)
    fks = inspector.get_foreign_keys(table_name)
    return [fk['name'] for fk in fks if fk.get('name')]


def upgrade():
    conn = op.get_bind()

    # retire qualquer FK existente (independente do nome)
    existing_fk_names = _drop_all_fks_on_table(conn, 'saldo_inicial')
    with op.batch_alter_table('saldo_inicial', schema=None) as batch_op:
        for fk_name in existing_fk_names:
            # safe drop by explicit name
            batch_op.drop_constraint(fk_name, type_='foreignkey')

        # criar FKs com nomes explícitos e ondelete CASCADE
        batch_op.create_foreign_key(
            'fk_saldo_inicial_usuario_id_usuarios',
            'usuarios',
            ['usuario_id'],
            ['id'],
            ondelete='CASCADE'
        )
        batch_op.create_foreign_key(
            'fk_saldo_inicial_conta_id_contas',
            'contas',
            ['conta_id'],
            ['id'],
            ondelete='CASCADE'
        )


def downgrade():
    conn = op.get_bind()

    # drop as FKs criadas no upgrade (pelos nomes que definimos)
    with op.batch_alter_table('saldo_inicial', schema=None) as batch_op:
        batch_op.drop_constraint('fk_saldo_inicial_usuario_id_usuarios', type_='foreignkey')
        batch_op.drop_constraint('fk_saldo_inicial_conta_id_contas', type_='foreignkey')

        # recria as FKs sem ondelete (nomeamos novamente; ajuste se quiser nomes diferentes)
        batch_op.create_foreign_key(
            'fk_saldo_inicial_usuario_id_usuarios',
            'usuarios',
            ['usuario_id'],
            ['id']
        )
        batch_op.create_foreign_key(
            'fk_saldo_inicial_conta_id_contas',
            'contas',
            ['conta_id'],
            ['id']
        )
