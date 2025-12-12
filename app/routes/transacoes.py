from datetime import date, datetime
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
# Cadastro de Transação (versão endurecida: detecta nome do campo de saldo e logs)
# -------------------------------------
@transacao_bp.route('/cadastrar', methods=['POST'])
@login_required
def cadastrarTransacao():
    try:
        usuario = current_user.id
        hoje = datetime.now().date()

        # 1. Captura e processamento dos dados do formulário
        conta_id_raw       = request.form.get('conta_transacao')
        cartao_id_raw      = request.form.get('cartao')
        categoria_id_raw   = request.form.get('categoria_transacao')
        tipo               = request.form.get('tipo_transacao')
        descricao          = request.form.get('descricao')
        valor_parcela      = limpar_currency(request.form.get('valor_transacao'))
        data_str           = request.form.get('data_transacao')
        recorrencia        = request.form.get('recorrencia')
        num_parcelas_str   = request.form.get('num_parcelas')

        # Checkbox
        receita_ja_incluida_raw = request.form.get('receita_ja_incluida') == 'on'

        # Conversões robustas de IDs (string -> int ou None)
        def to_int_or_none(v):
            try:
                return int(v) if v not in (None, '', 'None') else None
            except (ValueError, TypeError):
                return None

        conta_id_int     = to_int_or_none(conta_id_raw)
        cartao_id_int    = to_int_or_none(cartao_id_raw)
        categoria_id_int = to_int_or_none(categoria_id_raw)

        # Valida data
        data_transacao = datetime.strptime(data_str, "%Y-%m-%d").date()

        # Parcelamento
        num_parcelas_total = int(num_parcelas_str) if num_parcelas_str and num_parcelas_str.isdigit() and int(num_parcelas_str) > 1 else 1
        parcelado = num_parcelas_total > 1

        valor_registro = float(valor_parcela or 0.0)
        valor_total_cheio = valor_registro * num_parcelas_total

        transacoes_a_salvar = []
        nova_transacao = None

        # Variáveis de compensação
        valor_a_compensar_cartao = 0.0
        valor_a_compensar_conta = 0.0

        # Helper: data é do mês/ano atual?
        def data_e_mes_atual(dt: date):
            return dt.month == hoje.month and dt.year == hoje.year

        # A marcação só é aplicável se:
        # - checkbox marcado
        # - tipo == 'Receita'
        # - conta vinculada (id inteiro)
        # - data da transação é do mês atual
        receita_ja_incluida_aplicavel = (
            receita_ja_incluida_raw
            and tipo == 'Receita'
            and conta_id_int is not None
            and data_e_mes_atual(data_transacao)
        )

        current_app.logger.debug(f"[cadastrarTransacao] inicio usuario={usuario} tipo={tipo} valor={valor_registro} data={data_transacao} conta={conta_id_int} cartao={cartao_id_int} parcelado={parcelado} receita_ja_incluida_raw={receita_ja_incluida_raw}")

        # 3. Criação das transações
        if parcelado:
            transacao_mestra = Transacoes(
                usuario_id=usuario,
                conta_id=conta_id_int,
                cartao_id=cartao_id_int,
                categoria_id=categoria_id_int,
                tipo=tipo,
                descricao=(descricao + f" (Mestra - {num_parcelas_total}x)"),
                valor=valor_total_cheio,
                data_transacao=data_transacao,
                parcelado=True,
                parcelas_total=num_parcelas_total,
                parcela_atual=0,
                recorrencia='Sem recorrencia'
            )
            db.session.add(transacao_mestra)
            db.session.commit()  # garante ID da mestra

            for i in range(1, num_parcelas_total + 1):
                data_parcela = data_transacao + relativedelta(months=i-1)
                flag_receita_ja_incluida = (i == 1) and receita_ja_incluida_aplicavel

                nova_parcela = Transacoes(
                    usuario_id=usuario,
                    conta_id=conta_id_int,
                    cartao_id=cartao_id_int,
                    categoria_id=categoria_id_int,
                    tipo=tipo,
                    descricao=(descricao + f" ({i}/{num_parcelas_total})"),
                    valor=valor_registro,
                    data_transacao=data_parcela,
                    parcelado=True,
                    parcelas_total=num_parcelas_total,
                    parcela_atual=i,
                    id_original=transacao_mestra.id,
                    recorrencia='Mensal',
                    receita_ja_incluida=bool(flag_receita_ja_incluida)
                )
                transacoes_a_salvar.append(nova_parcela)
                if i == 1:
                    nova_transacao = nova_parcela

            db.session.add_all(transacoes_a_salvar)

            # Compensacoes parcelado
            if tipo == 'Despesa' and cartao_id_int:
                valor_a_compensar_cartao = valor_total_cheio
            elif conta_id_int is not None and data_transacao <= hoje:
                if not (tipo == 'Receita' and receita_ja_incluida_aplicavel):
                    valor_a_compensar_conta = valor_registro
                else:
                    valor_a_compensar_conta = 0.0

        else:
            flag_receita_ja_incluida_para_unica = receita_ja_incluida_aplicavel

            nova_transacao = Transacoes(
                usuario_id=usuario,
                conta_id=conta_id_int,
                cartao_id=cartao_id_int,
                categoria_id=categoria_id_int,
                tipo=tipo,
                descricao=descricao,
                valor=valor_registro,
                data_transacao=data_transacao,
                recorrencia=recorrencia,
                recorrente=(recorrencia != 'Sem recorrencia'),
                parcelado=False,
                parcelas_total=1,
                parcela_atual=1,
                receita_ja_incluida=bool(flag_receita_ja_incluida_para_unica)
            )
            db.session.add(nova_transacao)

            # Compensacoes unica/recorrente
            if tipo == 'Despesa' and cartao_id_int:
                valor_a_compensar_cartao = valor_registro
            elif conta_id_int is not None and data_transacao <= hoje:
                if not (tipo == 'Receita' and flag_receita_ja_incluida_para_unica):
                    valor_a_compensar_conta = valor_registro
                else:
                    valor_a_compensar_conta = 0.0

        current_app.logger.debug(f"[cadastrarTransacao] compensacoes calculadas cartao={valor_a_compensar_cartao} conta={valor_a_compensar_conta}")

        # 5. Aplicacao das compensacoes
        # 5.1 Limite do cartao
        if valor_a_compensar_cartao > 0 and cartao_id_int:
            cartao_associado = Cartoes.query.filter_by(id=cartao_id_int, usuario_id=usuario).first()
            if cartao_associado:
                cartao_associado.limite_disponivel = (cartao_associado.limite_disponivel or 0.0) - valor_a_compensar_cartao
                db.session.add(cartao_associado)
                current_app.logger.debug(f"[cadastrarTransacao] limite cartao atualizado id={cartao_id_int} novo_limite={cartao_associado.limite_disponivel}")
            else:
                current_app.logger.debug(f"[cadastrarTransacao] cartao_id {cartao_id_int} nao encontrado para usuario {usuario}")

        # 5.2 Saldo da conta: detecta nome do atributo e atualiza
        if conta_id_int:
            if valor_a_compensar_conta > 0:
                conta_associada = Contas.query.filter_by(id=conta_id_int, usuario_id=usuario).first()
                if not conta_associada:
                    current_app.logger.debug(f"[cadastrarTransacao] conta_id {conta_id_int} nao encontrada para usuario {usuario}")
                else:
                    # Detecta qual campo de saldo existe
                    saldo_field_candidates = ['saldo_inicial', 'saldo_atual', 'saldo', 'balanco']
                    field_found = None
                    for f in saldo_field_candidates:
                        if hasattr(conta_associada, f):
                            field_found = f
                            break

                    if not field_found:
                        current_app.logger.warning(f"[cadastrarTransacao] Nenhum campo de saldo conhecido ({saldo_field_candidates}) encontrado no modelo Contas. Não foi possível atualizar saldo para conta {conta_id_int}.")
                    else:
                        current_saldo = getattr(conta_associada, field_found) or 0.0
                        new_saldo = current_saldo - valor_a_compensar_conta if tipo == 'Despesa' else current_saldo + valor_a_compensar_conta

                        # Atualiza e loga
                        setattr(conta_associada, field_found, new_saldo)
                        db.session.add(conta_associada)
                        current_app.logger.debug(f"[cadastrarTransacao] Atualizado campo '{field_found}' da conta {conta_id_int}: {current_saldo} -> {new_saldo} (tipo={tipo}, ajuste={valor_a_compensar_conta})")

        # 6. Recorrentes: gerar próximas ocorrências (se aplicável)
        if not parcelado and nova_transacao.recorrente:
            db.session.flush()
            nova_transacao.id_original = nova_transacao.id
            db.session.commit()

            ocorrencias_geradas = gerar_proximas_transacoes_recorrentes(nova_transacao, db, Transacoes, num_meses=12)
            flash(f'Transação cadastrada com sucesso! ({ocorrencias_geradas} ocorrências recorrentes geradas para o futuro.)', 'success')
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
        current_app.logger.warning(f'Erro ao cadastrar transacao: {e}', exc_info=True)
        flash('Ocorreu algum erro inesperado', 'error')
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

        # helper: converte string -> int ou None
        def to_int_or_none(v):
            try:
                return int(v) if v not in (None, '', 'None') else None
            except (ValueError, TypeError):
                return None

        # helper: detecta campo de saldo no modelo Contas
        def detectar_campo_saldo(conta_obj):
            candidatos = ['saldo_inicial', 'saldo_atual', 'saldo', 'balanco']
            for f in candidatos:
                if hasattr(conta_obj, f):
                    return f
            return None

        transacao_id_form = request.form.get('receita_id') or request.form.get('despesa_id')
        transacao_id_int = to_int_or_none(transacao_id_form)

        if not transacao_id_int:
            flash('ID de transação inválido', 'error')
            return redirect(url_for('transacao.acessarTransacao'))

        # --- Lógica de Edição de Receita ---
        if tipo == 'Receita':
            receita = Transacoes.query.filter(
                Transacoes.id == transacao_id_int,
                Transacoes.tipo == 'Receita',
                Transacoes.usuario_id == usuario_id
            ).first()

            if not receita:
                flash('Receita não encontrada', 'danger')
                return redirect(url_for('transacao.acessarTransacao'))

            # Guarda dados antigos para estorno/checagens
            valor_antigo = float(receita.valor or 0.0)
            conta_id_antiga = to_int_or_none(receita.conta_id)
            data_antiga = receita.data_transacao
            flag_antiga_receita_ja_incluida = bool(getattr(receita, 'receita_ja_incluida', False))

            # Lê novos dados do formulário
            data_str = request.form.get('data_transacao')
            nova_data = datetime.strptime(data_str, "%Y-%m-%d").date() if data_str else receita.data_transacao
            novo_valor = float(limpar_currency(request.form.get('valor_transacao'))) if request.form.get('valor_transacao') else float(receita.valor or 0.0)
            novo_conta_id_raw = request.form.get('conta_transacao')
            novo_conta_id = to_int_or_none(novo_conta_id_raw) if novo_conta_id_raw is not None else conta_id_antiga
            nova_recorrencia_str = request.form.get('recorrencia') or receita.recorrencia

            # Lê checkbox e determina aplicabilidade (mesma regra da criação: só aplica se tipo=Receita, conta preenchida e data no mês atual)
            receita_ja_incluida_raw = request.form.get('receita_ja_incluida') == 'on'
            def data_e_mes_atual(dt):
                return dt.month == hoje.month and dt.year == hoje.year
            nova_receita_ja_incluida_aplicavel = (
                receita_ja_incluida_raw
                and novo_conta_id is not None
                and data_e_mes_atual(nova_data)
            )

            # Atualiza campos na transação (incluindo a flag, que salvamos conforme aplicabilidade)
            receita.conta_id = novo_conta_id
            receita.categoria_id = to_int_or_none(request.form.get('categoria_transacao')) or receita.categoria_id
            receita.descricao = request.form.get('descricao') or receita.descricao
            receita.valor = novo_valor
            receita.data_transacao = nova_data
            receita.recorrencia = nova_recorrencia_str
            receita.recorrente = (nova_recorrencia_str != 'Sem recorrencia')
            receita.receita_ja_incluida = bool(nova_receita_ja_incluida_aplicavel)

            transacao_editada = receita

            current_app.logger.debug(f"[editarTransacao][receita] id={receita.id} antigo_valor={valor_antigo} novo_valor={novo_valor} conta_antiga={conta_id_antiga} conta_nova={novo_conta_id} data_antiga={data_antiga} data_nova={nova_data} antiga_flag={flag_antiga_receita_ja_incluida} nova_flag={receita.receita_ja_incluida}")

            # 1) ESTORNO do valor antigo: só se a transação antiga realmente havia compensado o saldo
            # e só se NÃO estava marcada como 'receita_ja_incluida'
            if conta_id_antiga and data_antiga <= hoje and not flag_antiga_receita_ja_incluida:
                conta_antiga = Contas.query.filter_by(id=conta_id_antiga, usuario_id=usuario_id).first()
                if conta_antiga:
                    campo_saldo = detectar_campo_saldo(conta_antiga)
                    if campo_saldo:
                        atual = getattr(conta_antiga, campo_saldo) or 0.0
                        novo = atual - valor_antigo  # estorna a receita antiga (subtrai)
                        setattr(conta_antiga, campo_saldo, novo)
                        db.session.add(conta_antiga)
                        current_app.logger.debug(f"[editarTransacao] estorno aplicado conta_antiga id={conta_id_antiga} campo={campo_saldo} {atual} -> {novo}")
                    else:
                        current_app.logger.warning(f"[editarTransacao] conta_antiga id={conta_id_antiga} não possui campo de saldo conhecido.")

            # 2) APLICAÇÃO do novo valor: só se a nova transação deve compensar o saldo
            # e só se a nova transação NÃO estiver marcada como 'receita_ja_incluida'
            if novo_conta_id and receita.data_transacao <= hoje and not receita.receita_ja_incluida:
                conta_nova = Contas.query.filter_by(id=novo_conta_id, usuario_id=usuario_id).first()
                if conta_nova:
                    campo_saldo = detectar_campo_saldo(conta_nova)
                    if campo_saldo:
                        atual = getattr(conta_nova, campo_saldo) or 0.0
                        novo = atual + float(receita.valor or 0.0)
                        setattr(conta_nova, campo_saldo, novo)
                        db.session.add(conta_nova)
                        current_app.logger.debug(f"[editarTransacao] aplicação novo valor conta_nova id={novo_conta_id} campo={campo_saldo} {atual} -> {novo}")
                    else:
                        current_app.logger.warning(f"[editarTransacao] conta_nova id={novo_conta_id} não possui campo de saldo conhecido.")

        # --- Lógica de Edição de Despesa ---
        elif tipo == 'Despesa':
            despesa_id = transacao_id_int

            despesa = Transacoes.query.filter(
                Transacoes.id == despesa_id,
                Transacoes.tipo == 'Despesa',
                Transacoes.usuario_id == usuario_id
            ).first()

            if not despesa:
                flash('Despesa não encontrada', 'error')
                return redirect(url_for('transacao.acessarTransacao'))

            # Guarda dados antigos
            valor_antigo = float(despesa.valor or 0.0)
            cartao_id_antigo = to_int_or_none(despesa.cartao_id)
            conta_id_antiga = to_int_or_none(despesa.conta_id)
            data_antiga = despesa.data_transacao

            # Lê novos dados
            data_str = request.form.get('data_transacao')
            nova_data = datetime.strptime(data_str, "%Y-%m-%d").date() if data_str else despesa.data_transacao
            novo_valor = float(limpar_currency(request.form.get('valor_transacao'))) if request.form.get('valor_transacao') else float(despesa.valor or 0.0)
            novo_cartao_id = to_int_or_none(request.form.get('cartao'))
            novo_conta_id = to_int_or_none(request.form.get('conta_transacao'))
            nova_recorrencia_str = request.form.get('recorrencia') or despesa.recorrencia

            # Atualiza campos
            despesa.conta_id = novo_conta_id or despesa.conta_id
            despesa.cartao_id = novo_cartao_id
            despesa.categoria_id = to_int_or_none(request.form.get('categoria_transacao')) or despesa.categoria_id
            despesa.descricao = request.form.get('descricao') or despesa.descricao
            despesa.valor = novo_valor or despesa.valor
            despesa.data_transacao = nova_data
            despesa.recorrencia = nova_recorrencia_str
            despesa.recorrente = (nova_recorrencia_str != 'Sem recorrencia')
            transacao_editada = despesa

            # Debug
            current_app.logger.debug(f"[editarTransacao][despesa] id={despesa.id} antigo_valor={valor_antigo} novo_valor={despesa.valor} cartao_antigo={cartao_id_antigo} cartao_novo={despesa.cartao_id} conta_antiga={conta_id_antiga} conta_nova={despesa.conta_id}")

            # 1) Estorno do pagamento antigo
            if cartao_id_antigo:
                cartao_antigo = Cartoes.query.filter_by(id=cartao_id_antigo, usuario_id=usuario_id).first()
                if cartao_antigo and not despesa.parcelado:
                    cartao_antigo.limite_disponivel = (cartao_antigo.limite_disponivel or 0.0) + valor_antigo
                    db.session.add(cartao_antigo)
                    current_app.logger.debug(f"[editarTransacao] estorno limite cartao id={cartao_id_antigo} +{valor_antigo}")

            elif conta_id_antiga:
                # estorna saldo antigo se a antiga data já compensou
                if data_antiga <= hoje:
                    conta_antiga = Contas.query.filter_by(id=conta_id_antiga, usuario_id=usuario_id).first()
                    if conta_antiga:
                        campo_saldo = detectar_campo_saldo(conta_antiga)
                        if campo_saldo:
                            atual = getattr(conta_antiga, campo_saldo) or 0.0
                            novo = atual + valor_antigo
                            setattr(conta_antiga, campo_saldo, novo)
                            db.session.add(conta_antiga)
                            current_app.logger.debug(f"[editarTransacao] estorno saldo conta_antiga id={conta_id_antiga} {atual} -> {novo}")

            # 2) Aplicação do novo pagamento
            if despesa.cartao_id:
                cartao_novo = Cartoes.query.filter_by(id=despesa.cartao_id, usuario_id=usuario_id).first()
                if cartao_novo and not despesa.parcelado:
                    cartao_novo.limite_disponivel = (cartao_novo.limite_disponivel or 0.0) - float(despesa.valor or 0.0)
                    db.session.add(cartao_novo)
                    current_app.logger.debug(f"[editarTransacao] subtracao limite cartao id={despesa.cartao_id} -{despesa.valor}")

            elif despesa.cartao_id is None and despesa.conta_id:
                if despesa.data_transacao <= hoje:
                    conta_nova = Contas.query.filter_by(id=despesa.conta_id, usuario_id=usuario_id).first()
                    if conta_nova:
                        campo_saldo = detectar_campo_saldo(conta_nova)
                        if campo_saldo:
                            atual = getattr(conta_nova, campo_saldo) or 0.0
                            novo = atual - float(despesa.valor or 0.0)
                            setattr(conta_nova, campo_saldo, novo)
                            db.session.add(conta_nova)
                            current_app.logger.debug(f"[editarTransacao] subtracao saldo conta_nova id={despesa.conta_id} {atual} -> {novo}")

        else:
            # Tipo inválido
            flash('Tipo de transação inválido', 'error')
            return redirect(url_for('transacao.acessarTransacao'))

        # Lógica de re-geração de recorrência (aplica-se apenas a transações não parceladas)
        if transacao_editada and not transacao_editada.parcelado:
            is_mestra = (transacao_editada.id_original == transacao_editada.id) or (transacao_editada.id_original is None)

            if is_mestra:
                if transacao_editada.recorrente:
                    if transacao_editada.id_original is None:
                        transacao_editada.id_original = transacao_editada.id

                    # Deleta ocorrências futuras (que não compensaram saldo/limite)
                    Transacoes.query.filter(
                        Transacoes.id_original == transacao_editada.id_original,
                        Transacoes.id != transacao_editada.id,
                        Transacoes.data_transacao > hoje,
                        Transacoes.usuario_id == usuario_id
                    ).delete(synchronize_session=False)

                    db.session.add(transacao_editada)
                    db.session.flush()

                    # Gera novas ocorrências futuras
                    ocorrencias_geradas = gerar_proximas_transacoes_recorrentes(transacao_editada, db, Transacoes, num_meses=12)

                    db.session.commit()
                    flash(f'{tipo} mestra atualizada. {ocorrencias_geradas} ocorrências futuras regeradas!', 'success')

                else:
                    # Deleta todas as recorrências futuras se convertido para simples
                    Transacoes.query.filter(
                        Transacoes.id_original == transacao_editada.id,
                        Transacoes.id != transacao_editada.id,
                        Transacoes.data_transacao > hoje,
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
            # Transação parcelada ou outras: commit simples
            db.session.commit()
            flash(f'{tipo} atualizada com sucesso', 'success')

        return redirect(url_for('transacao.acessarTransacao'))

    except Exception as e:
        db.session.rollback()
        current_app.logger.warning(f'Erro ao editar transacao: {e}', exc_info=True)
        flash('Ocorreu algum erro inesperado', 'error')
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
        
        # ============================================================
        # 1. DELEÇÃO DE TRANSAÇÃO SIMPLES (NÃO PARCELADA / NÃO RECORRENTE)
        # ============================================================
        if not transacao.parcelado and not transacao.recorrente:
            
            # Estorno do limite do cartão (somente despesas)
            if transacao.tipo == 'Despesa' and transacao.cartao_id:
                cartao = Cartoes.query.filter_by(id=transacao.cartao_id, usuario_id=usuario_id).first()
                if cartao:
                    cartao.limite_disponivel += transacao.valor
                    db.session.add(cartao)

            # Estorno do saldo da conta
            # Mas apenas se:
            #   - tem conta vinculada
            #   - data já compensou
            #   - NÃO foi marcada como "Receita já incluída"
            elif transacao.conta_id and transacao.data_transacao <= hoje and not transacao.receita_ja_incluida:
                conta = Contas.query.filter_by(id=transacao.conta_id, usuario_id=usuario_id).first()
                if conta:
                    if transacao.tipo == 'Despesa':
                        conta.saldo_inicial += transacao.valor
                    elif transacao.tipo == 'Receita':
                        conta.saldo_inicial -= transacao.valor
                    db.session.add(conta)
            
            db.session.delete(transacao)
            db.session.commit()
            flash('Transação excluída com sucesso', 'success')
            return redirect(url_for('transacao.acessarTransacao'))


        # ============================================================
        # 2. DELEÇÃO DE SÉRIE (PARCELADA OU RECORRENTE)
        # ============================================================
        id_mestra = transacao.id_original if transacao.id_original else transacao.id
        mestra = Transacoes.query.filter_by(id=id_mestra, usuario_id=usuario_id).first()
        
        if mestra:
            # Estorno do limite do cartão
            if mestra.tipo == 'Despesa' and mestra.cartao_id:
                cartao = Cartoes.query.filter_by(id=mestra.cartao_id, usuario_id=usuario_id).first()
                if cartao:
                    cartao.limite_disponivel += mestra.valor
                    db.session.add(cartao)

            # Estorno do saldo da conta
            if mestra.conta_id:
                deve_estornar_saldo = (
                    (mestra.tipo == 'Receita') or
                    (mestra.tipo == 'Despesa' and not mestra.cartao_id)
                )

                if deve_estornar_saldo:
                    conta = Contas.query.filter_by(id=mestra.conta_id, usuario_id=usuario_id).first()
                    if conta:

                        # Localizar a parcela que compensou saldo
                        if mestra.parcelado:
                            compensadora = Transacoes.query.filter(
                                Transacoes.id_original == id_mestra,
                                Transacoes.parcela_atual == 1,
                                Transacoes.usuario_id == usuario_id
                            ).first()
                        else:
                            compensadora = mestra

                        valor_estorno = 0.0

                        # Só estorna se:
                        #   - já compensou (data <= hoje)
                        #   - NÃO era "Receita já incluída"
                        if compensadora and compensadora.data_transacao <= hoje and not compensadora.receita_ja_incluida:
                            valor_estorno = compensadora.valor

                        if valor_estorno > 0:
                            if mestra.tipo == 'Despesa':
                                conta.saldo_inicial += valor_estorno
                            elif mestra.tipo == 'Receita':
                                conta.saldo_inicial -= valor_estorno
                            db.session.add(conta)
            
            is_parcelado = mestra.parcelado
            
            # Exclui toda a série
            Transacoes.query.filter(
                (Transacoes.id == id_mestra) | (Transacoes.id_original == id_mestra),
                Transacoes.usuario_id == usuario_id
            ).delete(synchronize_session=False)

            db.session.commit()
            
            tipo_serie = 'parcelada' if is_parcelado else 'recorrente'
            flash(f'Série de transações ({tipo_serie}) excluída com sucesso!', 'success')
            return redirect(url_for('transacao.acessarTransacao'))

        flash('Erro ao deletar: Transação mestra não encontrada.', 'error')
        return redirect(url_for('transacao.acessarTransacao'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.warning(f'Erro ao deletar transacao: {e}')
        flash('Ocorreu algum erro inesperado', 'error')
        return redirect(url_for('transacao.acessarTransacao'))
