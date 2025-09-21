from flask import Blueprint, render_template, request

conta_bp = Blueprint('conta', __name__, url_prefix='/conta')

@conta_bp.route('/contas', methods=['GET'])
def contas():
    if request.method == 'GET':
        return render_template('despeRecei.html')
