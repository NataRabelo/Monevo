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
        
        if request.method == "GET":
            return render_template('categoria/editar')
        
        if request.method == "POST":
            # Passando os dados alterados ( or not )
            categoria.nome  = request.form.get('nome') or categoria.nome
            categoria.tipo  = request.form.get('tipo') or categoria.tipo

            # Passando para o banco
            db.session.commit()
            flash('Categoria atualizada com sucesso')
            return redirect(url_for('categoria.AcessarCategoria'))

    except Exception as e:
        db.session.rollback
        flash('Ocorreu algum erro inesperado')
        current_app.logger.warning(f'Erro ao editar categoria: {e}')
        return redirect(url_for('main.menu'))


@categoria_bp.route('/deletar/<int:categoria_id>', methds=["GET", "POST"])
def deletarCategoria(categoria_id):
    try:
        # Valida a existencia
        categoria = Categorias.query.filter(Categorias.id == categoria_id).first()

        if not categoria:
            flash('Categoria não encontrada')
            return redirect(url_for('categoria.acessarCategoria'))
        
        if request.method == "POST":
            # Deleta do banco
            db.session.delete(categoria)
            db.session.commit()
            flash('Categoria excluida com sucesso')
            return redirect(url_for('cateegoria.acessarCategoria'))
        
    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado')
        current_app.logger.warning(f'Erro ao deletar categoria: {e}')
        return redirect(url_for('categoria.acessarConta'))
    

@categoria_bp.route('/listar', methods=['GET', 'POST'])
def listarCategoria():
    try:
        # Busca todos os objetos
        categorias = Categorias.query.all()

        if not categorias:
            flash('Nenhuma categoria cadastrada')
            return redirect(url_for(categorias.acessarCategoria))
        
        if request.method == "GET":
            # Retorna com a lista
            return render_template('categoria/listar.html', categorias=categorias)
        
    except Exception as e:
        flash('Ocorreu algum erro inesperado')
        current_app.logger.warning(f'Erro ao listar categorias: {e}')
        return redirect(url_for('categoria.acessarCategoria'))