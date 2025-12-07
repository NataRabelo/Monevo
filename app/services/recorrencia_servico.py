from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from flask import current_app

# Define a janela de geração (gerar transações para os próximos 12 meses)
JANELA_MESES = 12

def gerar_proximas_transacoes_recorrentes(mestra_transacao, db, Transacoes):
    """
    Gera as ocorrências futuras de uma transação mestra.
    """
    
    # 1. Validar se a recorrência é válida
    if mestra_transacao.recorrencia == 'Sem recorrencia':
        return 0
        
    id_mestra = mestra_transacao.id
    
    # Se a transação mestra não tiver um id_original definido, define para ela mesma
    if not mestra_transacao.id_original:
        mestra_transacao.id_original = id_mestra
        db.session.add(mestra_transacao) # Salva a atualização
        db.session.commit()
    
    hoje = datetime.now().date()
    limite_geracao = hoje + relativedelta(months=+JANELA_MESES)
    
    novas_transacoes = []
    
    # Começa a partir da data de transação da mestra
    data_base = mestra_transacao.data_transacao 

    # Loop para gerar as ocorrências futuras
    # *Começa a partir da data da mestra, mas o primeiro 'data_proxima' é o primeiro futuro.
    while data_base <= limite_geracao:
        data_proxima = None
        
        if mestra_transacao.recorrencia == 'Diária':
            data_proxima = data_base + relativedelta(days=+1)
        elif mestra_transacao.recorrencia == 'Semanal':
            data_proxima = data_base + relativedelta(weeks=+1)
        elif mestra_transacao.recorrencia == 'Mensal': # <-- CORREÇÃO AQUI
            data_proxima = data_base + relativedelta(months=+1)
        elif mestra_transacao.recorrencia == 'Anual':
            data_proxima = data_base + relativedelta(years=+1)
        
        # Se data_proxima for None (erro de lógica) ou ultrapassar o limite
        if not data_proxima or data_proxima > limite_geracao:
            # Se for Anual, o limite de 12 meses pode ser muito curto,
            # mas vamos manter a lógica original por enquanto.
            break
            
        existe = Transacoes.query.filter(
            Transacoes.id_original == id_mestra, 
            Transacoes.data_transacao == data_proxima
        ).first()
        
        # Garante que a transação não exista e que seja FUTURE (exclui a mestra se for hoje)
        if not existe and data_proxima > hoje:
            
            nova_transacao = Transacoes(
                usuario_id=mestra_transacao.usuario_id,
                tipo=mestra_transacao.tipo,
                descricao=mestra_transacao.descricao,
                valor=mestra_transacao.valor,
                data_transacao=data_proxima,
                conta_id=mestra_transacao.conta_id,
                categoria_id=mestra_transacao.categoria_id,
                cartao_id=mestra_transacao.cartao_id,
                recorrencia='Sem recorrencia', # <-- Recomendado: Marcar ocorrências como 'Sem recorrencia'
                id_original=id_mestra, 
                recorrente=False # <-- Recomendado: Marcar ocorrências como False. A mestra é True.
            )
            novas_transacoes.append(nova_transacao)

        data_base = data_proxima # Avança a base para a próxima iteração
        
    if novas_transacoes:
        db.session.add_all(novas_transacoes)
        db.session.commit()
        return len(novas_transacoes)
    
    return 0