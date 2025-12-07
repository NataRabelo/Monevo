from datetime import datetime
from flask import Blueprint, current_app, render_template, request, flash, redirect, url_for
from app.models import Categorias, Contas, Cartoes, Transacoes
from app.services.agrupador import agrupar_transacoes_por_mes
from app.services.recorrencia_servico import gerar_proximas_transacoes_recorrentes
from app.utils import limpar_currency
from flask_login import current_user, login_required
from app import db
from dateutil.relativedelta import relativedelta

transacao_bp = Blueprint('transacao', __name__, url_prefix='/transacao')


# -------------------------------------
# Acesso à Página de Transações
# -------------------------------------
@transacao_bp.route('/', methods=['GET'])
@login_required
def acessarTransacao():
    if request.method == "GET":
        usuario_id = current_user.id
        hoje = datetime.now().date()

        data_inicio_busca = hoje + relativedelta(months=-6, day=1)
        data_fim_busca = hoje + relativedelta(months=+12, day=31)
        
        cartoes = Cartoes.query.filter_by(usuario_id=usuario_id).all()
        contas = Contas.query.filter_by(usuario_id=usuario_id).all()
        categorias = Categorias.query.filter_by(usuario_id=usuario_id).all()

        transacoes_filtradas = Transacoes.query.filter(
            Transacoes.usuario_id == usuario_id,
            Transacoes.data_transacao >= data_inicio_busca,
            Transacoes.data_transacao <= data_fim_busca
        ).order_by(Transacoes.data_transacao.desc()).all()

        transacoes_agrupadas = agrupar_transacoes_por_mes(transacoes_filtradas)
        
        total_receita = db.session.query(
            db.func.sum(Transacoes.valor)
        ).filter(
            Transacoes.tipo == "Receita",
            Transacoes.usuario_id == usuario_id,
            Transacoes.data_transacao >= data_inicio_busca,
            Transacoes.data_transacao <= data_fim_busca    
        ).scalar() or 0

        total_despesa = db.session.query(
            db.func.sum(Transacoes.valor)
        ).filter(
            Transacoes.tipo == "Despesa",
            Transacoes.usuario_id == usuario_id,
            Transacoes.data_transacao >= data_inicio_busca,
            Transacoes.data_transacao <= data_fim_busca    
        ).scalar() or 0

        return render_template('dashboard/transacao.html',
                                cartoes = cartoes,
                                contas = contas,
                                transacoes_agrupadas = transacoes_agrupadas,
                                total_receita = total_receita,
                                total_despesa = total_despesa,
                                categorias = categorias)

# -------------------------------------
# Cadastro de Transação
# -------------------------------------
@transacao_bp.route('/cadastrar', methods=['POST'])
@login_required
def cadastrarTransacao():
    try:
        usuario = current_user.id

        # CAPTURA DADOS DO FORM (nomes alinhados com o HTML)
        conta_id        = request.form.get('conta_transacao')
        cartao_id       = request.form.get('cartao') # Pode ser nulo
        categoria_id    = request.form.get('categoria_transacao')
        tipo            = request.form.get('tipo_transacao')
        descricao       = request.form.get('descricao')
        valor           = limpar_currency(request.form.get('valor_transacao'))
        data_str        = request.form.get('data_transacao')
        recorrencia     = request.form.get('recorrencia')
        data_transacao = datetime.strptime(data_str, "%Y-%m-%d").date()
        
        # Variável para armazenar a transação recém-criada
        nova_transacao = None 

       # CADASTRAR RECEITA (ou Despesa)
        if tipo == 'Receita':
            nova_transacao = Transacoes(
                usuario_id      = usuario,
                conta_id        = conta_id,
                categoria_id    = categoria_id,
                tipo            = tipo,
                descricao       = descricao,
                valor           = valor,
                data_transacao  = data_transacao,
                recorrencia     = recorrencia,
                # AGORA: MESTRA INICIALMENTE NÃO TEM id_original
                recorrente      = recorrencia != 'Sem recorrencia' # <-- CORREÇÃO: Marca como recorrente se tiver recorrência
            )
        
        elif tipo == 'Despesa':
            nova_transacao = Transacoes(
                usuario_id      = usuario,
                conta_id        = conta_id,
                cartao_id       = cartao_id,
                categoria_id    = categoria_id,
                tipo            = tipo,
                descricao       = descricao,
                valor           = valor,
                data_transacao  = data_transacao,
                recorrencia     = recorrencia,
                recorrente      = recorrencia != 'Sem recorrencia'
            )
        
        db.session.add(nova_transacao)
        db.session.commit()
        
        if nova_transacao.recorrencia != 'Sem recorrencia':
            nova_transacao.id_original = nova_transacao.id
            db.session.commit()
        
        if nova_transacao.recorrencia != 'Sem recorrencia':
            ocorrencias_geradas = gerar_proximas_transacoes_recorrentes(nova_transacao, db, Transacoes)
            flash(f'Transação cadastrada com sucesso! ({ocorrencias_geradas} ocorrências recorrentes geradas.)', 'success')
        else:
            flash('Transação cadastrada com sucesso!', 'success')
        
        return redirect(url_for('transacao.acessarTransacao'))
        
    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado ao cadastrar.', 'danger')
        current_app.logger.warning(f'Erro ao cadastrar transacao: {e}')
        return redirect(url_for('transacao.acessarTransacao'))

# -------------------------------------
# Edição de Transação (CORRIGIDA)
# -------------------------------------
@transacao_bp.route('/editar', methods=['POST'])
@login_required
def editarTransacao():
    try:
        tipo = request.form.get('tipo_transacao')

        # O loop de edição precisa ser envolvido em uma variável `transacao_editada`
        # para aplicar a lógica de recorrência no final.
        transacao_editada = None
        
        # EDITAR RECEITA
        if tipo == 'Receita':
            receita_id = request.form.get('receita_id')
            
            # 1. ENCONTRAR E VALIDAR A RECEITA
            receita = Transacoes.query.filter(
                Transacoes.id == receita_id,
                Transacoes.tipo == 'Receita',
                Transacoes.usuario_id == current_user.id
            ).first()

            if not receita:
                flash('Receita não encontrada', 'danger')
                return redirect(url_for('transacao.acessarTransacao'))
            
            # 2. CAPTURAR DADOS E ATUALIZAR A MESTRA
            
            # Garante que a data_transacao seja um objeto date para evitar erros
            data_str = request.form.get('data_transacao')
            nova_data = datetime.strptime(data_str, "%Y-%m-%d").date() if data_str else receita.data_transacao

            # Atualizando campos
            receita.conta_id        = request.form.get('conta_transacao') or receita.conta_id
            receita.categoria_id    = request.form.get('categoria_transacao') or receita.categoria_id
            receita.descricao       = request.form.get('descricao') or receita.descricao
            receita.valor           = limpar_currency(request.form.get('valor_transacao')) or receita.valor
            receita.data_transacao  = nova_data
            receita.recorrencia     = request.form.get('recorrencia') or receita.recorrencia
            
            # Se a recorrência foi alterada/adicionada, garanta que a mestra esteja marcada corretamente
            if receita.recorrencia != 'Sem recorrencia':
                # Se for a primeira vez, marca como recorrente e aponta para si mesma.
                if not receita.id_original:
                     receita.id_original = receita.id 
                receita.recorrente = True
            else:
                 # Se a recorrência foi removida, limpa os flags
                receita.recorrente = False
                # Não é recomendável setar id_original como None, mas para simplificar:
                # Transações filhas que porventura já existam continuarão apontando para o ID dela,
                # mas ela não gerará novas ocorrências.
            
            transacao_editada = receita # Armazena a transação para a lógica de recorrência

        # ... (BLOCO DE EDIÇÃO PARA 'Despesa' DEVE VIR AQUI) ...
        
        # 3. LÓGICA DE REGENERAÇÃO PARA SÉRIES RECORRENTES (Executa após as atualizações)
        if transacao_editada and transacao_editada.recorrencia != 'Sem recorrencia' and transacao_editada.id_original == transacao_editada.id:
            
            # A) DELETAR todas as ocorrências filhas FUTURAS associadas a esta mestra
            Transacoes.query.filter(
                Transacoes.id_original == transacao_editada.id_original,
                Transacoes.id != transacao_editada.id, # Não deleta a própria mestra
                Transacoes.data_transacao > datetime.now().date(), # Deleta apenas as futuras
                Transacoes.usuario_id == current_user.id # Filtro de segurança
            ).delete(synchronize_session=False)

            # B) REGERAR as ocorrências filhas com os NOVOS dados da mestra
            # Se a data de transação da mestra mudou, a série recomeça a partir dela.
            ocorrencias_geradas = gerar_proximas_transacoes_recorrentes(transacao_editada, db, Transacoes)
            
            db.session.commit()
            flash(f'Receita mestra atualizada. {ocorrencias_geradas} ocorrências futuras regeradas!', 'success')
            
        elif transacao_editada:
            # 4. COMMIT FINAL para transações simples (ou filhas)
            db.session.commit()
            flash('Transação atualizada com sucesso', 'success')

        return redirect(url_for('transacao.acessarTransacao'))
        
    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado ao editar.', 'danger')
        current_app.logger.warning(f'Erro ao editar transacao: {e}')
        return redirect(url_for('transacao.acessarTransacao'))

        # EDITAR DESPESA
        if tipo == 'Despesa':

            despesa_id = request.form.get('despesa_id')

            despesa = Transacoes.query.filter(
                Transacoes.id == despesa_id,
                Transacoes.tipo == 'Despesa',
                Transacoes.usuario_id == current_user.id
            ).first()

            if not despesa:
                flash('Despesa não encontrada', 'danger')
                return redirect(url_for('transacao.acessarTransacao'))

            despesa.conta_id        = request.form.get('conta_transacao') or despesa.conta_id
            despesa.cartao_id       = request.form.get('cartao') or despesa.cartao_id
            despesa.categoria_id    = request.form.get('categoria_transacao') or despesa.categoria_id
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


# -------------------------------------
# Deleção de Transação (Corrigida)
# -------------------------------------
@transacao_bp.route('/deletar/<int:transacao_id>', methods=['GET', 'POST'])
@login_required
def deletarTransacao(transacao_id):
    try:
        usuario_id = current_user.id
        
        transacao = Transacoes.query.filter(
            Transacoes.id == transacao_id, 
            Transacoes.usuario_id == usuario_id
        ).first()

        if not transacao:
            flash('Transação não encontrada', 'warning')
            return redirect(url_for('transacao.acessarTransacao'))
        
        if transacao.recorrencia != 'Sem recorrencia' and transacao.id_original == transacao.id:
            
            Transacoes.query.filter(
                Transacoes.id_original == transacao.id_original,
                Transacoes.usuario_id == usuario_id
            ).delete(synchronize_session=False)
            flash('Série de transações recorrentes excluída com sucesso!', 'success')
            
        else:
            db.session.delete(transacao)
            flash('Transação excluída com sucesso', 'success')

        db.session.commit()
        return redirect(url_for('transacao.acessarTransacao'))
        
    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado ao deletar a transação.', 'danger')
        current_app.logger.warning(f'Erro ao deletar transacao: {e}')
        return redirect(url_for('transacao.acessarTransacao'))


# -------------------------------------
# Importação de Transações OFX
# -------------------------------------
@transacao_bp.route('/importar', methods=['GET'])
@login_required
def importarOfx():
    return 0
