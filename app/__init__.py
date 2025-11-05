# -*- coding: utf-8 -*-
import os
import logging
from flask import Flask
from flask.cli import load_dotenv
from logging.handlers import RotatingFileHandler
from config import DevelopmentConfig, ProductionConfig
from app.extensions import db, bcrypt, migrate, login_manager, mail

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

def configure_logging(app):

    if app.config.get("LOG_TO_STDOUT"):
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
    else:
        # Cria o diretório de logs se não existir
        if not os.path.exists("logs"):
            os.mkdir("logs")
        
        # Configura o handler de arquivo rotativo
        file_handler = RotatingFileHandler(
            "logs/servidor.log", maxBytes=5 * 1024 * 1024, backupCount=3
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info("Aplicativo Flask iniciado")

def create_app(config_class=None):
    if config_class is None:
        env = os.getenv("FLASK_ENV", "development")
        if env == "production":
            config_class = ProductionConfig
        else:
            config_class = DevelopmentConfig

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Cria o diretório de instância se não existir
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Define o caminho do banco de dados
    if app.config["DEBUG"]:
        db_path = os.path.join(app.instance_path, "development.db")
    else:
        db_path = os.path.join(app.instance_path, "production.db")

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

    # Inicializa as extensões com o aplicativo
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Configurações do servidor SMTP (exemplo Gmail)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = os.getenv("EMAIL_REMETENTE")
    app.config['MAIL_PASSWORD'] = os.getenv("EMAIL_SENHA_APP")
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv("EMAIL_REMETENTE")

    mail.init_app(app)

    # Configurações do login_manager
    login_manager.login_view = "main.index"
    login_manager.login_message_category = "info"

    # Configura o logging
    configure_logging(app)

    # Importa os models para evitar import circular
    from . import models
    from .models import Usuarios  # Supondo que seu modelo de usuário se chama User

    # Função para carregar o usuário logado
    @login_manager.user_loader
    def load_user(user_id):
        # Busca o usuário no banco de dados
        return Usuarios.query.get(int(user_id))

    # Registra os blueprints
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    from app.routes.usuarios import user_bp
    app.register_blueprint(user_bp)

    from app.routes.contas import conta_bp
    app.register_blueprint(conta_bp)

    from app.routes.autenticador import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.cartoes import cartao_bp
    app.register_blueprint(cartao_bp)

    from app.routes.categorias import categoria_bp
    app.register_blueprint(categoria_bp)

    from app.routes.transacoes import transacao_bp
    app.register_blueprint(transacao_bp)

    return app
