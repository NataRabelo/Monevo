from flask import Blueprint, current_app, render_template, request, flash, redirect, url_for
from app.models import Contas, Cartoes
from flask_login import current_user
from app import db

transacao_bp = Blueprint('transacao', __name__, url_prefix='/transacao')

@transacao_bp.route('/', methods=['GET', 'POST'])
def acessarTransacao():
    if request.method == "GET":
        return render_template('dashboard/transacao.html')