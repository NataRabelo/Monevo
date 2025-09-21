from flask import Blueprint, flash, render_template, request, current_app, redirect, url_for
from app.services.registrar_requisicao import registrar_requisicao
from app.models import Usuarios
from app import bcrypt, db

user_bp = Blueprint('user', __name__, url_prefix='/usuario')


@user_bp.route('/cadastro', methods=["POST", "GET"])
def cadastroUsuario():
    if request.method == "GET":
        # apenas exibe o formulário
        return render_template("cadastro.html")

    if request.method == "POST":
        try:
            nome_completo = request.form.get('nome')
            email = request.form.get('email')
            password = request.form.get('senha')

            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            validar_email = Usuarios.query.filter_by(email=email).first()
            
            if validar_email:
                flash('Email já associado a uma conta', 'warning')
                current_app.logger.info(f'Email já associado a uma conta: {email}')
                return redirect(url_for('main.login'))
            else:
                new_usuario = Usuarios(
                    nome_completo=nome_completo,
                    email=email,
                    password_hash=password_hash
                )

                db.session.add(new_usuario)
                db.session.commit()

                flash('Cadastro realizado com sucesso!!', 'success')
                current_app.logger.info(f'Usuario cadastrado com sucesso: {email}')

                return redirect(url_for('main.login'))

        except Exception as e:
            current_app.logger.error(f"Erro ao tentar cadastrar novo usuario: {e}", exc_info=True)
            registrar_requisicao(request, 500, 'erro enviado')
            return {"erro": "Falha ao cadastrar usuario"}, 500


@user_bp.route('/editar', methods=['GET', 'POST'])
def editarUsuario():
    return 0

@user_bp.errorhandler(500)
def erro_interno(detalhe):
    current_app.logger.exception("Erro interno do servidor")
    registrar_requisicao(request, 500, "erro interno")
    return {"erro": "Erro interno do servidor"}, 500
