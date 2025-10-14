from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app
from flask_login import current_user, login_user, logout_user
from app.models import Usuarios, KeyValidation
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
        return render_template('dashboard/menu.html', 
                               usuario          =usuario, 
                               total_receitas   =3500, 
                               total_despesas   =1500, 
                               diferenca        =2000
                               )