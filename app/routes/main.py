from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from app.models import Transacoes
from flask.cli import load_dotenv
from app.extensions import db
from datetime import datetime


load_dotenv()

main_bp = Blueprint('main', __name__)

# -------------------------------------
# Rota inicial redirecionando para login
# -------------------------------------
@main_bp.route('/')
def index():
    return redirect(url_for('auth.login'))

        
# -------------------------------------
# Rota do menu principal
# -------------------------------------
@main_bp.route('/menu', methods=['POST', 'GET'])
@login_required
def menu():
    if request.method == 'GET':
        usuario = current_user
        
        hoje = datetime.now()
        mes_atual = hoje.month
        ano_atual = hoje.year

        # --- NOVA LÓGICA DE FILTRAGEM ---
        # Garantir que apenas as transações *filhas* ou *únicas* (parcela_atual > 0) sejam somadas.
        # Transações mestras (parcela_atual = 0) contêm o valor total da série e devem ser excluídas.
        
        # 1. Total Receita do Mês
        total_receita_mes = db.session.query(
            db.func.sum(Transacoes.valor)
        ).filter(
            Transacoes.tipo == "Receita",
            Transacoes.usuario_id == current_user.id,
            db.func.extract('month', Transacoes.data_transacao) == mes_atual,
            db.func.extract('year', Transacoes.data_transacao) == ano_atual,
            Transacoes.parcela_atual > 0 # <--- FILTRO CHAVE ADICIONADO
        ).scalar() or 0

        # 2. Total Despesa do Mês
        total_despesa_mes = db.session.query(
            db.func.sum(Transacoes.valor)
        ).filter(
            Transacoes.tipo == "Despesa",
            Transacoes.usuario_id == current_user.id,
            db.func.extract('month', Transacoes.data_transacao) == mes_atual,
            db.func.extract('year', Transacoes.data_transacao) == ano_atual,
            Transacoes.parcela_atual > 0 # <--- FILTRO CHAVE ADICIONADO
        ).scalar() or 0
        
        # ... restante da função ...
        resultado_mes = total_receita_mes - total_despesa_mes
        
        return render_template('dashboard/menu.html', 
                               usuario = usuario, 
                               total_despesa_mes = total_despesa_mes,
                               total_receita_mes = total_receita_mes,
                               resultado_mes = resultado_mes
                               )