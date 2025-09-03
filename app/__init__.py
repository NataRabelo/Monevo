import os 
from flask import Flask
from flask.cli import load_dotenv
from config import DevelopmentConfig, ProductionConfig
from app.extensions import db, bcrypt, migrate, login_manager


load_dotenv()

def create_app(config_class = None):
    if config_class is None:
        env = os.getenv("FLASK_ENV", "development")
        if env == "production":
            config_class = ProductionConfig
        else:
            config_class = DevelopmentConfig
    
    app = Flask(__name__)
    app.config.from_object(config_class)

    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    if app.config["DEBUG"]:
        db_path = os.path.join(app.instance_path, "development.db")
    else:
        db_path = os.path.join(app.instance_path, "production.db")

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    from . import models

    login_manager.init_app(app)
    login_manager.login_view = 'main.index'
    login_manager.login_mensagem_category = 'info'
    
    #Inicialização do blueprints
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    return app