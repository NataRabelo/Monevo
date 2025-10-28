from flask import Blueprint, current_app, render_template, request, flash, redirect, url_for
from app.models import Categorias
from flask_login import current_user
from app import db

categoria_bp = Blueprint('categoria', __name__, url_prefix='/categoria')

@categoria_bp.route('/cadastrar', method=['GET', 'POST'])
def cadastrarCategoria():
    try:
        usuario = current_user

        # Buscar dados
        usuario     = usuario
        nome        = request.form.get('nome')
        tipo        = request.form.get('tipo')

        # Verificação

        # Criando o objeto Categoria
        new_categoria = Categorias(
            usuario_id      = usuario,
            nome            = nome,
            tipo            = tipo
        )

        # Adiciona ao banco
        db.session.add(new_categoria)
        db.session.commit()

        # Notificação + log 
        flash(f'Categoria {nome}, cadastrada com sucesso')
        current_app.logger.info(f'Categoria cadastrada com sucesso: {nome} - {tipo}')

        return redirect(url_for('main.menu'))
    
    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado')
        current_app.logger.warning(f'Erro ao cadastrar a categoria: {e}')
        return redirect(url_for('main.menu'))
    

@categoria_bp.route('/editar/<int:categoria_id>', methods=['GET', 'POST'])
def editarCategoria(categoria_id):
    try:
        # Validar a existencia da categoria
        categoria = Categorias.query.filter(Categorias.id == categoria_id).first()

        if not categoria:
            flash('Categoria não encontrada')
            return redirect(url_for('main.menu'))

    except Exception as e:
        return 0