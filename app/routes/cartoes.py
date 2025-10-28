from flask import Blueprint, current_app, render_template, request, flash, redirect, url_for
from app.models import Cartoes
from flask_login import current_user
from app import db

cartao_bp = Blueprint('cartao', __name__, url_prefix='/cartao')

@cartao_bp.route('/cadastrar', methods=['GET', 'POST'])
def cadastraCartao():
    try: 
        usuario = current_user

        # Buscar dados
        usuario                 = usuario.id
        nome_cartao             = request.form.get('nome_cartao')
        bandeira                = request.form.get('bandeira')
        limite                  = request.form.get('limite')
        dia_fechamento_fatura   = request.form.get('dia_fechamento_fatura')
        dia_vencimento_fatura   = request.form.get('dia_vencimento_fatura')
        
        # Verificação

        # Criando o objeto Cartão
        new_cartao = Cartoes (
            usuario_id              = usuario,
            nome_cartao             = nome_cartao,
            bandeira                = bandeira,
            limite                  = limite,
            dia_fechamento_fatura   = dia_fechamento_fatura,
            dia_vencimento_fatura   = dia_vencimento_fatura
        )

        # Adiciona ao banco
        db.session.add(new_cartao)
        db.session.commit()

        # Notificação + log
        flash(f'Cartão do banco {nome_cartao}, cadastrado com sucesso')
        current_app.logger.info(f'Cartão cadstrado com sucesso: {nome_cartao} - {bandeira}')

        return redirect(url_for('conta.acessarConta'))

    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado')
        current_app.logger.warning(f'Erro ao cadastrar cartão {e}')
        return redirect(url_for('conta.acessarConta'))
    
@cartao_bp.route('/editar/<int:cartao_id>', methods=['GET', 'POST'])
def editarCartao(cartao_id):
    try:
        # Validar a existencia do cartão
        cartao = Cartoes.query.filter(Cartoes.id == cartao_id).first()

        if not cartao:
            flash('Cartão não encontrado')
            return redirect(url_for('conta.acessarConta'))
        
        if request.method == 'GET':
            return render_template('cartao/editar')
        
        if request.method == 'POST':
            # Passando os dados alterados ( or not )
            cartao.nome_cartao              = request.form.get('nome_cartao') or cartao.nome_cartao
            cartao.bandeira                 = request.form.get('bandeira') or cartao.bandeira
            cartao.limite                   = request.form.get('limite') or cartao.limite
            cartao.dia_fechamento_fatura    = request.form.get('dia_fechamento_fatura') or cartao.dia_fechamento_cartao
            cartao.dia_vencimento_fatura    = request.form.get('dia_vencimento_fatura') or cartao.dia_vencimento_cartao

            # Passando para o banco
            db.session.commit()
            flash('Cartão atualizado com sucesso')
            return redirect(url_for('conta.acessoConta'))

    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado')
        current_app.logger.warning(f'Erro ao editar o cartao: {e}')
        return redirect(url_for('main.menu'))
    

@cartao_bp.route('/deletar/<int:cartao_id>', methods=['GET', 'POST'])
def deletarCartao(cartao_id):
    try:
        # Valida a existencia
        cartao = Cartoes.query.filter(Cartoes.id == cartao_id).first()

        if not cartao:
            flash('Cartão não encontrado')
            return redirect(url_for('conta.acessarConta'))
        
        if request.method == 'POST':
            # Deleta do banco
            db.session.delete(cartao)
            db.session.commit()
            flash('Cartão excluido com sucesso.')
            return redirect(url_for('conta.acessarConta'))
    
    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado')
        current_app.logger.warning(f'Erro ao deletar cartao: {e}')
        return redirect(url_for('conta.acessarConta'))
    

@cartao_bp.route('/listar', methods=['GET', 'POST'])
def listarCartao():
    try:
        # Buscar todos os objetos
        cartoes = Cartoes.query.all()

        if not cartoes:
            flash('Nenhum cartão cadastrado')
            return redirect(url_for('conta.acessarConta'))
        
        if request.method == 'GET':
            # Retorna a lista
            return render_template('cartao/listar.html', cartoes=cartoes)

    except Exception as e:
        flash('Ocorreu algum erru inesperado')
        current_app.logger.warning(f'Erro ao listar os cartoes: {e}')
        return redirect(url_for('conta.acessarConta'))