from flask import Blueprint, current_app, render_template, request, flash, redirect, url_for
from app.models import Categorias, Transacoes
from flask_login import current_user, login_required
from app import db

categoria_bp = Blueprint('categoria', __name__, url_prefix='/categoria')

# -------------------------------------
# Cadastro de Categoria
# -------------------------------------
@categoria_bp.route('/cadastrar', methods=['POST'])
@login_required
def cadastrarCategoria():
    try:
        if request.method == "POST":
            usuario = current_user
            nome = request.form.get('nome_categoria')
            tipo = request.form.get('tipo_categoria')

            new_categoria = Categorias(
                usuario_id=usuario.id,
                nome=nome,
                tipo=tipo
            )

            db.session.add(new_categoria)
            db.session.commit()

            flash(f'Categoria {nome} cadastrada com sucesso', 'success')
            current_app.logger.info(f'Categoria cadastrada: {nome} - {tipo}')

            return redirect(url_for('transacao.acessarTransacao'))

    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado', 'error')
        current_app.logger.warning(f'Erro ao cadastrar a categoria: {e}')
        return redirect(url_for('transacao.acessarTransacao'))

# -------------------------------------
# Edição de Categoria
# -------------------------------------
@categoria_bp.route('/editar/', methods=['POST'])
@login_required
def editarCategoria():
    try:
        categoria_id = request.form.get("categoria_id")
        categoria = Categorias.query.get(categoria_id)

        if not categoria:
            flash('Categoria não encontrada', 'error')
            return redirect(url_for('transacao.acessarTransacao'))

        categoria.nome = request.form.get('nome_categoria') or categoria.nome
        categoria.tipo = request.form.get('tipo_categoria') or categoria.tipo

        db.session.commit()
        flash('Categoria atualizada com sucesso', 'success')
        return redirect(url_for('transacao.acessarTransacao'))

    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado', 'error')
        current_app.logger.warning(f'Erro ao editar a categoria: {e}')
        return redirect(url_for('transacao.acessarTransacao'))

# -------------------------------------
# Deleção de Categoria
# -------------------------------------
@categoria_bp.route('/deletar/<int:categoria_id>', methods=["POST"])
@login_required
def deletarCategoria(categoria_id):
    try:
        categoria = Categorias.query.get(categoria_id)

        transacao_categoria = Transacoes.query.filter_by(categoria_id=categoria_id).first()
        if transacao_categoria:
            flash('Não é possível deletar uma categoria vinculada a transações', 'error')
            return redirect(url_for('transacao.acessarTransacao'))

        if not categoria:
            flash('Categoria não encontrada', 'error')
            return redirect(url_for('transacao.acessarTransacao'))

        db.session.delete(categoria)
        db.session.commit()
        flash('Categoria excluída com sucesso', 'success')
        return redirect(url_for('transacao.acessarTransacao'))

    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado', 'error')
        current_app.logger.warning(f'Erro ao deletar a categoria: {e}')
        return redirect(url_for('transacao.acessarTransacao'))

# -------------------------------------
# Listagem de Categoria
# -------------------------------------
@categoria_bp.route('/listar', methods=['GET'])
@login_required
def listarCategoria():
    try:
        categorias = Categorias.query.all()
        return render_template('categoria/listar.html', categorias=categorias)

    except Exception as e:
        flash('Ocorreu algum erro inesperado', 'error')
        return redirect(url_for('transacao.acessarTransacao'))
