from flask import Blueprint, current_app, render_template, request, flash, redirect, url_for
from app.utils import limpar_currency
from flask_login import current_user, login_required
from app.models import Cartoes, Transacoes
from app import db


cartao_bp = Blueprint('cartao', __name__, url_prefix='/cartao')


# -------------------------------------
# Cadastro de Cartão
# -------------------------------------
@cartao_bp.route('/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrarCartao():
    try: 
        usuario = current_user.id

        nome_cartao             = request.form.get('nome_cartao')
        bandeira                = request.form.get('bandeira')
        limite                  = limpar_currency(request.form.get('limite'))
        limite_disponivel       = limite
        dia_fechamento_fatura   = request.form.get('dia_fechamento_fatura')
        dia_vencimento_fatura   = request.form.get('dia_vencimento_fatura')
        conta_id                = request.form.get('conta_cartao')

        new_cartao = Cartoes(
            usuario_id              = usuario,
            nome_cartao             = nome_cartao,
            bandeira                = bandeira,
            limite                  = limite,
            limite_disponivel       = limite_disponivel,
            dia_fechamento_fatura   = dia_fechamento_fatura,
            dia_vencimento_fatura   = dia_vencimento_fatura,
            conta_id                = int(conta_id)
        )

        db.session.add(new_cartao)
        db.session.commit()

        flash(f'Cartão do banco {nome_cartao} cadastrado com sucesso', 'success')
        return redirect(url_for('conta.acessarConta'))

    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado', 'error')
        current_app.logger.warning(f'Erro ao cadastrar cartão: {e}')
        return redirect(url_for('conta.acessarConta'))

# -------------------------------------
# Edição de Cartão
# -------------------------------------
@cartao_bp.route('/editar', methods=['GET', 'POST'])
@login_required
def editarCartao():
    try:
        cartao_id    = request.form.get('cartao_id')
        cartao = Cartoes.query.filter(Cartoes.id == cartao_id).first()

        if not cartao:
            flash('Cartão não encontrado', 'error')
            return redirect(url_for('conta.acessarConta'))
        
        if request.method == 'GET':
            return render_template('cartao/editar')
        
        if request.method == 'POST':
            cartao.nome_cartao              = request.form.get('nome_cartao') or cartao.nome_cartao
            cartao.bandeira                 = request.form.get('bandeira') or cartao.bandeira
            cartao.limite                   = limpar_currency(request.form.get('limite') or cartao.limite)
            cartao.limite_disponivel        = cartao.limite
            cartao.dia_fechamento_fatura    = request.form.get('dia_fechamento_fatura') or cartao.dia_fechamento_cartao
            cartao.dia_vencimento_fatura    = request.form.get('dia_vencimento_fatura') or cartao.dia_vencimento_cartao

            db.session.commit()
            flash('Cartão atualizado com sucesso', 'success')
            return redirect(url_for('conta.acessarConta'))

    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado', 'error')
        current_app.logger.warning(f'Erro ao editar o cartao: {e}')
        return redirect(url_for('main.menu'))

# -------------------------------------
# Deleção de Cartão
# -------------------------------------
@cartao_bp.route('/deletar/<int:cartao_id>', methods=['GET', 'POST'])
@login_required
def deletarCartao(cartao_id):
    try:
        cartao = Cartoes.query.filter(Cartoes.id == cartao_id).first()

        if not cartao:
            flash('Cartão não encontrado', 'error')
            return redirect(url_for('conta.acessarConta'))
        
        transacao_vinculada = Transacoes.query.filter(Transacoes.cartao_id == cartao.id).first()
        if transacao_vinculada:
            flash('Não é possível excluir um cartão com transações vinculadas.', 'error')
            return redirect(url_for('conta.acessarConta'))
        
        if request.method == 'POST':
            db.session.delete(cartao)
            db.session.commit()
            flash('Cartão excluido com sucesso.', 'success')
            return redirect(url_for('conta.acessarConta'))
    
    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado', 'error')
        current_app.logger.warning(f'Erro ao deletar cartao: {e}')
        return redirect(url_for('conta.acessarConta'))

# -------------------------------------
# Listagem de Cartões
# -------------------------------------
@cartao_bp.route('/listar', methods=['GET', 'POST'])
@login_required
def listarCartao(): 
    try:
        cartoes = Cartoes.query.all()

        if not cartoes:
            flash('Nenhum cartão cadastrado', 'error')
            return redirect(url_for('conta.acessarConta'))
        
        if request.method == 'GET':
            return render_template('cartao/listar.html', cartoes=cartoes)

    except Exception as e:
        flash('Ocorreu algum erro inesperado', 'error')
        current_app.logger.warning(f'Erro ao listar os cartoes: {e}')
        return redirect(url_for('conta.acessarConta'))