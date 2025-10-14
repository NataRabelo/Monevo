from flask import Blueprint, flash, render_template, request, current_app, redirect, url_for
from app.services.registrar_requisicao import registrar_requisicao
from flask_login import current_user, logout_user
from app.models import Usuarios
from app import bcrypt, db

user_bp = Blueprint('user', __name__, url_prefix='/usuario')


@user_bp.route('/cadastrar', methods=["POST", "GET"])
def cadastroUsuario():
    if request.method == "GET":
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
                return redirect(url_for('auth.login'))
            if validar_cpf :
                flash('CPF já associado a uma conta', 'warning')
                current_app.logger.info('CPF já associado a uma conta')
                return redirect(url_for('auth.login'))
            else:
                new_usuario = Usuarios(
                    nome            = nome,
                    sobrenome       = sobrenome,
                    email           = email,
                    celular         = celular,
                    cpf             = cpf,
                    password_hash   = password_hash
                )

                db.session.add(new_usuario)
                db.session.commit()

                flash('Cadastro realizado com sucesso.', 'success')
                current_app.logger.info(f'Usuario cadastrado com sucesso: {email}')

                return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            flash('Ocorreu algum erro inesperado')
            current_app.logger.warning(f'Erro ao cadastrar usuário: {e}')
            return redirect(url_for('main.menu'))

@user_bp.route('/editar/', methods=['GET', 'POST'])
def editarUsuario():
    try:
        user_id = current_user.id
        usuario = Usuarios.query.filter(Usuarios.id == user_id).first()

        if not usuario:
            flash('Usuário não encontrado.')
            return redirect(url_for('main.menu'))

        if request.method == "GET":
            return render_template("usuario/editar.html", usuario=usuario)

        if request.method == "POST":
            usuario.nome        = request.form.get('nome') or usuario.nome
            usuario.sobrenome   = request.form.get('sobrenome') or usuario.sobrenome
            usuario.email       = request.form.get('email') or usuario.email
            usuario.celular     = request.form.get('celular') or usuario.celular
            usuario.cpf         = request.form.get('cpf') or usuario.cpf

            senha = request.form.get('senha', '').strip()
            if senha:
                usuario.senha   = bcrypt.generate_password_hash(senha).decode('utf-8')

            db.session.commit()
            flash('Usuário editado com sucesso!')
            return redirect(url_for('main.menu'))

    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado')
        current_app.logger.warning(f'Erro ao editar usuário: {e}')
        return redirect(url_for('main.menu'))

@user_bp.route('/deletar/', methods=['GET', 'POST'])
def deletarUsuario():
    try:
        
        user_id = current_user.id
        usuario = Usuarios.query.filter(Usuarios.id == user_id).first()

        if not usuario:
            flash('Usuário não encontrado')
            return redirect(url_for('main.menu'))
        
        if request.method == "GET":
            return render_template('usuario/deletar.html')
        
        if request.method == "POST":
            logout_user()
            db.session.delete(usuario)
            db.session.commit()
            flash('Sua conta foi excluída com sucesso.')
            return redirect(url_for('auth.login'))

    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado')
        current_app.logger.warning(f'Erro ao deletar usuario: {e}')
        return redirect(url_for('main.menu'))

@user_bp.route('/listar', methods=['GET', 'POST'])
def listarUsuario():
    try:
        usuarios = Usuarios.query.all()

        if not usuarios:
            flash('Nenhum usuário cadastrado no sistema')
            return redirect(url_for('usuario.cadastrar'))
        
        if request.method == "GET":
            render_template('usuario/listar.html', usuarios = usuarios)
        
    except Exception as e:
        flash('Ocorreu algum erro inesperado')
        current_app.logger.warning(f'erro ao listar usuários: {e}')
        return redirect(url_for('main.menu'))