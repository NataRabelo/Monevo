from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app
from flask_login import current_user, login_user, logout_user
from app.models import Transacoes, Usuarios, KeyValidation
from app.extensions import mail, db, bcrypt
from flask.cli import load_dotenv
from flask_mail import Message
import random


load_dotenv()

main_bp = Blueprint('main', __name__)

# Rota index do sistema ( redireciona para o login )
@main_bp.route('/')
def index():
    return redirect(url_for('auth.login'))

        
# Chamada de menu do sistema
@main_bp.route('/menu', methods=['POST', 'GET'])
def menu():
    if request.method == 'GET':
        usuario = current_user

        total_receita = db.session.query(
            db.func.sum(Transacoes.valor)
        ).filter(
            Transacoes.tipo == "Receita",
            Transacoes.usuario_id == current_user.id
        ).scalar() or 0

        total_despesa = db.session.query(
            db.func.sum(Transacoes.valor)
        ).filter(
            Transacoes.tipo == "Despesa",
            Transacoes.usuario_id == current_user.id
        ).scalar() or 0
        
        return render_template('dashboard/menu.html', 
                               usuario          =usuario, 
                               total_despesa    =total_despesa,
                               total_receita    =total_receita,
                               resultado        = total_receita - total_despesa
                               )