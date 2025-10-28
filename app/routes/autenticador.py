from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app, session
from flask_login import current_user, login_user, logout_user
from app.models import Usuarios, KeyValidation
from app.extensions import mail, db, bcrypt
from flask.cli import load_dotenv
from flask_mail import Message
import random

auth_bp = Blueprint('auth', __name__)

# Rota para logar o usuário 
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == "GET":
        return render_template("usuario/login.html")
    
    if request.method == "POST":
        try:
            email       = request.form.get('email')
            password    = request.form.get('senha')
            usuario     = Usuarios.query.filter_by(email = email).first()

            if usuario and usuario.password_hash and bcrypt.check_password_hash(usuario.password_hash, password):
                login_user(usuario)
                current_app.logger.info(f'Usuario {email} realizou login com sucesso!')
            else:
                if not usuario:
                    flash('Usuário não encontrado!')

                elif not bcrypt.check_password_hash(usuario.password_hash, password):
                    flash('Senha incorreta!')

                return redirect(url_for('auth.login'))
            
            session.pop('_flashes', None)
            return redirect(url_for('main.menu'))

        except Exception as e:
            current_app.logger.error(f'Erro no login: {e}')
            flash('Erro inesperado, tente novamente...')
            return redirect(url_for('auth.login'))

 
# Rota para deslogar o usuário 
@auth_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    if request.method == 'GET':
        logout_user()
        session.pop('_flashes', None)
        return redirect(url_for('auth.login'))


# Rota para enviar o email de recuperação de senha
@auth_bp.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    if request.method == 'GET':
        return render_template("usuario/recuperar.html")

    if request.method == 'POST':
        destinatario = request.form.get('email')
        usuario = Usuarios.query.filter_by(email=destinatario).first()

        if not usuario:
            flash("E-mail não encontrado no sistema.")
            current_app.logger.warning(f"Tentativa de recuperação com e-mail inexistente: {destinatario}")
            return redirect(url_for('user.cadastroUsuario'))

        keyValidation = KeyValidation(
            usuario_id=usuario.id,
            Key=random.randint(0, 999999)
        )
        reset_link = url_for('auth.editar', user_id=usuario.id, keyValidation=str(keyValidation.Key), _external=True)

        corpo_email = f"""
        Olá, {usuario.nome}!

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
            return redirect(url_for('auth.login'))

        except Exception as e:
            flash("Erro ao enviar o email.")
            current_app.logger.error('Erro ao enviar o email')
            return render_template('recuperar.html')


# Rota para cadastrar uma nova senha 
@auth_bp.route('/editar/<int:user_id>/<int:keyValidation>', methods=['GET', 'POST'])
def editar(user_id, keyValidation):
    
    if request.method == 'GET':
        return render_template("usuario/senhaNova.html", user_id=user_id, keyValidation=keyValidation)
    
    if request.method == 'POST':
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
                return redirect(url_for('auth.login'))
            else:
                flash('As senhas não são iguais')
        else:
            flash('Os códigos de validação não são iguais')

        # se não atualizar senha, volta para o form
        return render_template('senhaNova.html', user_id=user_id, keyValidation=keyValidation)
