from flask import Blueprint, request, redirect, flash, url_for
from flask_login import current_user, login_required
from app.extensions import db
from app.models import Transacoes, Contas, Categorias
from datetime import datetime
import ofxparse
import io
import re


# -------------------------------------
# Blueprint para importação de OFX
# -------------------------------------
ofx_bp = Blueprint("ofx", __name__, url_prefix="/ofx")


# -------------------------
# Função para limpar e padronizar descrições APENAS DE PIX
# -------------------------
def normalize_descricao(desc: str) -> str:
    if not desc:
        return "Pix"

    original = desc.lower()

    # Remove SOMENTE descrições padrão que realmente são PIX
    patterns_remove = [
        r"transfer[eê]ncia recebida pelo pix",
        r"transfer[eê]ncia enviada pelo pix",
        r"transfer[eê]ncia recebida via pix",
        r"transfer[eê]ncia enviada via pix",
        r"transfer[eê]ncia via pix",
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

    # ❗ Se não for PIX → mantém totalmente original
    return desc.strip().title()


# -------------------------
# Função auxiliar para ler OFX
# -------------------------
def parse_ofx(file):
    try:
        file_bytes = file.read()

        # Envia os bytes direto para o parser
        ofx_obj = ofxparse.OfxParser.parse(io.BytesIO(file_bytes))

        return ofx_obj.account.statement.transactions

    except Exception as e:
        print("Erro ao ler OFX:", e)
        return None


# -------------------------
# Rota: IMPORTAR OFX
# -------------------------
@ofx_bp.route("/importar", methods=["POST"])
@login_required
def importar_ofx():
    arquivo = request.files.get("arquivo_ofx")

    if not arquivo:
        flash("Nenhum arquivo selecionado!", "warning")
        return redirect(url_for("transacao.acessarTransacao"))

    # Parse do OFX
    transacoes_ofx = parse_ofx(arquivo)

    if not transacoes_ofx:
        flash("Arquivo OFX inválido ou corrompido!", "danger")
        return redirect(url_for("transacao.acessarTransacao"))

    # Conta padrão
    conta = Contas.query.filter_by(usuario_id=current_user.id).first()
    if not conta:
        flash("Cadastre uma conta antes de importar OFX!", "warning")
        return redirect(url_for("transacao.acessarTransacao"))

    # Categoria padrão: "Importado OFX"
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
        db.session.commit()

    count = 0  # contador de transações importadas

    # Loop nas transações do arquivo OFX
    for t in transacoes_ofx:
        valor = float(t.amount)
        tipo = "Receita" if valor > 0 else "Despesa"

        # Normalização da descrição (apenas PIX é alterado)
        descricao = normalize_descricao(t.memo or "")

        data_transacao = t.date.date()

        # Evitar duplicação
        existe = Transacoes.query.filter_by(
            usuario_id=current_user.id,
            conta_id=conta.id,
            valor=abs(valor),
            descricao=descricao,
            data_transacao=data_transacao
        ).first()

        if existe:
            continue

        # Criando a transação
        nova_transacao = Transacoes(
            usuario_id=current_user.id,
            conta_id=conta.id,
            categoria_id=categoria_padrao.id,
            tipo=tipo,
            descricao=descricao,
            valor=abs(valor),
            data_transacao=data_transacao,
            recorrencia="Sem recorrencia",
        )

        db.session.add(nova_transacao)
        count += 1

    db.session.commit()

    flash(f"{count} transações importadas com sucesso!", "success")
    return redirect(url_for("transacao.acessarTransacao"))
