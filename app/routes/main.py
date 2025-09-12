from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

# Rota de abertura do sistema 
@main_bp.route('/')
def index():
    return "Teste de funcionamento Monevo"

# Rota de chamada da tela de login 
@main_bp.route('/login', methods=["GET"])
def login():
    return render_template("login.html")

# Rota de chamada da tela de cadastro de novo usuário
@main_bp.route('/cadastro_usuario', methods=["GET"])
def cadastrar_usuario():
    return render_template("cadastrar_usuario.html")

# Rota de chamada da tela de recuperação de senha
@main_bp.route('/recuperar_senha', methods=['GET'])
def recuperar_senha():
    return render_template('recuperar_senha.html')

# Rota de chamada da tela de nova senha
@main_bp.route('/nova_senha', methods=['GET'])
def nova_senha():
    return render_template('nova_senha.html')

# Rota de chamada da tela inicial do sistema (Menu)
@main_bp.route('/menu', methods=['GET'])
def menu():
    return render_template('menu.html')

#rota de chamada da tela de contas e cartões
@main_bp.route('/contas_e_cartoes', methods=['GET'])
def contas_e_cartoes():
    return render_template('contas_e_cartoes.html')

# Rota de chamada de despesas_e_receitas
@main_bp.route('/despesas_e_receitas', methods=['GET'])
def despesas_e_receitas():
    return render_template("despesas_e_receitas.html")