from flask_login import UserMixin
from app.extensions import db

# Tabela de Usuários
class Usuarios(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id                  = db.Column(db.Integer, primary_key=True) 
    nome_completo       = db.Column(db.String(200), nullable=False)
    email               = db.Column(db.String(150), nullable=False, unique=True)
    password_hash       = db.Column(db.String(256), nullable=False)
    criado_em           = db.Column(db.DateTime, default=db.func.current_timestamp())
    atualizado_em       = db.Column(db.DateTime, default=db.func.current_timestamp())


# Tabela de contas
class Contas(db.Model):
    __tablename__ = "contas"

    id                  = db.Column(db.Integer, primary_key=True)
    usuario_id          = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    instituicao         = db.Column(db.String, nullable=False)
    tipo_conta          = db.Column(db.String, nullable=False)
    saldo_inicial       = db.Column(db.Float, default=0)
    criado_em           = db.Column(db.DateTime, default=db.func.current_timestamp())

# Tabela de categorias
class Categorias(db.Model):
    __tablename__ = "categorias"

    id                  = db.Column(db.Integer, primary_key=True)
    usuario_id          = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)  
    nome                = db.Column(db.String, nullable=False)
    tipo                = db.Column(db.String, nullable=False)
    criado_em           = db.Column(db.DateTime, default=db.func.current_timestamp())

# Tabela de transacoes
class Transacoes(db.Model):
    __tablename__ = "transacoes"

    id                  = db.Column(db.Integer, primary_key=True)
    usuario_id          = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)  
    conta_id            = db.Column(db.Integer, db.ForeignKey("contas.id", ondelete="CASCADE"), nullable=False)
    categoria_id        = db.Column(db.Integer, db.ForeignKey("categorias.id", ondelete="CASCADE"), nullable=False)
    tipo                = db.Column(db.String, nullable=False)
    descricao           = db.Column(db.Text)
    valor               = db.Column(db.Float, nullable=False)
    data_transacao      = db.Column(db.DateTime, nullable=False)
    recorrencia         = db.Column(db.String)
    criado_em           = db.Column(db.DateTime, default=db.func.current_timestamp())

# Tabela de extratos
class Extratos(db.Model):
    __tablename__ = "extratos"

    id                  = db.Column(db.Integer, primary_key=True)
    usuario_id          = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)  
    nome_arquivo        = db.Column(db.String, nullable=False)
    importado_em        = db.Column(db.DateTime, default=db.func.current_timestamp())
    status              = db.Column(db.String)

# Tabela de Projecoes
class Projecoes(db.Model):
    __tablename__ = "projecoes"

    id                  = db.Column(db.Integer, primary_key=True)
    usuario_id          = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    data_inicio         = db.Column(db.DateTime, nullable=False)
    data_final          = db.Column(db.DateTime, nullable=False)
    criado_em           = db.Column(db.DateTime, default=db.func.current_timestamp())

# Tabela de KeyValidation 
class KeyValidation(db.Model):
    __tablename__ = "keyvalidation"

    id                  = db.Column(db.Integer, primary_key=True)
    usuario_id          = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    Key                 = db.Column(db.Integer, nullable=False)