from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app, session
from flask_login import login_user, logout_user
from app.models import Usuarios, KeyValidation
from app.extensions import mail, db, bcrypt
from flask_mail import Message
import random

auth_bp = Blueprint('auth', __name__)

# -----------------------
# Login
# -----------------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template("usuario/login.html")

    if request.method == "POST":
        try:
            email = request.form.get('email')
            password = request.form.get('senha')
            usuario = Usuarios.query.filter_by(email=email).first()

            if usuario and usuario.password_hash and bcrypt.check_password_hash(usuario.password_hash, password):
                login_user(usuario)
                current_app.logger.info(f'Usuario {email} realizou login com sucesso!')
                session.pop('_flashes', None)
                return redirect(url_for('main.menu'))
            else:
                if not usuario:
                    flash('Usuário não encontrado!', 'error')
                else:
                    flash('Senha incorreta!', 'error')
                return redirect(url_for('auth.login'))

        except Exception as e:
            flash('Ocorreu algum erro inesperado', 'error')
            current_app.logger.error(f'Erro no login: {e}')
            return redirect(url_for('auth.login'))

# -----------------------
# Logout
# -----------------------
@auth_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    session.pop('_flashes', None)
    return redirect(url_for('auth.login'))


# -----------------------
# Envio do e-mail de recuperação
# -----------------------
@auth_bp.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha_email():
    if request.method == 'GET':
        return render_template("usuario/recuperar.html")

    if request.method == 'POST':
        destinatario = request.form.get('email')
        usuario = Usuarios.query.filter_by(email=destinatario).first()

        if not usuario:
            flash("E-mail não encontrado no sistema.", 'error')
            current_app.logger.warning(f"Tentativa de recuperação com e-mail inexistente: {destinatario}")
            return redirect(url_for('user.cadastroUsuario'))

        # Cria código de validação e salva no DB
        keyValidation = KeyValidation(
            usuario_id=usuario.id,
            key_value=random.randint(100000, 999999)
        )
        db.session.add(keyValidation)
        db.session.commit()

        # Cria link para redefinir senha
        reset_link = url_for(
            'auth.recuperar_senha_editar',
            user_id=usuario.id,
            keyValidation=str(keyValidation.key_value),
            _external=True
        )

        # 1. Preparar o corpo do e-mail em texto simples (fallback)
        corpo_email_text = f"""
        Olá, {usuario.nome}!

        Recebemos uma solicitação para redefinir sua senha no sistema Monevo.
        Para continuar, acesse o link abaixo:

        {reset_link}

        Se não foi você que pediu, ignore este e-mail.
        """
        
        # 2. Renderizar o template HTML (usando Jinja2)
        corpo_email_html = render_template(
            'email/email_recuperacao.html',
            usuario=usuario, 
            reset_link=reset_link,
            current_year=datetime.now().year
        )

        try:
            msg = Message(
                subject="Recuperação de Senha - Monevo",
                recipients=[destinatario],
                body=corpo_email_text,
                html=corpo_email_html
            )
            mail.send(msg)

            flash("Email enviado com sucesso! Verifique sua caixa de entrada.", 'success')
            current_app.logger.info('Email de recuperação enviado com sucesso')
            return redirect(url_for('auth.login'))

        except Exception as e:
            flash('Ocorreu algum erro inesperado ao enviar o email. Tente novamente.', 'error')
            current_app.logger.error(f'Erro ao enviar o email: {e}')
            return render_template('usuario/recuperar.html')


# -----------------------
# Redefinir senha via link enviado
# -----------------------
@auth_bp.route('/recuperar_senha/<int:user_id>', methods=['GET', 'POST'])
def recuperar_senha_editar(user_id):
    # Captura o código da URL (keyValidation)
    codigo_url = request.args.get('keyValidation', None)

    if request.method == 'GET':
        # Renderiza formulário para redefinição de senha
        return render_template(
            'usuario/recuperarSenha.html',
            user_id=user_id,
            keyValidation=codigo_url
        )

    if request.method == 'POST':
        # Captura dados do formulário
        codigo_enviado = request.form.get('codigo')
        new_password = request.form.get('senha')
        confirm_new_password = request.form.get('senha_confirmacao')

        # Converte o código para inteiro (se possível)
        try:
            codigo_int = int(codigo_enviado)
        except (TypeError, ValueError):
            flash('Código inválido', 'error')
            return render_template(
                'usuario/recuperarSenha.html',
                user_id=user_id,
                keyValidation=codigo_enviado
            )

        # Busca a validação no banco
        confirmKeyValidation = KeyValidation.query.filter_by(
            usuario_id=user_id,
            key_value=codigo_int
        ).first()

        if not confirmKeyValidation:
            flash('Código de validação inválido', 'error')
            return render_template(
                'usuario/recuperarSenha.html',
                user_id=user_id,
                keyValidation=codigo_enviado
            )

        # Confere se as senhas coincidem
        if new_password != confirm_new_password:
            flash('As senhas não são iguais', 'error')
            return render_template(
                'usuario/recuperarSenha.html',
                user_id=user_id,
                keyValidation=codigo_enviado
            )

        # Atualiza a senha do usuário
        usuario = Usuarios.query.get(user_id)
        usuario.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()

        # Remove o código de validação usado
        db.session.delete(confirmKeyValidation)
        db.session.commit()

        flash('Senha atualizada com sucesso! Faça login.', 'success')
        current_app.logger.info(f'Senha do usuário {usuario.email} atualizada com sucesso')
        return redirect(url_for('auth.login'))
