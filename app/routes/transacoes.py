from datetime import datetime
from flask import Blueprint, current_app, render_template, request, flash, redirect, url_for
from app.models import Categorias, Contas, Cartoes, Transacoes 
from app.services.agrupador import agrupar_transacoes_por_mes
from app.services.recorrencia_servico import gerar_proximas_transacoes_recorrentes
from app.utils import limpar_currency, formatar_currency 
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

        # Define o período de busca (12 meses para trás e 12 meses para frente)
        data_inicio_busca = hoje + relativedelta(months=-12, day=1)
        data_fim_busca = hoje + relativedelta(months=+12, day=31)
        
        # Busca todas as informações necessárias para a dashboard
        cartoes = Cartoes.query.filter_by(usuario_id=usuario_id).all()
        contas = Contas.query.filter_by(usuario_id=usuario_id).all()
        categorias = Categorias.query.filter_by(usuario_id=usuario_id).all()

        contas_usuario = Contas.query.filter_by(usuario_id=current_user.id).all()
        contas_correntes = Contas.query.filter_by(usuario_id=usuario_id).all()
        cartoes_credito = Cartoes.query.filter_by(usuario_id=usuario_id).all()

        # Filtra transações a serem exibidas: todas ativas (parcela_atual != 0) e dentro do período de busca
        transacoes_filtradas = Transacoes.query.filter(
            Transacoes.usuario_id == usuario_id,
            Transacoes.data_transacao >= data_inicio_busca,
            Transacoes.data_transacao <= data_fim_busca,
            Transacoes.parcela_atual != 0
        ).order_by(Transacoes.data_transacao.desc()).all()

        # Agrupa as transações para exibição (ex: por mês/ano)
        transacoes_agrupadas = agrupar_transacoes_por_mes(transacoes_filtradas)
        
        # Calcula o total de receita no período
        total_receita = db.session.query(
            db.func.sum(Transacoes.valor)
        ).filter(
            Transacoes.tipo == "Receita",
            Transacoes.usuario_id == usuario_id,
            Transacoes.data_transacao >= data_inicio_busca,
            Transacoes.data_transacao <= data_fim_busca,
            Transacoes.parcela_atual != 0
        ).scalar() or 0

        # Calcula o total de despesa no período
        total_despesa = db.session.query(
            db.func.sum(Transacoes.valor)
        ).filter(
            Transacoes.tipo == "Despesa",
            Transacoes.usuario_id == usuario_id,
            Transacoes.data_transacao >= data_inicio_busca,
            Transacoes.data_transacao <= data_fim_busca,
            Transacoes.parcela_atual != 0
        ).scalar() or 0

        return render_template('dashboard/transacao.html',
                                cartoes = cartoes,
                                contas = contas,
                                transacoes_agrupadas = transacoes_agrupadas,
                                total_receita = total_receita,
                                total_despesa = total_despesa,
                                categorias = categorias,
                                contas_correntes=contas_correntes, 
                                cartoes_credito=cartoes_credito,)

# -------------------------------------
# Cadastro de Transação
# -------------------------------------
@transacao_bp.route('/cadastrar', methods=['POST'])
@login_required
def cadastrarTransacao():
    try:
        usuario = current_user.id
        hoje = datetime.now().date()
        
        # 1. Captura e processamento dos dados do formulário
        conta_id          = request.form.get('conta_transacao')
        cartao_id         = request.form.get('cartao')
        categoria_id      = request.form.get('categoria_transacao')
        tipo              = request.form.get('tipo_transacao')
        descricao         = request.form.get('descricao')
        valor_parcela     = limpar_currency(request.form.get('valor_transacao'))
        data_str          = request.form.get('data_transacao')
        recorrencia       = request.form.get('recorrencia')
        num_parcelas_str  = request.form.get('num_parcelas') 
        
        data_transacao = datetime.strptime(data_str, "%Y-%m-%d").date()
        
        # Determina se a transação é parcelada e calcula valores
        num_parcelas_total = int(num_parcelas_str) if num_parcelas_str and num_parcelas_str.isdigit() and int(num_parcelas_str) > 1 else 1
        parcelado = num_parcelas_total > 1
        
        valor_registro = valor_parcela
        
        # O valor total 'cheio' (sem filtro de parcelas) é usado apenas para a transação mestra
        valor_total_cheio = valor_parcela * num_parcelas_total 
        
        transacoes_a_salvar = []
        nova_transacao = None
        
        # Variáveis de compensação
        valor_a_compensar_cartao = 0.0 # Valor total das parcelas restantes (incluindo a atual) para cartão
        valor_a_compensar_conta = 0.0  # Valor da parcela atual para a conta (se for hoje/passado)
        
        # 3. Criação da transação (mestra e parcelas/ocorrência única)
        if parcelado:
            
            # Cálculo de quantas parcelas já foram pagas/compensadas
            # Assumimos que a parcela atual (primeira a ser salva) é a parcela 'N'
            # A data da transação (data_str) é a data da PRIMEIRA parcela a ser salva (a parcela 'atual')
            
            # Calcula quantas parcelas JÁ deveriam ter ocorrido até a data atual (hoje)
            # Para manter a lógica de 'ver o futuro', o loop começa em i=1 e i representa o número da parcela (1/N, 2/N, etc.)
            
            # --- Nova Lógica para Parcelamento ---
            
            # 3.1. Cria a transação MESTRA (parcela_atual=0, valor=valor_total)
            transacao_mestra = Transacoes(
                usuario_id=usuario,
                conta_id=conta_id,
                cartao_id=cartao_id if cartao_id else None,
                categoria_id=categoria_id,
                tipo=tipo,
                descricao=descricao + f" (Mestra - {num_parcelas_total}x)",
                valor=valor_total_cheio,
                data_transacao=data_transacao,
                parcelado=True,
                parcelas_total=num_parcelas_total,
                parcela_atual=0,
                recorrencia='Sem recorrencia' 
            )
            db.session.add(transacao_mestra)
            db.session.commit() # Commit para obter o ID da mestra

            # 3.2. Cria as transações FILHAS (parcela_atual=1 a N, valor=valor_parcela)
            for i in range(1, num_parcelas_total + 1):
                # Data da parcela: data_transacao (primeira parcela) + (i-1) meses
                data_parcela = data_transacao + relativedelta(months=i-1)
                
                # Regra: Criamos TODAS as parcelas futuras, mas apenas a primeira (i=1)
                # se estiver no mês atual ou passado, afetará a conta.
                
                nova_parcela = Transacoes(
                    usuario_id=usuario,
                    conta_id=conta_id,
                    cartao_id=cartao_id if cartao_id else None,
                    categoria_id=categoria_id,
                    tipo=tipo,
                    descricao=descricao + f" ({i}/{num_parcelas_total})",
                    valor=valor_registro,
                    data_transacao=data_parcela,
                    parcelado=True,
                    parcelas_total=num_parcelas_total,
                    parcela_atual=i,
                    id_original=transacao_mestra.id,
                    recorrencia='Mensal' 
                )
                transacoes_a_salvar.append(nova_parcela)
                
                # Define a primeira transação salva como referência
                if i == 1:
                    nova_transacao = nova_parcela 
            
            db.session.add_all(transacoes_a_salvar)
            
            # 4. Cálculo da compensação - Parcelado
            
            # Compensação de Limite do Cartão (Despesa e Cartão)
            # Regra: Afeta o limite do cartão pelo VALOR TOTAL das parcelas (todas as N parcelas).
            if tipo == 'Despesa' and cartao_id:
                # O valor total 'cheio' é o valor a compensar no limite (todas as N parcelas)
                valor_a_compensar_cartao = valor_total_cheio

            # Compensação de Saldo da Conta (Receita ou Despesa em Conta)
            # Regra: Afeta o saldo da conta APENAS se a data da primeira parcela for hoje/passado.
            # Se a data for futura, a parcela ainda não compensou.
            elif conta_id and data_transacao <= hoje:
                # O valor a compensar na conta é APENAS o valor da PRIMEIRA parcela (valor_registro)
                valor_a_compensar_conta = valor_registro 

        else:
            # --- Nova Lógica para Transação Simples (Única/Recorrente) ---
            
            # Cria transação simples
            nova_transacao = Transacoes(
                usuario_id=usuario,
                conta_id=conta_id,
                cartao_id=cartao_id if cartao_id else None,
                categoria_id=categoria_id,
                tipo=tipo,
                descricao=descricao,
                valor=valor_registro,
                data_transacao=data_transacao,
                recorrencia=recorrencia,
                recorrente=recorrencia != 'Sem recorrencia',
                parcelado=False,
                parcelas_total=1,
                parcela_atual=1
            )
            db.session.add(nova_transacao)
            
            # 4. Cálculo da compensação - Única/Recorrente
            
            # Compensação de Limite do Cartão (Despesa e Cartão)
            # Regra: Afeta o limite do cartão pelo valor da transação.
            if tipo == 'Despesa' and cartao_id:
                valor_a_compensar_cartao = valor_registro

            # Compensação de Saldo da Conta (Receita ou Despesa em Conta)
            # Regra: Afeta o saldo da conta APENAS se a data da transação for hoje/passado.
            elif conta_id and data_transacao <= hoje:
                valor_a_compensar_conta = valor_registro
            
        
        # 5. Aplicação da LÓGICA DE COMPENSAÇÃO
        
        # Aplica a compensação ao LIMITE do Cartão
        if valor_a_compensar_cartao > 0 and nova_transacao.cartao_id:
            cartao_associado = Cartoes.query.filter_by(id=nova_transacao.cartao_id, usuario_id=usuario).first()
            if cartao_associado:
                cartao_associado.limite_disponivel -= valor_a_compensar_cartao
                db.session.add(cartao_associado)

        # Aplica a compensação ao SALDO da Conta
        if valor_a_compensar_conta > 0 and nova_transacao.conta_id:
            conta_associada = Contas.query.filter_by(id=nova_transacao.conta_id, usuario_id=usuario).first()
            
            if conta_associada: 
                if tipo == 'Despesa':
                    # Subtrai o valor da parcela/transação (ex: -100,00)
                    conta_associada.saldo_inicial -= valor_a_compensar_conta
                elif tipo == 'Receita':
                    # Adiciona o valor da parcela/transação (ex: +100,00)
                    conta_associada.saldo_inicial += valor_a_compensar_conta
                db.session.add(conta_associada)
        
        
        # 6. Lógica para transações recorrentes (Gera 12 ocorrências futuras)
        if not parcelado and nova_transacao.recorrente:
            db.session.flush() 
            nova_transacao.id_original = nova_transacao.id # Define a si mesma como original
            db.session.commit() 
            
            # Gera as 12 ocorrências futuras da transação recorrente
            # OBS: Assumimos que gerar_proximas_transacoes_recorrentes gera 12 ocorrências *além* da transação atual.
            ocorrencias_geradas = gerar_proximas_transacoes_recorrentes(nova_transacao, db, Transacoes, num_meses=12) 
            flash(f'Transação cadastrada com sucesso! ({ocorrencias_geradas} ocorrências recorrentes geradas para o futuro.)', 'success')
        
        # 7. Finalização e commit
        else:
            db.session.commit()
            
            if parcelado:
                valor_parcela_fmt = formatar_currency(valor_registro)
                valor_total_fmt = formatar_currency(valor_total_cheio)
                
                flash(f'Transação parcelada cadastrada com sucesso! ({num_parcelas_total} parcelas de {valor_parcela_fmt}, totalizando {valor_total_fmt}.)', 'success')
            else:
                flash('Transação cadastrada com sucesso!', 'success')
        
        return redirect(url_for('transacao.acessarTransacao'))
        
    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado', 'error')
        current_app.logger.warning(f'Erro ao cadastrar transacao: {e}')
        return redirect(url_for('transacao.acessarTransacao'))
    
# -------------------------------------
# Edição de Transação
# -------------------------------------
@transacao_bp.route('/editar', methods=['POST'])
@login_required
def editarTransacao():
    try:
        tipo = request.form.get('tipo_transacao')
        usuario_id = current_user.id
        hoje = datetime.now().date()
        transacao_editada = None
        
        transacao_id_form = request.form.get('receita_id') or request.form.get('despesa_id') 

        valor_antigo = 0.0
        cartao_id_antigo = None
        conta_id_antiga = None
        data_antiga = None 
        
        # --- Lógica de Edição de Receita ---
        if tipo == 'Receita':
            
            receita = Transacoes.query.filter(
                Transacoes.id == transacao_id_form,
                Transacoes.tipo == 'Receita',
                Transacoes.usuario_id == usuario_id
            ).first()

            if not receita:
                flash('Receita não encontrada', 'danger')
                return redirect(url_for('transacao.acessarTransacao'))

            # Guarda dados antigos para estorno
            valor_antigo = receita.valor
            conta_id_antiga = receita.conta_id
            data_antiga = receita.data_transacao 
            
            # Atualiza novos dados
            data_str                = request.form.get('data_transacao')
            nova_data               = datetime.strptime(data_str, "%Y-%m-%d").date() if data_str else receita.data_transacao
            novo_valor              = limpar_currency(request.form.get('valor_transacao')) or receita.valor
            novo_conta_id           = request.form.get('conta_transacao') or receita.conta_id
            nova_recorrencia_str    = request.form.get('recorrencia') or receita.recorrencia

            receita.conta_id        = novo_conta_id
            receita.categoria_id    = request.form.get('categoria_transacao') or receita.categoria_id
            receita.descricao       = request.form.get('descricao') or receita.descricao
            receita.valor           = novo_valor
            receita.data_transacao  = nova_data
            receita.recorrencia     = nova_recorrencia_str
            receita.recorrente      = nova_recorrencia_str != 'Sem recorrencia'
            
            transacao_editada = receita

            
            # 1. Compensação Antiga (Estorno da Receita na conta antiga)
            # Regra: Só estorna se a data da transação antiga já compensou o saldo
            conta_antiga = Contas.query.filter_by(id=conta_id_antiga, usuario_id=usuario_id).first()
            if conta_antiga and data_antiga <= hoje: 
                conta_antiga.saldo_inicial -= valor_antigo # Estorna o valor antigo
                db.session.add(conta_antiga)

            # 2. Aplicação Nova (Aplica a nova Receita na conta nova)
            # Regra: Só aplica se a nova data da transação deve compensar o saldo
            conta_nova = Contas.query.filter_by(id=receita.conta_id, usuario_id=usuario_id).first()
            if conta_nova and receita.data_transacao <= hoje: 
                conta_nova.saldo_inicial += receita.valor # Aplica o novo valor
                db.session.add(conta_nova)

        # --- Lógica de Edição de Despesa ---
        elif tipo == 'Despesa':
            despesa_id = request.form.get('despesa_id')
            
            despesa = Transacoes.query.filter(
                Transacoes.id == despesa_id,
                Transacoes.tipo == 'Despesa',
                Transacoes.usuario_id == usuario_id
            ).first()

            if not despesa:
                flash('Despesa não encontrada', 'error')
                return redirect(url_for('transacao.acessarTransacao'))

            # Guarda dados antigos para estorno
            valor_antigo            = despesa.valor
            cartao_id_antigo        = despesa.cartao_id
            conta_id_antiga         = despesa.conta_id
            data_antiga             = despesa.data_transacao 

            # Atualiza novos dados
            data_str                = request.form.get('data_transacao')
            nova_data               = datetime.strptime(data_str, "%Y-%m-%d").date() if data_str else despesa.data_transacao
            novo_valor              = limpar_currency(request.form.get('valor_transacao'))
            novo_cartao_id          = request.form.get('cartao')
            novo_conta_id           = request.form.get('conta_transacao')
            
            novo_cartao_id          = novo_cartao_id if novo_cartao_id else None
            nova_recorrencia_str    = request.form.get('recorrencia') or despesa.recorrencia

            # Atualiza a transação
            despesa.conta_id          = novo_conta_id or despesa.conta_id
            despesa.cartao_id         = novo_cartao_id 
            despesa.categoria_id      = request.form.get('categoria_transacao') or despesa.categoria_id
            despesa.descricao         = request.form.get('descricao') or despesa.descricao
            despesa.valor             = novo_valor or despesa.valor
            despesa.data_transacao    = nova_data
            despesa.recorrencia       = nova_recorrencia_str
            despesa.recorrente        = nova_recorrencia_str != 'Sem recorrencia'
            transacao_editada         = despesa
    
            
            # 1. Estorno do pagamento antigo
            # Se o pagamento ANTIGO era CARTÃO: Devolve o limite (sem verificação de data, pois afeta o total comprometido)
            if cartao_id_antigo:
                cartao_antigo = Cartoes.query.filter_by(id=cartao_id_antigo, usuario_id=usuario_id).first()
                if cartao_antigo:
                    # Se for parcelado, aqui deve-se estornar o valor TOTAL da série, mas
                    # como a edição de séries mestras é tratada na recorrência, aqui focamos no valor individual.
                    if not despesa.parcelado:
                         cartao_antigo.limite_disponivel += valor_antigo
                         db.session.add(cartao_antigo)
            
            # Se o pagamento ANTIGO era CONTA: Restaura o saldo (usa a DATA ANTIGA)
            # Regra: Só estorna se a data da transação antiga já compensou o saldo
            elif conta_id_antiga: 
                conta_antiga = Contas.query.filter_by(id=conta_id_antiga, usuario_id=usuario_id).first()
                if conta_antiga and data_antiga <= hoje: 
                    conta_antiga.saldo_inicial += valor_antigo # Restaura o saldo antigo
                    db.session.add(conta_antiga)


            # 2. Aplicação do novo pagamento
            # Se o pagamento NOVO é CARTÃO: Subtrai o novo limite (sem verificação de data)
            if despesa.cartao_id:
                cartao_novo = Cartoes.query.filter_by(id=despesa.cartao_id, usuario_id=usuario_id).first()
                if cartao_novo:
                    # Se for parcelado, aqui deve-se subtrair o valor TOTAL da série.
                    if not despesa.parcelado:
                        cartao_novo.limite_disponivel -= despesa.valor 
                        db.session.add(cartao_novo)

            # Se o pagamento NOVO é CONTA: Subtrai o novo saldo
            # Regra: Só aplica se a nova data da transação deve compensar o saldo
            elif despesa.cartao_id is None and despesa.conta_id:
                conta_nova = Contas.query.filter_by(id=despesa.conta_id, usuario_id=usuario_id).first()
                if conta_nova and despesa.data_transacao <= hoje: 
                    conta_nova.saldo_inicial -= despesa.valor
                    db.session.add(conta_nova)


        # Lógica de re-geração de recorrência (aplica-se apenas a transações não parceladas)
        if transacao_editada and not transacao_editada.parcelado:
            is_mestra = transacao_editada.id_original == transacao_editada.id or transacao_editada.id_original is None

            if is_mestra:
                if transacao_editada.recorrente:
                    if transacao_editada.id_original is None:
                        transacao_editada.id_original = transacao_editada.id
                    
                    # Deleta ocorrências futuras (que não compensaram o saldo/limite)
                    Transacoes.query.filter(
                        Transacoes.id_original == transacao_editada.id_original,
                        Transacoes.id != transacao_editada.id,
                        Transacoes.data_transacao > hoje, # Mantém apenas a transação atual e as passadas
                        Transacoes.usuario_id == usuario_id
                    ).delete(synchronize_session=False)

                    db.session.add(transacao_editada)
                    db.session.flush()
                    
                    # Gera novas 12 ocorrências futuras
                    ocorrencias_geradas = gerar_proximas_transacoes_recorrentes(transacao_editada, db, Transacoes, num_meses=12)
                    
                    db.session.commit()
                    flash(f'{tipo} mestra atualizada. {ocorrencias_geradas} ocorrências futuras regeradas!', 'success')
                    
                else:
                    # Deleta todas as recorrências futuras se o tipo mudou para 'Sem recorrencia'
                    Transacoes.query.filter(
                        Transacoes.id_original == transacao_editada.id, 
                        Transacoes.id != transacao_editada.id,
                        Transacoes.data_transacao > hoje, # Deleta apenas as futuras
                        Transacoes.usuario_id == usuario_id
                    ).delete(synchronize_session=False)
                    
                    transacao_editada.recorrente = False
                    transacao_editada.recorrencia = 'Sem recorrencia'
                    
                    db.session.add(transacao_editada)
                    db.session.commit()
                    flash(f'{tipo} convertida para transação simples. Ocorrências futuras excluídas.', 'success')

            else:
                # Transação individual (não mestra)
                db.session.commit()
                flash(f'{tipo} individual atualizada com sucesso', 'success')
        
        else:
            # Transação parcelada (não tem lógica de re-geração de recorrência aqui)
            db.session.commit()
            flash(f'{tipo} atualizada com sucesso', 'success')

        return redirect(url_for('transacao.acessarTransacao'))
        
    except Exception as e:
        db.session.rollback()
        flash('Ocorreu algum erro inesperado', 'error')
        current_app.logger.warning(f'Erro ao editar transacao: {e}')
        return redirect(url_for('transacao.acessarTransacao'))

# -------------------------------------
# Deleção de Transação
# -------------------------------------
@transacao_bp.route('/deletar/<int:transacao_id>', methods=['GET', 'POST'])
@login_required
def deletarTransacao(transacao_id):
    try:
        usuario_id = current_user.id
        hoje = datetime.now().date()
        
        transacao = Transacoes.query.filter(
            Transacoes.id == transacao_id, 
            Transacoes.usuario_id == usuario_id
        ).first()

        if not transacao:
            flash('Transação não encontrada', 'error')
            return redirect(url_for('transacao.acessarTransacao'))
        
        # --- Lógica de deleção para transação simples (não parcelada e não recorrente) ---
        if not transacao.parcelado and not transacao.recorrente:
            
            # Estorno de Limite do Cartão (Despesa) - Sempre estorna o valor
            if transacao.tipo == 'Despesa' and transacao.cartao_id:
                cartao = Cartoes.query.filter_by(id=transacao.cartao_id, usuario_id=usuario_id).first()
                if cartao:
                    cartao.limite_disponivel += transacao.valor 
                    db.session.add(cartao)

            # Estorno de Saldo da Conta (Despesa ou Receita)
            # Regra: Só estorna o saldo se a transação já tiver compensado (data <= hoje)
            elif transacao.conta_id and transacao.data_transacao <= hoje:
                conta = Contas.query.filter_by(id=transacao.conta_id, usuario_id=usuario_id).first()
                if conta:
                    if transacao.tipo == 'Despesa':
                        conta.saldo_inicial += transacao.valor
                    elif transacao.tipo == 'Receita':
                        conta.saldo_inicial -= transacao.valor
                    db.session.add(conta)
            
            # Deleção da transação simples
            db.session.delete(transacao)
            db.session.commit()
            flash('Transação excluída com sucesso', 'success')
            return redirect(url_for('transacao.acessarTransacao'))


        # --- Lógica de deleção para séries (parcelada ou recorrente) ---
        id_mestra = transacao.id_original if transacao.id_original else transacao.id
        mestra = Transacoes.query.filter_by(id=id_mestra, usuario_id=usuario_id).first()
        
        if mestra:
            
            # Estorno de Limite do Cartão (Despesa parcelada/recorrente)
            # Regra: Estorna o valor TOTAL da série (valor da Mestra)
            if mestra.tipo == 'Despesa' and mestra.cartao_id:
                cartao = Cartoes.query.filter_by(id=mestra.cartao_id, usuario_id=usuario_id).first()
                if cartao:
                    # O valor da mestra (mestra.valor) é o valor total.
                    cartao.limite_disponivel += mestra.valor 
                    db.session.add(cartao)
                    

            if mestra.conta_id:
                # Estorno de Saldo da Conta (Despesa ou Receita parcelada/recorrente)
                deve_estornar_saldo = (mestra.tipo == 'Receita') or (mestra.tipo == 'Despesa' and not mestra.cartao_id)
                if deve_estornar_saldo:
                    conta = Contas.query.filter_by(id=mestra.conta_id, usuario_id=usuario_id).first()
                    if conta:
                        # Busca APENAS a transação da série que já deveria ter compensado o saldo
                        # Pela nova lógica, isso é APENAS a primeira transação da série se data <= hoje
                        
                        # 1. Identifica o ID da transação que compensou (a primeira parcela/ocorrência)
                        if mestra.parcelado:
                            # A transação que compensou é a primeira parcela
                            compensadora = Transacoes.query.filter(
                                Transacoes.id_original == id_mestra,
                                Transacoes.usuario_id == usuario_id,
                                Transacoes.parcela_atual == 1
                            ).first()
                        else:
                            # A transação que compensou é a própria mestra
                            compensadora = mestra

                        valor_total_estorno_saldo = 0.0
                        
                        # 2. Verifica se a transação compensou o saldo
                        if compensadora and compensadora.data_transacao <= hoje:
                             # Pela nova regra de cadastro, apenas a primeira parcela/ocorrência (se atual/passada)
                             # afeta o saldo.
                             valor_total_estorno_saldo = compensadora.valor 
                        
                        if valor_total_estorno_saldo > 0:
                            if mestra.tipo == 'Despesa':
                                conta.saldo_inicial += valor_total_estorno_saldo # Despesa estornada (soma)
                            elif mestra.tipo == 'Receita':
                                conta.saldo_inicial -= valor_total_estorno_saldo # Receita estornada (subtrai)
                            db.session.add(conta)
            
            is_parcelado = mestra.parcelado
            
            # Deleção de todas as transações da série (mestra e filhas)
            Transacoes.query.filter(
                (Transacoes.id == id_mestra) | (Transacoes.id_original == id_mestra),
                Transacoes.usuario_id == usuario_id
            ).delete(synchronize_session=False)

            db.session.commit()
            
            tipo_serie = 'parcelada' if is_parcelado else 'recorrente'
            flash(f'Série de transações ({tipo_serie}) excluída com sucesso! O limite/saldo foi restaurado.', 'success')
            return redirect(url_for('transacao.acessarTransacao'))

        # Fallback (Mestra não encontrada)
        flash('Erro ao deletar: Transação mestra não encontrada.', 'error')
        return redirect(url_for('transacao.acessarTransacao'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.warning(f'Erro ao deletar transacao: {e}')
        flash('Ocorreu algum erro inesperado', 'error')
        return redirect(url_for('transacao.acessarTransacao'))