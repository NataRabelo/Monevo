# -------------------------------------
# Gerador de Transações Recorrentes
# -------------------------------------

from datetime import datetime
from dateutil.relativedelta import relativedelta

# Janela padrão para geração de recorrências (12 meses)
JANELA_MESES = 12


def gerar_proximas_transacoes_recorrentes(mestra_transacao, db, Transacoes, num_meses=12):
    if mestra_transacao.recorrencia == 'Sem recorrencia':
        return 0

    id_mestra = mestra_transacao.id

    if not mestra_transacao.id_original:
        mestra_transacao.id_original = id_mestra
        db.session.add(mestra_transacao)
        db.session.commit()

    hoje = datetime.now().date()
    limite_geracao = hoje + relativedelta(months=+num_meses)

    novas_transacoes = []
    data_base = mestra_transacao.data_transacao

    while data_base <= limite_geracao:
        if mestra_transacao.recorrencia == 'Diária':
            data_proxima = data_base + relativedelta(days=+1)
        elif mestra_transacao.recorrencia == 'Semanal':
            data_proxima = data_base + relativedelta(weeks=+1)
        elif mestra_transacao.recorrencia == 'Mensal':
            data_proxima = data_base + relativedelta(months=+1)
        elif mestra_transacao.recorrencia == 'Anual':
            data_proxima = data_base + relativedelta(years=+1)
        else:
            break

        if data_proxima > limite_geracao:
            break

        existe = Transacoes.query.filter(
            Transacoes.id_original == id_mestra,
            Transacoes.data_transacao == data_proxima
        ).first()

        if not existe:
            novas_transacoes.append(
                Transacoes(
                    usuario_id=mestra_transacao.usuario_id,
                    tipo=mestra_transacao.tipo,
                    descricao=mestra_transacao.descricao,
                    valor=mestra_transacao.valor,
                    data_transacao=data_proxima,
                    conta_id=mestra_transacao.conta_id,
                    categoria_id=mestra_transacao.categoria_id,
                    cartao_id=mestra_transacao.cartao_id,
                    recorrencia='Sem recorrencia',
                    id_original=id_mestra,
                    recorrente=False
                )
            )

        data_base = data_proxima

    if novas_transacoes:
        db.session.add_all(novas_transacoes)
        db.session.commit()
        return len(novas_transacoes)

    return 0
