from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Transacoes, Contas, Categorias, SaldoInicial
from sqlalchemy import func, extract, case
from datetime import datetime
from dateutil.relativedelta import relativedelta

projecao_bp = Blueprint('projecao', __name__, url_prefix='/projecao')

@projecao_bp.route('/', methods=['GET', 'POST'])
@login_required
def acessarProjecao():
    if request.method == "GET":
        return render_template('dashboard/projecao.html')

@projecao_bp.route("/dados", methods=["GET"])
@login_required
def obter_dados_projecao():
    usuario_id = current_user.id
    hoje = datetime.now().date()

    # 1. Definição do período da projeção: 12 meses
    data_inicio_projecao = hoje.replace(day=1)
    meses_projecao = [data_inicio_projecao + relativedelta(months=i) for i in range(12)]

    # Filtro opcional para cards
    filtro_mes = request.args.get("mes")
    filtro_ano = request.args.get("ano")
    mes_card = int(filtro_mes) if filtro_mes else hoje.month
    ano_card = int(filtro_ano) if filtro_ano else hoje.year

    # 2. Saldo inicial
    saldo_inicial_contas = db.session.query(func.sum(SaldoInicial.saldo_inicial))\
        .filter_by(usuario_id=usuario_id).scalar() or 0

    mov_anterior = db.session.query(
        func.sum(
            case((Transacoes.tipo == "Receita", Transacoes.valor), else_=-Transacoes.valor)
        )
    ).filter(
        Transacoes.usuario_id == usuario_id,
        Transacoes.data_transacao < data_inicio_projecao,
        Transacoes.parcela_atual != 0
    ).scalar() or 0

    # Receitas do mês inicial já incluídas no saldo real
    receitas_mes_atual_incluidas = db.session.query(
        func.sum(Transacoes.valor)
    ).filter(
        Transacoes.usuario_id == usuario_id,
        Transacoes.tipo == "Receita",
        Transacoes.receita_ja_incluida == True,
        Transacoes.parcela_atual != 0,
        extract('month', Transacoes.data_transacao) == data_inicio_projecao.month,
        extract('year', Transacoes.data_transacao) == data_inicio_projecao.year
    ).scalar() or 0

    saldo_inicial_projecao = float(saldo_inicial_contas) + float(mov_anterior) - float(receitas_mes_atual_incluidas)

    # 3. Consulta de transações no período de 12 meses
    data_fim_projecao = meses_projecao[-1] + relativedelta(day=31)  # último dia do último mês
    dados_transacoes = db.session.query(
        extract('year', Transacoes.data_transacao).label("ano"),
        extract('month', Transacoes.data_transacao).label("mes"),
        Transacoes.tipo,
        Transacoes.valor,
        Categorias.nome.label("categoria_nome"),
        Transacoes.receita_ja_incluida
    ).join(Categorias, Categorias.id == Transacoes.categoria_id)\
     .filter(
        Transacoes.usuario_id == usuario_id,
        Transacoes.data_transacao.between(data_inicio_projecao, data_fim_projecao),
        Transacoes.parcela_atual != 0
     ).all()

    # 4. Preparar estrutura mensal completa
    dados_mensais_agrupados = {}
    dados_pizza_receita = {}
    dados_pizza_despesa = {}

    for mes_data in meses_projecao:
        chave = mes_data.strftime("%m/%Y")
        dados_mensais_agrupados[chave] = {"Receita": 0.0, "Despesa": 0.0, "mes": mes_data.month, "ano": mes_data.year}

    mes_inicio = data_inicio_projecao.month
    ano_inicio = data_inicio_projecao.year

    for ano, mes, tipo_tx, valor, categoria_nome, receita_flag in dados_transacoes:
        # Ignora receita já incluída no saldo real do mês inicial

        chave_mes = f"{int(mes):02}/{int(ano)}"
        dados_mensais_agrupados[chave_mes][tipo_tx] += float(valor)

        if tipo_tx == "Receita":
            dados_pizza_receita[categoria_nome] = dados_pizza_receita.get(categoria_nome, 0.0) + float(valor)
        else:
            dados_pizza_despesa[categoria_nome] = dados_pizza_despesa.get(categoria_nome, 0.0) + float(valor)

    # 5. Fluxo de linha e saldo acumulado
    chaves_ordenadas = sorted(dados_mensais_agrupados.keys(), key=lambda x: datetime.strptime(x, "%m/%Y"))
    fluxo_linha = []
    saldo_acumulado = saldo_inicial_projecao
    saldo_investimento_acumulado = 0.0

    for chave_mes in chaves_ordenadas:
        dados_mes = dados_mensais_agrupados[chave_mes]
        receita_mes = dados_mes["Receita"]
        despesa_mes = dados_mes["Despesa"]
        saldo_acumulado += (receita_mes - despesa_mes)
        investimento_sugerido = receita_mes * 0.15
        saldo_investimento_acumulado += investimento_sugerido
        fluxo_linha.append({
            "mes": chave_mes,
            "receita": receita_mes,
            "despesa": despesa_mes,
            "saldo": saldo_acumulado,
            "investimento_sugerido_acumulado": saldo_investimento_acumulado
        })

    # 6. Cards
    dados_card = dados_mensais_agrupados.get(f"{mes_card:02}/{ano_card}", {"Receita": 0.0, "Despesa": 0.0})
    receita_card = dados_card["Receita"]
    despesa_card = dados_card["Despesa"]

    saldo_acumulado_card = saldo_inicial_projecao
    for item in fluxo_linha:
        mes_projecao, ano_projecao = map(int, item["mes"].split('/'))
        if mes_projecao == mes_card and ano_projecao == ano_card:
            saldo_acumulado_card = item["saldo"]
            break

    saldo_final_projecao = fluxo_linha[-1]["saldo"] if fluxo_linha else saldo_inicial_projecao

    recomendacao_card = {
        "necessidades": receita_card * 0.70,
        "desejos_sugerido": receita_card * 0.15,
        "investimentos_sugerido": receita_card * 0.15,
        "gasto_mensal_recomendado": receita_card * 0.85
    } if receita_card > 0 else {k: 0.0 for k in ["necessidades", "desejos_sugerido", "investimentos_sugerido", "gasto_mensal_recomendado"]}

    # 7. Retorno JSON
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
        "pizza_receita": [{"categoria": c, "valor": float(v)} for c, v in dados_pizza_receita.items()],
        "pizza_despesa": [{"categoria": c, "valor": float(v)} for c, v in dados_pizza_despesa.items()],
        "recomendacoes_card": recomendacao_card,
        "meses_disponiveis": chaves_ordenadas
    })
