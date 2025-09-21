import random
from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app
from flask_login import current_user, login_user, logout_user
from flask.cli import load_dotenv
from app.extensions import mail, db, bcrypt
from flask_mail import Message
from app.models import Usuarios, KeyValidation

load_dotenv()

import smtplib
from email.mime.text import MIMEText

main_bp = Blueprint('main', __name__)

# Rota de abertura do sistema 
@main_bp.route('/')
def index():
    return redirect(url_for('main.login'))

# Rota para login no sistema
@main_bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == "GET":
        return render_template('login.html')
    
    if request.method == "POST":

        try:
            email   = request.form.get('email')
            password   = request.form.get('senha')

            usuario = Usuarios.query.filter_by(email = email).first()

            if usuario and usuario.password_hash and bcrypt.check_password_hash(usuario.password_hash, password):
                login_user(usuario)
                flash('Login realizado!')
                current_app.logger.info(f'Usuario {email} realizou login com sucesso!')
            else:
                if not usuario:
                    flash('Usuário  encontrado!')
                    current_app.logger.info('Usuario nao encontrado')
                elif not bcrypt.check_password_hash(usuario.password_hash, password):
                    flash('Senha incorreta!')
                    current_app.logger.info('Senha informada nao e a correta')
                current_app.logger.info('Usuario nao cadastrado, redirecionamento realziado')
                return redirect(url_for('main.login'))
            
            return redirect(url_for('main.menu'))

        except Exception as e:
            current_app.logger.error(f'Erro no login: {e}')
            flash('Erro inesperado, tente novamente.')
            return redirect(url_for('main.login'))
        
# Rota para deslogar o usuário 
@main_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    if request.method == 'GET':
        current_app.logger.info('Usuario deslogado do sistema')
        logout_user()
        return redirect(url_for('main.login'))

# Rota para enviar o email de recuperação de senha
@main_bp.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    if request.method == 'GET':
        return render_template('recuperar.html')

    elif request.method == 'POST':
        destinatario = request.form.get('email')
        print(destinatario)
        usuario = Usuarios.query.filter_by(email=destinatario).first()

        if not usuario:
            flash("E-mail não encontrado no sistema.")
            current_app.logger.warning(f"Tentativa de recuperação com e-mail inexistente: {destinatario}")
            return redirect(url_for('user.cadastrar'))

        keyValidation = KeyValidation(
            usuario_id=usuario.id,
            Key=random.randint(0, 999999)
        )
        reset_link = url_for('main.editar', user_id=usuario.id, keyValidation=str(keyValidation.Key), _external=True)

        corpo_email = f"""
        Olá, {usuario.nome_completo}!

        Recebemos uma solicitação para redefinir sua senha.
        Para continuar, acesse o link abaixo:

        {reset_link}

        Se não foi você que pediu, ignore este email.
        """

        try:
            msg = Message(
                subject="Recuperação de Senha",
                recipients=[destinatario],
                body=corpo_email
            )
            mail.send(msg)

            db.session.add(keyValidation)
            db.session.commit()

            flash("Email enviado com sucesso!")
            current_app.logger.info('Email enviado com sucesso')
            return redirect(url_for('main.login'))

        except Exception as e:
            flash("Erro ao enviar o email.")
            current_app.logger.error('Erro ao enviar o email')
            return render_template('recuperar.html')

        
# Rota para cadastrar uma nova senha 
@main_bp.route('/editar/<int:user_id>/<int:keyValidation>', methods=['GET', 'POST'])
def editar(user_id, keyValidation):
    
    if request.method == 'GET':
        return render_template('senhaNova.html', user_id=user_id, keyValidation=keyValidation)
    
    elif request.method == 'POST':
        current_app.logger.info('Entrou dentro da chamada de recuperação de senha')
        confirmKeyValidation = KeyValidation.query.filter_by(usuario_id=user_id).first()

        if confirmKeyValidation and confirmKeyValidation.Key == keyValidation:
            new_password = request.form.get('senha')
            confirm_new_password = request.form.get('senha_confirmacao')
            current_app.logger.info('O código enviado no email corresponde com o do banco de dados')

            if new_password == confirm_new_password:
                current_app.logger.info('As senhas informadas são iguais')
                confirmed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

                new_usuario = Usuarios.query.filter_by(id=user_id).first()
                new_usuario.password_hash = confirmed_password

                db.session.commit()
                flash('Senha atualizada com sucesso')
                current_app.logger.info('Senha atualizada com sucesso ')
                db.session.delete(confirmKeyValidation)
                db.session.commit()
                return redirect(url_for('main.login'))
            else:
                flash('As senhas não são iguais')
        else:
            flash('Os códigos de validação não são iguais')

        # se não atualizar senha, volta para o form
        return render_template('senhaNova.html', user_id=user_id, keyValidation=keyValidation)

# Rota para chamar o menu e passar parâmetros para aparesentação
@main_bp.route('/menu', methods=['POST', 'GET'])
def menu():
    if request.method == 'GET':
        usuario = current_user
        return render_template('menu.html', usuario=usuario, total_receitas=3500, total_despesas=1500, diferenca=2000)