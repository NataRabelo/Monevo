# -------------------------------------
# Agrupador de Transações por Mês
# -------------------------------------
def agrupar_transacoes_por_mes(transacoes):
    """Agrupa uma lista de objetos Transacoes por mês e ano e calcula os totais."""
    transacoes_agrupadas = {}
    
    for t in transacoes:
        chave_mes_ano = t.data_transacao.strftime('%Y-%m')
        
        if chave_mes_ano not in transacoes_agrupadas:
            transacoes_agrupadas[chave_mes_ano] = {
                'nome_mes': t.data_transacao.strftime('%B / %Y').title().replace('Of', 'de'), 
                'itens': [],
                'total_receita_mes': 0.0,
                'total_despesa_mes': 0.0
            }
        try:
            valor = float(t.valor) 
        except ValueError:
            valor = 0.0
            
        if t.tipo == 'Receita':
            transacoes_agrupadas[chave_mes_ano]['total_receita_mes'] += valor
        elif t.tipo == 'Despesa':
            transacoes_agrupadas[chave_mes_ano]['total_despesa_mes'] += valor
        transacoes_agrupadas[chave_mes_ano]['itens'].append(t)
        
    transacoes_agrupadas_ordenadas = dict(sorted(transacoes_agrupadas.items(), reverse=True))

    return transacoes_agrupadas_ordenadas