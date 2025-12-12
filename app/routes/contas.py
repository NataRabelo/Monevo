from flask import Blueprint, current_app, render_template, request, flash, redirect, url_for
from app.models import Contas, Cartoes, SaldoInicial, Transacoes
from flask_login import current_user, login_required
from app import db
from app.utils import limpar_currency, limpar_espacos
from datetime import datetime

conta_bp = Blueprint('conta', __name__, url_prefix='/conta')

# -------------------------------------
# Acesso à Página de Contas/Cartões
# -------------------------------------
@conta_bp.route('/', methods=['GET', 'POST'])
@login_required
def acessarConta():
    if request.method == "GET":
        contas = Contas.query.all()
        cartoes = Cartoes.query.all()
        return render_template('dashboard/contas.html', contas=contas, cartoes=cartoes)

# -------------------------------------
# Cadastro de Conta
# -------------------------------------
@conta_bp.route('/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrarConta():
    try:
        usuario_id = current_user.id

        nome_conta      = limpar_espacos(request.form.get('nome_conta'))
        instituicao     = limpar_espacos(request.form.get('instituicao'))
        tipo_conta      = request.form.get('tipo_conta')
        saldo_atual     = limpar_currency(request.form.get('saldo_inicial'))
        
        new_conta = Contas (
            usuario_id      = usuario_id,
            nome_conta      = nome_conta,
            instituicao     = instituicao,
            tipo_conta      = tipo_conta,
            saldo_inicial   = saldo_atual 
        )

        db.session.add(new_conta)
        db.session.commit()
        hoje = datetime.now()
        mes_ano_referencia = hoje.date().replace(day=1) 
        
        novo_saldo_inicial = SaldoInicial(
            usuario_id=usuario_id,
            conta_id=new_conta.id,
            saldo_inicial=saldo_atual,
            mes_ano=mes_ano_referencia
        )
        
        db.session.add(novo_saldo_inicial)
        db.session.commit()

        flash(f'Conta do banco {instituicao} cadastrada com sucesso e saldo inicial registrado.', 'success')
        current_app.logger.info(f'Conta cadastrada com sucesso: {instituicao} - { tipo_conta}')

        return redirect(url_for('conta.acessarConta'))
    
    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado', 'error')
        current_app.logger.warning(f'Erro ao cadastrar conta: {e}')
        return redirect(url_for('conta.acessarConta'))

# -------------------------------------
# Edição de Conta
# -------------------------------------
@conta_bp.route('/editar', methods=['GET', 'POST'])
@login_required
def editarConta():
    try:
        usuario_id = current_user.id
        
        conta_id    = request.form.get('conta_id')
        conta       = Contas.query.filter(
            Contas.id == conta_id,
            Contas.usuario_id == usuario_id
        ).first()

        if not conta:
            flash('Conta não encontrada', 'error')
            return redirect(url_for('conta.acessarConta'))

        if request.method == "GET":
            return render_template('conta/editar')
        
        if request.method == "POST":
            novo_saldo_vivo_str     = request.form.get('saldo_inicial')
            novo_saldo_vivo         = limpar_currency(novo_saldo_vivo_str)
            conta.nome_conta        = limpar_espacos(request.form.get('nome_conta')) or conta.nome_conta
            conta.instituicao       = limpar_espacos(request.form.get('instituicao')) or conta.instituicao
            conta.tipo_conta        = request.form.get('tipo_conta') or conta.tipo_conta
            
            if novo_saldo_vivo is not None:
                conta.saldo_inicial = novo_saldo_vivo
            
            hoje = datetime.now()
            mes_ano_referencia = hoje.date().replace(day=1) 
            
            saldo_projecao = SaldoInicial.query.filter(
                SaldoInicial.conta_id == conta_id,
                SaldoInicial.mes_ano == mes_ano_referencia,
                SaldoInicial.usuario_id == usuario_id
            ).first()

            if saldo_projecao:
                saldo_projecao.saldo_inicial = conta.saldo_inicial
                db.session.add(saldo_projecao)
            else:
                novo_saldo_projecao = SaldoInicial(
                    usuario_id=usuario_id,
                    conta_id=conta_id,
                    saldo_inicial=conta.saldo_inicial,
                    mes_ano=mes_ano_referencia
                )
                db.session.add(novo_saldo_projecao)
            
            db.session.commit()
            flash('Conta atualizada e saldo de projeção sincronizado com sucesso', 'success')
            return redirect(url_for('conta.acessarConta'))
        
    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado', 'error')
        current_app.logger.warning(f'Erro ao editar conta: {e}')
        return redirect(url_for('conta.acessarConta'))

# -------------------------------------
# Deleção de Conta
# -------------------------------------
@conta_bp.route('/deletar/<int:conta_id>', methods=['POST'])
@login_required
def deletarConta(conta_id):
    try:
        usuario_id = current_user.id
        
        conta = Contas.query.filter(
            Contas.id == conta_id,
            Contas.usuario_id == usuario_id 
        ).first()

        if not conta:
            flash('Conta não encontrada ou você não tem permissão para deletá-la.', 'error')
            return redirect(url_for('conta.acessarConta'))
        
        transacoes_vinculadas = Transacoes.query.filter_by(conta_id=conta_id).first()
        
        if transacoes_vinculadas:
            flash('Não é possível excluir esta conta porque há transações (receitas ou despesas) vinculadas a ela. Exclua as transações primeiro.', 'error')
            return redirect(url_for('conta.acessarConta'))
        
        cartao_vinculado = Cartoes.query.filter_by(conta_id=conta_id).first()
        if cartao_vinculado:
            flash('Não é possível excluir esta conta porque há cartões vinculados a ela. Exclua os cartões primeiro.', 'error')
            return redirect(url_for('conta.acessarConta'))

        SaldoInicial.query.filter_by(conta_id=conta_id).delete(synchronize_session=False)

        db.session.delete(conta)
        db.session.commit()
        
        flash(f'Conta "{conta.nome_conta}" excluída com sucesso.', 'success')
        return redirect(url_for('conta.acessarConta'))
        
    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado', 'error')
        current_app.logger.warning(f'Erro ao deletar conta: {e}')
        return redirect(url_for('conta.acessarConta'))

# -------------------------------------
# Listagem de Conta
# -------------------------------------
@conta_bp.route('/listar', methods=['GET', 'POST'])
@login_required
def listarConta():
    try:
        contas = Contas.query.all()

        if not contas:
            flash('Nenhuma conta cadastrada', 'error')
            return redirect(url_for('conta.acessarConta'))
        
        if request.method == "GET":
            return render_template('conta/listar.html', contas = contas)
        
    except Exception as e:
        flash('Ocorreu algum erro inesperado', 'error')
        current_app.logger.warning(f'Erro ao listar contas: {e}')
        return redirect(url_for('conta.acessarConta'))
    