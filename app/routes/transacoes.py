from datetime import datetime
from flask import Blueprint, current_app, render_template, request, flash, redirect, url_for
from app.models import Contas, Cartoes, Transacoes
from app.utils import limpar_currency
from flask_login import current_user
from app import db


transacao_bp = Blueprint('transacao', __name__, url_prefix='/transacao')

@transacao_bp.route('/', methods=['GET'])
def acessarTransacao():
    if request.method == "GET":
        cartoes = Cartoes.query.all()
        contas = Contas.query.all()
        transacoes = Transacoes.query.all()
        return render_template('dashboard/transacao.html',
                                cartoes = cartoes,
                                contas = contas,
                                transacoes = transacoes)
    

@transacao_bp.route('/cadastrar', methods=['POST'])
def cadastrarTransacao():
    try:
        usuario = current_user.id

        # ------------------------------
        # CAPTURA DADOS DO FORM
        # ------------------------------ 
        conta_id        = request.form.get('conta_transacao')
        cartao_id       = request.form.get('cartao')
        categoria_id    = request.form.get('categoria')
        tipo            = request.form.get('tipo_transacao')
        descricao       = request.form.get('descricao')
        valor           = limpar_currency(request.form.get('valor_transacao'))
        data_str        = request.form.get('data_transacao')
        recorrencia     = request.form.get('recorrencia')
        data_transacao = datetime.strptime(data_str, "%Y-%m-%d").date()

        # ------------------------------
        # CADASTRAR RECEITA
        # ------------------------------ 
        if tipo == 'Receita':
            new_receita = Transacoes(
                usuario_id      = usuario,
                conta_id        = conta_id,
                categoria_id    = 1,
                tipo            = tipo,
                descricao       = descricao,
                valor           = valor,
                data_transacao  = data_transacao,
                recorrencia     = recorrencia
            )
            db.session.add(new_receita)
            db.session.commit()

        # ------------------------------
        # CADASTRAR DESPESA
        # ------------------------------    
        elif tipo == 'Despesa':
            new_despesa = Transacoes(
                usuario_id      = usuario,
                conta_id        = conta_id,
                cartao_id       = cartao_id,
                categoria_id    = categoria_id,
                tipo            = tipo,
                descricao       = descricao,
                valor           = valor,
                data_transacao  = data_transacao,
                recorrencia     = recorrencia
            )
            db.session.add(new_despesa)     
            db.session.commit()
        
        return redirect(url_for('transacao.acessarTransacao'))
        
    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado', 'danger')
        current_app.logger.warning(f'Erro ao cadastrar transacao: {e}')
        return redirect(url_for('transacao.acessarTransacao'))
    
@transacao_bp.route('/editar', methods=['POST'])
def editarTransacao():
    try:
        tipo = request.form.get('tipo_transacao')

        # ------------------------------
        # EDITAR RECEITA
        # ------------------------------
        if tipo == 'Receita':

            receita_id = request.form.get('receita_id')

            receita = Transacoes.query.filter(
                Transacoes.id == receita_id,
                Transacoes.tipo == 'Receita'
            ).first()

            if not receita:
                flash('Receita não encontrada', 'danger')
                return redirect(url_for('transacao.acessarTransacao'))

            # Atualizando campos
            receita.conta_id        = request.form.get('conta_transacao') or receita.conta_id
            receita.categoria_id    = request.form.get('categoria') or receita.categoria_id
            receita.descricao       = request.form.get('descricao') or receita.descricao
            receita.valor           = limpar_currency(request.form.get('valor_transacao')) or receita.valor
            receita.data_transacao  = datetime.strptime(request.form.get('data_transacao'), "%Y-%m-%d") if request.form.get('data_transacao') else receita.data_transacao
            receita.recorrencia     = request.form.get('recorrencia') or receita.recorrencia

            db.session.commit()
            flash('Receita atualizada com sucesso', 'success')
            return redirect(url_for('transacao.acessarTransacao'))

        # ------------------------------
        # EDITAR DESPESA
        # ------------------------------
        if tipo == 'Despesa':

            despesa_id = request.form.get('despesa_id')

            despesa = Transacoes.query.filter(
                Transacoes.id == despesa_id,
                Transacoes.tipo == 'Despesa'
            ).first()

            if not despesa:
                flash('Despesa não encontrada', 'danger')
                return redirect(url_for('transacao.acessarTransacao'))

            despesa.conta_id        = request.form.get('conta_transacao') or despesa.conta_id
            despesa.cartao_id       = request.form.get('cartao') or despesa.cartao_id
            despesa.categoria_id    = request.form.get('categoria') or despesa.categoria_id
            despesa.descricao       = request.form.get('descricao') or despesa.descricao
            despesa.valor           = limpar_currency(request.form.get('valor_transacao')) or despesa.valor
            despesa.data_transacao  = datetime.strptime(request.form.get('data_transacao'), "%Y-%m-%d") if request.form.get('data_transacao') else despesa.data_transacao
            despesa.recorrencia     = request.form.get('recorrencia') or despesa.recorrencia

            db.session.commit()
            flash('Despesa atualizada com sucesso', 'success')
            return redirect(url_for('transacao.acessarTransacao'))

        flash("Tipo de transação inválido", "danger")
        return redirect(url_for('transacao.acessarTransacao'))

    except Exception as e:
        db.session.rollback()
        current_app.logger.warning(f'Erro ao editar transacao: {e}')
        flash('Ocorreu algum erro inesperado', 'danger')
        return redirect(url_for('transacao.acessarTransacao'))

@transacao_bp.route('/deletar/<int:transacao_id>', methods=['GET', 'POST'])
def deletarTransacao(transacao_id):
    try:
        # VALIDA A EXISTENCIA 
        transacao = Transacoes.query.filter(Transacoes.id == transacao_id).first()

        if not transacao:
            flash('Transação não encontrada')
            return redirect(url_for('transacao.acessarTransacao'))
        
        if request.methods == 'GET':
            return 0
        
        if request.method == 'POST':
            # DELETAR DO BANCO 
            db.session.delete(transacao)
            db.session.commit()
            flash('Transação excluida com sucesso')
            return redirect(url_for('transacao.acessarTransacao'))
        
    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado', 'danger')
        return redirect


@transacao_bp.route('/importar', methods=['GET'])
def importarOfx():
    return 0