from flask import Blueprint, current_app, render_template, request, flash, redirect, url_for
from app.models import Contas, Cartoes, SaldoInicial
from flask_login import current_user, login_required
from app import db
from app.utils import limpar_currency
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

        # Buscar dados
        nome_conta      = request.form.get('nome_conta')
        instituicao     = request.form.get('instituicao')
        tipo_conta      = request.form.get('tipo_conta')
        # Saldo inicial é o saldo ATUAL da conta
        saldo_atual     = limpar_currency(request.form.get('saldo_inicial'))
        
        # 1. Criando o objeto Conta 
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

        # notificação + log
        flash(f'Conta do banco {instituicao} cadastrada com sucesso e saldo inicial registrado.')
        current_app.logger.info(f'Conta cadastrada com sucesso: {instituicao} - { tipo_conta}')

        return redirect(url_for('conta.acessarConta'))
    
    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado')
        current_app.logger.warning(f'Erro ao cadastrar conta: {e}')
        return redirect(url_for('conta.acessarConta'))


# -------------------------------------
# Edição de Conta (ATUALIZADA)
# -------------------------------------
@conta_bp.route('/editar', methods=['GET', 'POST'])
@login_required
def editarConta():
    try:
        usuario_id = current_user.id
        
        # Validar a existencia da conta 
        conta_id    = request.form.get('conta_id')
        conta       = Contas.query.filter(
            Contas.id == conta_id,
            Contas.usuario_id == usuario_id # Boa prática: validar que a conta pertence ao usuário
        ).first()

        if not conta:
            flash('Conta não encontrada', 'danger')
            return redirect(url_for('conta.acessarConta'))

        if request.method == "GET":
            return render_template('conta/editar')
        
        if request.method == "POST":
            # 1. Captura do novo saldo (saldo vivo)
            novo_saldo_vivo_str = request.form.get('saldo_inicial')
            novo_saldo_vivo = limpar_currency(novo_saldo_vivo_str)

            # 2. Atualiza a Conta (Saldo Vivo e outros dados)
            conta.nome_conta        = request.form.get('nome_conta') or conta.nome_conta
            conta.instituicao       = request.form.get('instituicao') or conta.instituicao
            conta.tipo_conta        = request.form.get('tipo_conta') or conta.tipo_conta
            
            # Atualiza o saldo vivo APENAS se um novo valor válido foi fornecido
            if novo_saldo_vivo is not None:
                conta.saldo_inicial = novo_saldo_vivo

            # 3. SINCRONIZAÇÃO DO SALDO DE PROJEÇÃO (SaldoInicial) 💰
            
            hoje = datetime.now()
            # O ponto de partida da projeção é o primeiro dia do mês atual
            mes_ano_referencia = hoje.date().replace(day=1) 
            
            # Buscar o registro de SaldoInicial para a Conta e o Mês Atual
            saldo_projecao = SaldoInicial.query.filter(
                SaldoInicial.conta_id == conta_id,
                SaldoInicial.mes_ano == mes_ano_referencia,
                SaldoInicial.usuario_id == usuario_id
            ).first()

            if saldo_projecao:
                # Se o registro existe (deve existir, pois foi criado no cadastro)
                saldo_projecao.saldo_inicial = conta.saldo_inicial
                db.session.add(saldo_projecao)
            else:
                 # Cria o registro se por algum motivo ele foi deletado ou não existia
                novo_saldo_projecao = SaldoInicial(
                    usuario_id=usuario_id,
                    conta_id=conta_id,
                    saldo_inicial=conta.saldo_inicial,
                    mes_ano=mes_ano_referencia
                )
                db.session.add(novo_saldo_projecao)
            
            # 4. Finaliza a transação
            db.session.commit()
            flash('Conta atualizada e saldo de projeção sincronizado com sucesso', 'success')
            return redirect(url_for('conta.acessarConta'))
        
    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado ao editar a conta.', 'danger')
        current_app.logger.warning(f'Erro ao editar conta: {e}')
        return redirect(url_for('conta.acessarConta'))


# -------------------------------------
# Deleção de Conta (CORRIGIDO)
# -------------------------------------
@conta_bp.route('/deletar/<int:conta_id>', methods=['POST']) # Alterado para POST
@login_required
def deletarConta(conta_id):
    try:
        usuario_id = current_user.id
        
        # Valida a existencia e a posse
        conta = Contas.query.filter(
            Contas.id == conta_id,
            Contas.usuario_id == usuario_id 
        ).first()

        if not conta:
            flash('Conta não encontrada ou você não tem permissão para deletá-la.', 'danger')
            return redirect(url_for('conta.acessarConta'))
        
        # 1. VERIFICAR TRANSAÇÕES VINCULADAS (MELHOR PRÁTICA: IMPEDIR DELEÇÃO SE HOUVER TRANSAÇÕES)
        # Se houver transações vinculadas, impedimos a exclusão para evitar buracos no histórico
        from app.models import Transacoes # Importar Transacoes aqui (ou no topo)
        transacoes_vinculadas = Transacoes.query.filter_by(conta_id=conta_id).first()
        
        if transacoes_vinculadas:
            flash('Não é possível excluir esta conta porque há transações (receitas ou despesas) vinculadas a ela. Exclua as transações primeiro.', 'warning')
            return redirect(url_for('conta.acessarConta'))


        # 2. DELETAR REGISTROS ASSOCIADOS (Tabelas de projeção)
        # Deletar todos os registros de SaldoInicial para esta conta
        SaldoInicial.query.filter_by(conta_id=conta_id).delete(synchronize_session=False)

        # 3. DELETAR A CONTA MESTRA
        db.session.delete(conta)
        db.session.commit()
        
        flash(f'Conta "{conta.nome_conta}" excluída com sucesso.', 'success')
        return redirect(url_for('conta.acessarConta'))
        
    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado ao deletar a conta.', 'danger')
        current_app.logger.warning(f'Erro ao deletar conta: {e}')
        return redirect(url_for('conta.acessarConta'))


# -------------------------------------
# Listagem de Conta
# -------------------------------------
@conta_bp.route('/listar', methods=['GET', 'POST'])
@login_required
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
    