from flask import Blueprint, request, jsonify
from ofxparse import OfxParser
import io

ofx_bp = Blueprint('ofx', __name__)

@ofx_bp.route('/importar-ofx', methods=['POST'])
def importar_ofx():
    try:
        # 1. Verifica se o arquivo veio na requisição
        if 'arquivo' not in request.files:
            return jsonify({"erro": "Nenhum arquivo enviado"}), 400

        arquivo = request.files['arquivo']

        # 2. Convertemos para bytes e lemos com OFXParser
        ofx_data = arquivo.read()
        ofx = OfxParser.parse(io.BytesIO(ofx_data))

        transacoes = ofx.bank_accounts[0].statement.transactions

        receitas = []
        despesas = []

        # 3. Converte cada transação em receita/despesa
        for t in transacoes:
            item = {
                "data": t.date.strftime("%Y-%m-%d"),
                "descricao": t.memo,
                "valor": float(t.amount)
            }

            if t.amount > 0:
                receitas.append(item)
            else:
                item["valor"] = abs(item["valor"])  # deixa positivo
                despesas.append(item)

        return jsonify({
            "receitas": receitas,
            "despesas": despesas
        }), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
