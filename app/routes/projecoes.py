from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Transacoes, Contas, Categorias
from sqlalchemy import func, extract, case
from datetime import datetime

projecao_bp = Blueprint('projecao', __name__, url_prefix='/projecao')

@projecao_bp.route('/', methods=['GET', 'POST'])
def acessarProjecao():
    if request.method == "GET":
        return render_template('dashboard/projecao.html')

# ===========================
#     ROTA PRINCIPAL JSON
# ===========================
@projecao_bp.route("/dados", methods=["GET"])
@login_required
def obter_dados_projecao():
    # -----------------------
    # Parâmetros recebidos
    # -----------------------
    data_inicio = request.args.get("inicio")
    data_fim = request.args.get("fim")
    tipo = request.args.get("tipo")  # mensal, semanal, anual

    # Conversão
    data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d").date()
    data_fim = datetime.strptime(data_fim, "%Y-%m-%d").date()

    # ===============================
    # 1) SALDO DO MÊS ANTERIOR
    # ===============================
    saldo_inicial = 0

    contas = db.session.query(Contas).filter_by(usuario_id=current_user.id).all()
    for c in contas:
        saldo_inicial += c.saldo_inicial

    mov_anterior = db.session.query(
        func.sum(
            case(
                (Transacoes.tipo == "Receita", Transacoes.valor),
                else_=-Transacoes.valor
            )
        )
    ).filter(
        Transacoes.usuario_id == current_user.id,
        Transacoes.data_transacao < data_inicio
    ).scalar() or 0

    saldo_anterior = saldo_inicial + mov_anterior

    # ===============================
    # 2) RECEITAS PROJETADAS
    # ===============================
    receitas = db.session.query(
        func.sum(Transacoes.valor)
    ).filter(
        Transacoes.usuario_id == current_user.id,
        Transacoes.tipo == "Receita",
        Transacoes.data_transacao.between(data_inicio, data_fim)
    ).scalar() or 0

    # ===============================
    # 3) DESPESAS PROJETADAS
    # ===============================
    despesas = db.session.query(
        func.sum(Transacoes.valor)
    ).filter(
        Transacoes.usuario_id == current_user.id,
        Transacoes.tipo == "Despesa",
        Transacoes.data_transacao.between(data_inicio, data_fim)
    ).scalar() or 0

    resultado = receitas - despesas

    # ===============================
    # 4) GRÁFICO 1 – Receitas x Despesas por período
    # ===============================
    graf1 = db.session.query(
        extract('year', Transacoes.data_transacao).label("ano"),
        extract('month', Transacoes.data_transacao).label("mes"),
        Transacoes.tipo,
        func.sum(Transacoes.valor).label("total"),
    ).filter(
        Transacoes.usuario_id == current_user.id,
        Transacoes.data_transacao.between(data_inicio, data_fim)
    ).group_by("ano", "mes", Transacoes.tipo).order_by("ano", "mes").all()

    dados_barra = {}
    for ano, mes, tipo_tx, total in graf1:
        chave = f"{int(mes):02}/{int(ano)}"
        if chave not in dados_barra:
            dados_barra[chave] = {"Receita": 0, "Despesa": 0}
        dados_barra[chave][tipo_tx] = float(total)

    # ===============================
    # 5) GRÁFICO 2 – Pizza (proporção)
    # ===============================
    graf2 = db.session.query(
        Categorias.nome,
        func.sum(Transacoes.valor)
    ).join(Categorias, Categorias.id == Transacoes.categoria_id)\
    .filter(
        Transacoes.usuario_id == current_user.id,
        Transacoes.data_transacao.between(data_inicio, data_fim)
    ).group_by(Categorias.nome).all()

    dados_pizza = [{"categoria": c, "valor": float(v)} for c, v in graf2]

    # ===============================
    # 6) GRÁFICO 3 – Fluxo de Caixa
    # ===============================
    graf3 = db.session.query(
        Transacoes.data_transacao,
        func.sum(
            case(
                (Transacoes.tipo == "Receita", Transacoes.valor),
                else_=-Transacoes.valor
            )
        )
    ).filter(
        Transacoes.usuario_id == current_user.id,
        Transacoes.data_transacao.between(data_inicio, data_fim)
    ).group_by(
        Transacoes.data_transacao
    ).order_by(
        Transacoes.data_transacao
    ).all()

    saldo = saldo_anterior
    fluxo = []
    for data, valor in graf3:
        saldo += float(valor)
        fluxo.append({
            "data": data.strftime("%Y-%m-%d"),
            "saldo": saldo
        })

    # ===============================
    # RETORNO JSON FINAL
    # ===============================
    return jsonify({
        "cards": {
            "saldo_anterior": saldo_anterior,
            "receitas": receitas,
            "despesas": despesas,
            "resultado": resultado,
        },
        "barra": dados_barra,
        "pizza": dados_pizza,
        "linha": fluxo,
    })
