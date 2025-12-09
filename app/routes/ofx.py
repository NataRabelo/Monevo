from flask import Blueprint, request, redirect, flash, url_for
from flask_login import current_user, login_required
from app.extensions import db
from app.models import Transacoes, Contas, Categorias
from datetime import datetime
import ofxparse
import io
import re

# Definição do Blueprint
ofx_bp = Blueprint("ofx", __name__, url_prefix="/ofx")


# -------------------------
# Função para limpar e padronizar descrições - PIX
# -------------------------
def normalize_descricao(desc: str) -> str:
    if not desc:
        return "Pix"

    original = desc.lower()

    patterns_remove = [
        r"transfer[eê]ncia recebida pelo pix",
        r"transfer[eê]ncia enviada pelo pix",
        r"transfer[eê]ncia recebida via pix",
        r"transfer[eê]ncia enviada via pix",
        r"transfer[eê]ncia via pix",
        r"Transferência Recebida",
        r"pagamento efetuado via pix",
        r"pagamento realizado via pix",
        r"pix recebido",
        r"pix enviado",
    ]

    for p in patterns_remove:
        if re.search(p, original, flags=re.IGNORECASE):
            original = re.sub(p, "", original, flags=re.IGNORECASE).strip()
            original = f"Pix {original}".strip()
            return original.title()

    # Adicionando tratamento para descrições de parcelamento comuns em cartão
    if "parcela" in original and re.search(r"\d+/\d+", original):
        # Ex: "Cakto Pay Lt*Compra - Parcela 1/9" -> "Cakto Pay Lt (1/9)"
        match = re.search(r"-\s*parcela\s*(\d+/\d+)", original, flags=re.IGNORECASE)
        if match:
            original = re.sub(r"-\s*parcela\s*(\d+/\d+)", f"({match.group(1)})", original, flags=re.IGNORECASE).strip()
        
    return original.strip().title()


# -------------------------
# Função auxiliar para ler OFX e identificar o tipo (Conta ou Cartão)
# -------------------------
def parse_ofx(file):
    try:
        file_bytes = file.read()
        ofx_obj = ofxparse.OfxParser.parse(io.BytesIO(file_bytes))
        
        transacoes = []
        is_credit_card = False

        # Verifica se é extrato de Conta Bancária (Statement)
        if ofx_obj.account.statement and ofx_obj.account.statement.transactions:
            transacoes = ofx_obj.account.statement.transactions
            
        # Verifica se é extrato de Cartão de Crédito (Credit Card Statement)
        elif hasattr(ofx_obj.account, 'ccstatement') and ofx_obj.account.ccstatement.transactions:
            transacoes = ofx_obj.account.ccstatement.transactions
            is_credit_card = True
        
        return transacoes, is_credit_card

    except Exception as e:
        print("Erro ao ler OFX:", e)
        return None, None


# -------------------------
# Rota para importar OFX (Adaptada)
# -------------------------
@ofx_bp.route("/importar", methods=["POST"])
@login_required
def importar_ofx():
    arquivo = request.files.get("arquivo_ofx")
    
    # -------------------------------------
    # NOVOS PARÂMETROS DO FORMULÁRIO (Modal)
    # Recebe os IDs da conta e do cartão selecionados no frontend
    # -------------------------------------
    conta_debito_id = request.form.get("conta_debito_id", type=int)
    cartao_credito_id = request.form.get("cartao_credito_id", type=int)

    # -------------------------------------
    # Verificações iniciais
    # -------------------------------------
    if not arquivo:
        flash("Nenhum arquivo selecionado!", "error")
        return redirect(url_for("transacao.acessarTransacao"))

    transacoes_ofx, is_credit_card = parse_ofx(arquivo)

    if not transacoes_ofx:
        flash("Arquivo OFX inválido ou corrompido!", "error")
        return redirect(url_for("transacao.acessarTransacao"))

    # Define qual conta será usada com base no tipo de OFX
    if is_credit_card:
        conta_associada = Contas.query.filter_by(usuario_id=current_user.id, id=cartao_credito_id).first()
        if not conta_associada:
            flash("Selecione um Cartão de Crédito válido para este arquivo OFX!", "error")
            return redirect(url_for("transacao.acessarTransacao"))
    else:
        conta_associada = Contas.query.filter_by(usuario_id=current_user.id, id=conta_debito_id).first()
        if not conta_associada:
            flash("Selecione uma Conta (Débito/Pix) válida para este arquivo OFX!", "error")
            return redirect(url_for("transacao.acessarTransacao"))

    # -------------------------------------
    # Processamento das transações
    # -------------------------------------
    categoria_padrao = Categorias.query.filter_by(
        usuario_id=current_user.id, nome="Importado OFX"
    ).first()

    if not categoria_padrao:
        categoria_padrao = Categorias(
            usuario_id=current_user.id,
            nome="Importado OFX",
            tipo="Despesa"
        )
        db.session.add(categoria_padrao)
        # Não commitamos ainda, pois faremos o commit no final

    count = 0

    for t in transacoes_ofx:
        valor = float(t.amount)
        descricao = normalize_descricao(t.memo or "")
        data_transacao = t.date.date()
        
        # Lógica para definir o TIPO e VALOR:
        
        # 1. Se for Cartão de Crédito (is_credit_card == True):
        if is_credit_card:
            # Despesas no Cartão (Débito no OFX = Negativo) são registradas como Despesa no seu sistema.
            # Pagamentos de Fatura (Crédito no OFX = Positivo) são registradas como Receita no Cartão.
            if valor < 0:
                tipo = "Despesa"
            elif valor > 0:
                # É um pagamento de fatura, que "compensa" as despesas do cartão.
                # No seu sistema financeiro, isso é uma entrada/receita na conta do Cartão.
                tipo = "Receita" 
            else:
                continue # Transação de valor zero

        # 2. Se for Conta Bancária (Débito/Pix):
        else:
            # Receita (Positivo no OFX)
            if valor > 0:
                tipo = "Receita"
            # Despesa (Negativo no OFX)
            elif valor < 0:
                tipo = "Despesa"
            else:
                continue # Transação de valor zero

        # A Conta/Cartão para o registro já foi definida fora do loop (conta_associada)
        
        # Verifica duplicidade
        existe = Transacoes.query.filter_by(
            usuario_id=current_user.id,
            conta_id=conta_associada.id,
            valor=abs(valor),
            descricao=descricao,
            data_transacao=data_transacao
        ).first()

        if existe:
            continue

        # Cria nova transação
        nova_transacao = Transacoes(
            usuario_id=current_user.id,
            conta_id=conta_associada.id, # Usa a conta ou cartão correto
            categoria_id=categoria_padrao.id,
            tipo=tipo,
            descricao=descricao,
            valor=abs(valor), # Sempre armazena o valor absoluto
            data_transacao=data_transacao,
            recorrencia="Sem recorrencia",
        )

        db.session.add(nova_transacao)
        count += 1

    db.session.commit()

    flash(f"{count} transações importadas com sucesso na conta/cartão: {conta_associada.nome_conta}!", "success")
    return redirect(url_for("transacao.acessarTransacao"))