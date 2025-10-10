from flask import Blueprint, render_template, request
from app.models import Contas

conta_bp = Blueprint('conta', __name__, url_prefix='/conta')

@conta_bp.route('/contas', methods=['GET'])
def contas():
    if request.method == 'GET':
        return render_template('dashboard/despeRecei.html')

@conta_bp.route('/cadastrar', methods=['GET', 'POST'])
def cadastrarConta():
    try:
        # Buscar dados 
        new_conta = Contas(
            
        )
        return 0 
    except Exception as e:
        return 0 