from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Transacoes, Contas, Categorias
from sqlalchemy import func, extract, case
from datetime import datetime
from dateutil.relativedelta import relativedelta

projecao_bp = Blueprint('projecao', __name__, url_prefix='/projecao')

@projecao_bp.route('/', methods=['GET', 'POST'])
@login_required
def acessarProjecao():
    if request.method == "GET":
        return render_template('dashboard/projecao.html')

# ===========================
#     ROTA PRINCIPAL JSON
# ===========================
@projecao_bp.route("/dados", methods=["GET"])
@login_required
def obter_dados_projecao():
    usuario_id = current_user.id
    hoje = datetime.now().date()
    
    # 1. Definição do período fixo (Mês Atual + 11 meses futuros = 12 meses totais)
    data_inicio_projecao = hoje.replace(day=1) # Dia 1 do Mês Atual
    data_fim_projecao = data_inicio_projecao + relativedelta(months=+12, days=-1)
    
    # Parâmetros opcionais para filtragem dos CARDS (Mês/Ano)
    filtro_mes = request.args.get("mes")
    filtro_ano = request.args.get("ano")

    # ===============================
    # 2. SALDO INICIAL DA PROJEÇÃO (Saldo ao final do Mês Anterior)
    # ===============================
    
    # 2a. Saldo Inicial Básico (Definido pelo usuário na criação da conta)
    saldo_inicial_contas = db.session.query(func.sum(Contas.saldo_inicial))\
                           .filter_by(usuario_id=usuario_id).scalar() or 0

    # 2b. Movimentos compensados ANTES do início do período de projeção (data_transacao < data_inicio_projecao)
    mov_anterior = db.session.query(
        func.sum(
            case(
                (Transacoes.tipo == "Receita", Transacoes.valor),
                else_=-Transacoes.valor
            )
        )
    ).filter(
        Transacoes.usuario_id == usuario_id,
        Transacoes.data_transacao < data_inicio_projecao, # Filtro chave: APENAS movimentos ANTES do Mês 1
        Transacoes.parcela_atual != 0 
    ).scalar() or 0

    # Saldo Inicial da Projeção = Saldo Básico + Movimentos até o final do mês anterior
    # Este é o ponto de partida para a iteração de 12 meses.
    saldo_inicial_projecao = saldo_inicial_contas + mov_anterior


    # ===============================
    # 3. DADOS MENSAIS E GLOBAIS (12 meses)
    # ===============================
    
    # Consulta unificada para Receita, Despesa, Categoria e Fluxo de Caixa Mensal
    dados_mensais = db.session.query(
        extract('year', Transacoes.data_transacao).label("ano"),
        extract('month', Transacoes.data_transacao).label("mes"),
        Transacoes.tipo,
        Transacoes.valor,
        Categorias.nome.label("categoria_nome"),
    ).join(Categorias, Categorias.id == Transacoes.categoria_id)\
    .filter(
        Transacoes.usuario_id == usuario_id,
        Transacoes.data_transacao.between(data_inicio_projecao, data_fim_projecao),
        Transacoes.parcela_atual != 0 # Ignora registros mestres
    ).order_by("ano", "mes", Transacoes.data_transacao).all()

    # Estruturas para montagem dos gráficos
    dados_mensais_agrupados = {}
    dados_pizza_receita = {}
    dados_pizza_despesa = {}

    for ano, mes, tipo_tx, valor, categoria_nome in dados_mensais:
        chave_mes = f"{int(mes):02}/{int(ano)}"
        
        # Agrupamento Mensal (Gráfico 1 e 2)
        if chave_mes not in dados_mensais_agrupados:
            dados_mensais_agrupados[chave_mes] = {"Receita": 0.0, "Despesa": 0.0, "mes": int(mes), "ano": int(ano)}
        
        dados_mensais_agrupados[chave_mes][tipo_tx] += float(valor)
        
        # Agrupamento de Pizza (Gráfico 3 e 4)
        if tipo_tx == "Receita":
            dados_pizza_receita[categoria_nome] = dados_pizza_receita.get(categoria_nome, 0.0) + float(valor)
        else: # Despesa
            dados_pizza_despesa[categoria_nome] = dados_pizza_despesa.get(categoria_nome, 0.0) + float(valor)

    # ===============================
    # 4. PREPARAÇÃO DADOS PARA GRÁFICOS (12 MESES)
    # ===============================

    # LISTA ORDENADA DAS CHAVES (CORREÇÃO DE ORDENAÇÃO)
    chaves_ordenadas = sorted(dados_mensais_agrupados.keys(), key=lambda x: datetime.strptime(x, "%m/%Y"))

    fluxo_linha = []
    saldo_acumulado = saldo_inicial_projecao # Ponto de partida AGORA é o final do mês anterior
    saldo_investimento_acumulado = 0.0 

    for chave_mes in chaves_ordenadas:
        dados_mes = dados_mensais_agrupados[chave_mes]
        
        receita_mes = dados_mes["Receita"]
        despesa_mes = dados_mes["Despesa"]
        
        # Saldo Acumulado
        saldo_acumulado += (receita_mes - despesa_mes)
        
        # Projeção de Investimento: 15% da Receita do Mês
        investimento_sugerido = receita_mes * 0.15 
        
        # Saldo Investimento Acumulado
        saldo_investimento_acumulado += investimento_sugerido 
        
        fluxo_linha.append({
            "mes": chave_mes,
            "receita": receita_mes,
            "despesa": despesa_mes,
            "saldo": saldo_acumulado,
            "investimento_sugerido_acumulado": saldo_investimento_acumulado
        })

    # ===============================
    # 5. CÁLCULO DOS CARDS (Baseado no Filtro ou Mês Atual)
    # ===============================
    
    # Pega o mês/ano de hoje como default para os cards, se não houver filtro
    mes_card = int(filtro_mes) if filtro_mes else hoje.month
    ano_card = int(filtro_ano) if filtro_ano else hoje.year
    
    receita_card = 0.0
    despesa_card = 0.0
    
    # Soma a Receita e Despesa para o mês/ano selecionado (ou atual)
    for chave_mes, dados in dados_mensais_agrupados.items():
        if dados["mes"] == mes_card and dados["ano"] == ano_card:
            receita_card = dados["Receita"]
            despesa_card = dados["Despesa"]
            break

    # Determina o Saldo Acumulado para o Mês do Card
    saldo_acumulado_card = saldo_inicial_projecao
    for item in fluxo_linha:
        mes_projecao, ano_projecao = map(int, item["mes"].split('/'))
        if mes_projecao == mes_card and ano_projecao == ano_card:
            saldo_acumulado_card = item["saldo"]
            break
            
    # Último Saldo da Projeção para o card de "Saldo Projetado Final"
    saldo_final_projecao = fluxo_linha[-1]["saldo"] if fluxo_linha else saldo_inicial_projecao

    # Calcula Recomendação para o Card
    recomendacao_card = {}
    if receita_card > 0:
        recomendacao_card = {
            "necessidades": receita_card * 0.70,
            "desejos_sugerido": receita_card * 0.15,
            "investimentos_sugerido": receita_card * 0.15,
            "gasto_mensal_recomendado": receita_card * 0.85
        }
    else:
        recomendacao_card = {k: 0.0 for k in ["necessidades", "desejos_sugerido", "investimentos_sugerido", "gasto_mensal_recomendado"]}
        
    # ===============================
    # 6. RETORNO JSON FINAL
    # ===============================
    
    # Converte os dados de pizza para o formato final
    dados_pizza_receita = [{"categoria": c, "valor": float(v)} for c, v in dados_pizza_receita.items()]
    dados_pizza_despesa = [{"categoria": c, "valor": float(v)} for c, v in dados_pizza_despesa.items()]

    return jsonify({
        "cards": {
            "saldo_inicial_projecao": saldo_inicial_projecao,
            "receita_card": receita_card,
            "despesa_card": despesa_card,
            "resultado_card": receita_card - despesa_card,
            "saldo_acumulado_card": saldo_acumulado_card,
            "saldo_final_projecao": saldo_final_projecao
        },
        "dados_mensais_agrupados": dados_mensais_agrupados, 
        "fluxo_linha": fluxo_linha, 
        "pizza_receita": dados_pizza_receita,
        "pizza_despesa": dados_pizza_despesa,
        "recomendacoes_card": recomendacao_card,
        "meses_disponiveis": chaves_ordenadas
    })