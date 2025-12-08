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

        data_inicio_busca = hoje + relativedelta(months=-12, day=1)
        data_fim_busca = hoje + relativedelta(months=+12, day=31)
        
        cartoes = Cartoes.query.filter_by(usuario_id=usuario_id).all()
        contas = Contas.query.filter_by(usuario_id=usuario_id).all()
        categorias = Categorias.query.filter_by(usuario_id=usuario_id).all()

        transacoes_filtradas = Transacoes.query.filter(
            Transacoes.usuario_id == usuario_id,
            Transacoes.data_transacao >= data_inicio_busca,
            Transacoes.data_transacao <= data_fim_busca,
            Transacoes.parcela_atual != 0
        ).order_by(Transacoes.data_transacao.desc()).all()

        transacoes_agrupadas = agrupar_transacoes_por_mes(transacoes_filtradas)
        
        total_receita = db.session.query(
            db.func.sum(Transacoes.valor)
        ).filter(
            Transacoes.tipo == "Receita",
            Transacoes.usuario_id == usuario_id,
            Transacoes.data_transacao >= data_inicio_busca,
            Transacoes.data_transacao <= data_fim_busca,
            Transacoes.parcela_atual != 0
        ).scalar() or 0

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
                                categorias = categorias)

# -------------------------------------
# Cadastro de Transação
# -------------------------------------
@transacao_bp.route('/cadastrar', methods=['POST'])
@login_required
def cadastrarTransacao():
    try:
        usuario = current_user.id
        hoje = datetime.now().date()
        
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
        
        num_parcelas = int(num_parcelas_str) if num_parcelas_str and num_parcelas_str.isdigit() and int(num_parcelas_str) > 1 else 1
        parcelado = num_parcelas > 1
        
        valor_total_cheio = valor_parcela * num_parcelas
        valor_registro = valor_parcela
        
        if parcelado:
            valor_a_compensar_imediato = valor_total_cheio if tipo == 'Despesa' and cartao_id else valor_registro
        else:
            valor_a_compensar_imediato = valor_registro
            valor_total_cheio = valor_registro
        
        transacoes_a_salvar = []
        nova_transacao = None

        
        if parcelado:
            
            transacao_mestra = Transacoes(
                usuario_id=usuario,
                conta_id=conta_id,
                cartao_id=cartao_id if cartao_id else None,
                categoria_id=categoria_id,
                tipo=tipo,
                descricao=descricao + f" (Mestra - {num_parcelas}x)",
                valor=valor_total_cheio,
                data_transacao=data_transacao,
                parcelado=True,
                parcelas_total=num_parcelas,
                parcela_atual=0,
                recorrencia='Sem recorrencia' 
            )
            db.session.add(transacao_mestra)
            db.session.commit() 
            
            for i in range(1, num_parcelas + 1):
                data_parcela = data_transacao + relativedelta(months=i-1)
                
                nova_parcela = Transacoes(
                    usuario_id=usuario,
                    conta_id=conta_id,
                    cartao_id=cartao_id if cartao_id else None,
                    categoria_id=categoria_id,
                    tipo=tipo,
                    descricao=descricao + f" ({i}/{num_parcelas})",
                    valor=valor_registro,
                    data_transacao=data_parcela,
                    parcelado=True,
                    parcelas_total=num_parcelas,
                    parcela_atual=i,
                    id_original=transacao_mestra.id,
                    recorrencia='Mensal' 
                )
                transacoes_a_salvar.append(nova_parcela)
            
            db.session.add_all(transacoes_a_salvar)
            nova_transacao = transacoes_a_salvar[0] 

        else:
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

        
        #1. Despesa com Cartão
        if tipo == 'Despesa' and nova_transacao.cartao_id:
            cartao_associado = Cartoes.query.filter_by(id=nova_transacao.cartao_id, usuario_id=usuario).first()
            if cartao_associado:
                cartao_associado.limite_disponivel -= valor_a_compensar_imediato
                db.session.add(cartao_associado)

        #2. Despesa com Conta
        elif tipo == 'Despesa' and not nova_transacao.cartao_id:
            conta_associada = Contas.query.filter_by(id=nova_transacao.conta_id, usuario_id=usuario).first()
            # Compensa apenas se a transação for de hoje ou passada
            if conta_associada and nova_transacao.data_transacao <= hoje: 
                conta_associada.saldo_inicial -= valor_a_compensar_imediato
                db.session.add(conta_associada)
        
        #3. Receita com Conta (DATAS RETROATIVAS)
        elif tipo == 'Receita':
            conta_associada = Contas.query.filter_by(id=nova_transacao.conta_id, usuario_id=usuario).first()

            if conta_associada and nova_transacao.data_transacao <= hoje: 
                conta_associada.saldo_inicial += valor_a_compensar_imediato
                db.session.add(conta_associada)
        
        if not parcelado and nova_transacao.recorrente:
            db.session.flush() 
            nova_transacao.id_original = nova_transacao.id 
            db.session.commit() 
            
            ocorrencias_geradas = gerar_proximas_transacoes_recorrentes(nova_transacao, db, Transacoes)
            flash(f'Transação cadastrada com sucesso! ({ocorrencias_geradas} ocorrências recorrentes geradas.)', 'success')
        
        else:
            db.session.commit()
            
            if parcelado:
                valor_parcela_fmt = formatar_currency(valor_registro)
                valor_total_fmt = formatar_currency(valor_total_cheio)
                
                flash(f'Transação parcelada cadastrada com sucesso! ({num_parcelas} parcelas de {valor_parcela_fmt}, totalizando {valor_total_fmt}.)', 'success')
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

        if tipo == 'Receita':
            
            receita = Transacoes.query.filter(
                Transacoes.id == transacao_id_form,
                Transacoes.tipo == 'Receita',
                Transacoes.usuario_id == usuario_id
            ).first()

            if not receita:
                flash('Receita não encontrada', 'danger')
                return redirect(url_for('transacao.acessarTransacao'))

            valor_antigo = receita.valor
            conta_id_antiga = receita.conta_id
            data_antiga = receita.data_transacao 
            
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

            
            # Compensação Antiga
            conta_antiga = Contas.query.filter_by(id=conta_id_antiga, usuario_id=usuario_id).first()
            if conta_antiga and data_antiga <= hoje: 
                conta_antiga.saldo_inicial -= valor_antigo 
                db.session.add(conta_antiga)

            # Aplicação Nova 
            conta_nova = Contas.query.filter_by(id=receita.conta_id, usuario_id=usuario_id).first()
            if conta_nova and receita.data_transacao <= hoje: 
                conta_nova.saldo_inicial += receita.valor 
                db.session.add(conta_nova)

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

            valor_antigo            = despesa.valor
            cartao_id_antigo        = despesa.cartao_id
            conta_id_antiga         = despesa.conta_id
            data_antiga             = despesa.data_transacao 

            data_str                = request.form.get('data_transacao')
            nova_data               = datetime.strptime(data_str, "%Y-%m-%d").date() if data_str else despesa.data_transacao
            novo_valor              = limpar_currency(request.form.get('valor_transacao'))
            novo_cartao_id          = request.form.get('cartao')
            novo_conta_id           = request.form.get('conta_transacao')
            
            novo_cartao_id          = novo_cartao_id if novo_cartao_id else None
            nova_recorrencia_str    = request.form.get('recorrencia') or despesa.recorrencia

            # --- 2. ATUALIZA A MESTRA ---
            despesa.conta_id          = novo_conta_id or despesa.conta_id
            despesa.cartao_id         = novo_cartao_id 
            despesa.categoria_id      = request.form.get('categoria_transacao') or despesa.categoria_id
            despesa.descricao         = request.form.get('descricao') or despesa.descricao
            despesa.valor             = novo_valor or despesa.valor
            despesa.data_transacao    = nova_data
            despesa.recorrencia       = nova_recorrencia_str
            despesa.recorrente        = nova_recorrencia_str != 'Sem recorrencia'
            transacao_editada         = despesa
    
            
            #Se o pagamento ANTIGO era CARTÃO: Devolve o limite
            if cartao_id_antigo:
                cartao_antigo = Cartoes.query.filter_by(id=cartao_id_antigo, usuario_id=usuario_id).first()
                if cartao_antigo:
                    cartao_antigo.limite_disponivel += valor_antigo
                    db.session.add(cartao_antigo)
            
            #Se o pagamento ANTIGO era CONTA: Restaura o saldo (usa a DATA ANTIGA)
            elif conta_id_antiga: 
                conta_antiga = Contas.query.filter_by(id=conta_id_antiga, usuario_id=usuario_id).first()
                if conta_antiga and data_antiga <= hoje: 
                    conta_antiga.saldo_inicial += valor_antigo 
                    db.session.add(conta_antiga)


            #Se o pagamento NOVO é CARTÃO: Subtrai o novo limite
            if despesa.cartao_id:
                cartao_novo = Cartoes.query.filter_by(id=despesa.cartao_id, usuario_id=usuario_id).first()
                if cartao_novo:
                    cartao_novo.limite_disponivel -= despesa.valor 
                    db.session.add(cartao_novo)

            #Se o pagamento NOVO é CONTA: Subtrai o novo saldo
            elif despesa.cartao_id is None and despesa.conta_id:
                conta_nova = Contas.query.filter_by(id=despesa.conta_id, usuario_id=usuario_id).first()
                if conta_nova and despesa.data_transacao <= hoje: 
                    conta_nova.saldo_inicial -= despesa.valor
                    db.session.add(conta_nova)



        if transacao_editada and not transacao_editada.parcelado:
            is_mestra = transacao_editada.id_original == transacao_editada.id or transacao_editada.id_original is None

            if is_mestra:
                if transacao_editada.recorrente:
                    if transacao_editada.id_original is None:
                        transacao_editada.id_original = transacao_editada.id
                    
                    Transacoes.query.filter(
                        Transacoes.id_original == transacao_editada.id_original,
                        Transacoes.id != transacao_editada.id,
                        Transacoes.data_transacao > hoje,
                        Transacoes.usuario_id == usuario_id
                    ).delete(synchronize_session=False)

                    db.session.add(transacao_editada)
                    db.session.flush()
                    
                    ocorrencias_geradas = gerar_proximas_transacoes_recorrentes(transacao_editada, db, Transacoes)
                    
                    db.session.commit()
                    flash(f'{tipo} mestra atualizada. {ocorrencias_geradas} ocorrências futuras/passadas regeradas!', 'success')
                    
                else:
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
                db.session.commit()
                flash(f'{tipo} individual atualizada com sucesso', 'success')
        
        else:
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
        
        
        if not transacao.parcelado and not transacao.recorrente:
            
            #Estorno de Limite do Cartão (Despesa)
            if transacao.tipo == 'Despesa' and transacao.cartao_id:
                cartao = Cartoes.query.filter_by(id=transacao.cartao_id, usuario_id=usuario_id).first()
                if cartao:
                    cartao.limite_disponivel += transacao.valor 
                    db.session.add(cartao)

            #Estorno de Saldo da Conta (Despesa)
            elif transacao.tipo == 'Despesa' and not transacao.cartao_id:
                conta = Contas.query.filter_by(id=transacao.conta_id, usuario_id=usuario_id).first()
                if conta and transacao.data_transacao <= hoje:
                    conta.saldo_inicial += transacao.valor
                    db.session.add(conta)
            
            #Estorno de Saldo da Conta (Receita)
            elif transacao.tipo == 'Receita':
                conta = Contas.query.filter_by(id=transacao.conta_id, usuario_id=usuario_id).first()
                if conta and transacao.data_transacao <= hoje:
                    conta.saldo_inicial -= transacao.valor
                    db.session.add(conta)
            
            # Deleção da transação simples
            db.session.delete(transacao)
            db.session.commit()
            flash('Transação excluída com sucesso', 'success')
            return redirect(url_for('transacao.acessarTransacao'))


        id_mestra = transacao.id_original if transacao.id_original else transacao.id
        mestra = Transacoes.query.filter_by(id=id_mestra, usuario_id=usuario_id).first()
        
        if mestra:
            if mestra.tipo == 'Despesa' and mestra.cartao_id:
                cartao = Cartoes.query.filter_by(id=mestra.cartao_id, usuario_id=usuario_id).first()
                if cartao:
                    cartao.limite_disponivel += mestra.valor 
                    db.session.add(cartao)
                    

            if mestra.conta_id:
                deve_estornar_saldo = (mestra.tipo == 'Receita') or (mestra.tipo == 'Despesa' and not mestra.cartao_id)
                if deve_estornar_saldo:
                    conta = Contas.query.filter_by(id=mestra.conta_id, usuario_id=usuario_id).first()
                    if conta:
                        transacoes_da_serie_realizadas = Transacoes.query.filter(
                            (Transacoes.id_original == id_mestra) | (Transacoes.id == id_mestra),
                            Transacoes.usuario_id == usuario_id,
                            Transacoes.data_transacao <= hoje, 
                            Transacoes.parcela_atual != 0
                        ).all()
                        
                        valor_total_estorno_saldo = sum(t.valor for t in transacoes_da_serie_realizadas)
                        
                        if valor_total_estorno_saldo > 0:
                            if mestra.tipo == 'Despesa':
                                conta.saldo_inicial += valor_total_estorno_saldo
                            elif mestra.tipo == 'Receita':
                                conta.saldo_inicial -= valor_total_estorno_saldo
                            db.session.add(conta)
            
            is_parcelado = mestra.parcelado
            
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