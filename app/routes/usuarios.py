from flask import Blueprint, flash, render_template, request, current_app, redirect, url_for
from app.services.registrar_requisicao import registrar_requisicao
from app.models import Usuarios
from app import bcrypt, db

user_bp = Blueprint('user', __name__, url_prefix='/usuario')


@user_bp.route('/cadastro', methods=["POST", "GET"])
def cadastroUsuario():
    if request.method == "GET":
        # apenas exibe o formulário
        return render_template("usuario/cadastro.html")

    if request.method == "POST":
        try:
            nome            = request.form.get('nome')
            sobrenome       = request.form.get('sobrenome')
            email           = request.form.get('email')
            celular         = request.form.get('celular')
            cpf             = request.form.get('cpf')
            password        = request.form.get('senha')

            password_hash   = bcrypt.generate_password_hash(password).decode('utf-8')
            validar_email   = Usuarios.query.filter_by(email=email).first()
            validar_cpf     = Usuarios.query.filter_by(cpf=cpf).first()
            
            if validar_email:
                flash('Email já associado a uma conta', 'warning')
                current_app.logger.info(f'Email já associado a uma conta: {email}')
                return redirect(url_for('main.login'))
            if validar_cpf :
                flash('CPF já associado a uma conta', 'warning')
                current_app.logger.info('CPF já associado a uma conta')
                return redirect(url_for('main.login'))
            else:
                new_usuario = Usuarios(
                    nome            = nome,
                    sobrenome       = sobrenome,
                    email           = email,
                    celular         = celular,
                    cpf             = cpf,
                    password_hash   =password_hash
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
    if request.method == "GET":
        current_app.logger.info('Tela de edicao de usuario')
        return render_template("usuario/editar.html")
    
    if request.method == "POST":
        try:
            usuario = Usuarios.query.filter(id=id)  

            new_nome = request.form.get('nome')
            new_email = request.form.get('email')
            
            if new_nome == None:
                new_nome == usuario.nome_completo
                return 0
        except Exception as e:
            return 0 

    

@user_bp.errorhandler(500)
def erro_interno(detalhe):
    current_app.logger.exception("Erro interno do servidor")
    registrar_requisicao(request, 500, "erro interno")
    return {"erro": "Erro interno do servidor"}, 500
