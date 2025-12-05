from flask import Blueprint, current_app, render_template, request, flash, redirect, url_for
from app.models import Categorias
from flask_login import current_user
from app import db

categoria_bp = Blueprint('categoria', __name__, url_prefix='/categoria')

@categoria_bp.route('/cadastrar', methods=['POST'])
def cadastrarCategoria():
    try:
        if request.method == "POST":
            usuario = current_user
            nome = request.form.get('nome')
            tipo = request.form.get('tipo')

            new_categoria = Categorias(
                usuario_id=usuario.id,
                nome=nome,
                tipo=tipo
            )

            db.session.add(new_categoria)
            db.session.commit()

            flash(f'Categoria {nome} cadastrada com sucesso')
            current_app.logger.info(f'Categoria cadastrada: {nome} - {tipo}')

            return redirect(url_for('transacao.acessarTransacao'))

    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado')
        current_app.logger.warning(f'Erro ao cadastrar a categoria: {e}')
        return redirect(url_for('transacao.acessarTransacao'))

@categoria_bp.route('/editar/<int:categoria_id>', methods=['POST'])
def editarCategoria(categoria_id):
    try:
        categoria = Categorias.query.get(categoria_id)

        if not categoria:
            flash('Categoria não encontrada')
            return redirect(url_for('transacao.acessarTransacao'))

        categoria.nome = request.form.get('nome') or categoria.nome
        categoria.tipo = request.form.get('tipo') or categoria.tipo

        db.session.commit()
        flash('Categoria atualizada com sucesso')
        return redirect(url_for('transacao.acessarTransacao'))

    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado')
        return redirect(url_for('transacao.acessarTransacao'))

@categoria_bp.route('/deletar/<int:categoria_id>', methods=["POST"])
def deletarCategoria(categoria_id):
    try:
        categoria = Categorias.query.get(categoria_id)

        if not categoria:
            flash('Categoria não encontrada')
            return redirect(url_for('transacao.acessarTransacao'))

        db.session.delete(categoria)
        db.session.commit()
        flash('Categoria excluída com sucesso')
        return redirect(url_for('transacao.acessarTransacao'))

    except Exception as e:
        db.session.rollback()
        flash('Erro ao deletar categoria')
        return redirect(url_for('transacao.acessarTransacao'))

@categoria_bp.route('/listar', methods=['GET'])
def listarCategoria():
    try:
        categorias = Categorias.query.all()
        return render_template('categoria/listar.html', categorias=categorias)

    except Exception as e:
        flash('Erro ao listar categorias')
        return redirect(url_for('transacao.acessarTransacao'))
