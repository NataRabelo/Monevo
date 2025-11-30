from flask import Blueprint, current_app, render_template, request, flash, redirect, url_for
from app.models import Contas, Cartoes
from flask_login import current_user
from app import db
from app.utils import limpar_currency

conta_bp = Blueprint('conta', __name__, url_prefix='/conta')

@conta_bp.route('/', methods=['GET', 'POST'])
def acessarConta():
    if request.method == "GET":
        contas = Contas.query.all()
        cartoes = Cartoes.query.all()
        return render_template('dashboard/contas.html', contas=contas, cartoes=cartoes)

@conta_bp.route('/cadastrar', methods=['GET', 'POST'])
def cadastrarConta():
    try:
        usuario = current_user

        # Buscar dados
        usuario         = usuario.id
        nome_conta      = request.form.get('nome_conta')
        instituicao     = request.form.get('instituicao')
        tipo_conta      = request.form.get('tipo_conta')
        saldo_inicial   = limpar_currency(request.form.get('saldo_inicial'))
        
        # Verificações 

        # Criando o objeto Conta 
        new_conta = Contas (
            usuario_id      = usuario,
            nome_conta      = nome_conta,
            instituicao     = instituicao,
            tipo_conta      = tipo_conta,
            saldo_inicial   = saldo_inicial
        )

        # Adiciona ao banco 
        db.session.add(new_conta)
        db.session.commit()

        # notificação + log
        flash(f'Conta do banco {instituicao}, cadastrada com sucesso')
        current_app.logger.info(f'Conta cadastrada com sucesso: {instituicao} - { tipo_conta}')

        return redirect(url_for('conta.acessarConta'))
    
    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado')
        current_app.logger.warning(f'Erro ao cadastrar conta: {e}')
        return redirect(url_for('conta.acessarConta'))

@conta_bp.route('/editar', methods=['GET', 'POST'])
def editarConta():
    try:
        # Validar a existencia da conta 
        conta_id    = request.form.get('conta_id')
        conta       = Contas.query.filter(Contas.id == conta_id).first()

        if not conta:
            flash('Conta não encontrada')
            return redirect(url_for('conta.acessarConta'))

        if request.method == "GET":
            return render_template('conta/editar')
        
        if request.method == "POST":
            # Passando os dados alterados ( or not )
            conta.nome_conta        = request.form.get('nome_conta') or conta.nome_conta
            conta.instituicao       = request.form.get('instituicao') or conta.instituicao
            conta.tipo_conta        = request.form.get('tipo_conta') or conta.tipo_conta
            conta.saldo_inicial     = limpar_currency(request.form.get('saldo_inicial') or conta.saldo_inicial)

            # passsando para o banco 
            db.session.commit()
            flash('Conta atualizada com sucesso')
            return redirect(url_for('conta.acessarConta'))
        
    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado')
        current_app.logger.warning(f'Erro ao editar conta: {e}')
        return redirect(url_for('conta.acessarConta'))
    
@conta_bp.route('/deletar/<int:conta_id>', methods=['GET', 'POST'])
def deletarConta(conta_id):
    try:
        # Valida a existencia
        conta = Contas.query.filter(Contas.id == conta_id).first()

        if not conta:
            flash('Conta não encontrada')
            return redirect(url_for('conta.acessarConta'))
        
        if request.method == "POST":
            # Deleta do banco
            db.session.delete(conta)
            db.session.commit()
            flash('Conta excluida com sucesso.')
            return redirect(url_for('conta.acessarConta'))
        
    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado')
        current_app.logger.warning(f'Erro ao deletar conta: {e}')
        return redirect(url_for('conta.acessarConta'))
    
@conta_bp.route('/listar', methods=['GET', 'POST'])
def listarConta():
    try:
        # Busca todos os objetos
        contas = Contas.query.all()

        if not contas:
            flash('Nenhuma conta cadastrada')
            return redirect(url_for('conta.acessarConta'))
        
        if request.method == "GET":
            # Retorna com a lista 
            return render_template('conta/listar.html', contas = contas)
        
    except Exception as e:
        flash('Ocorreu algum erro inesperado')
        current_app.logger.warning(f'Erro ao listar contas: {e}')
        return redirect(url_for('conta.acessarConta'))
    