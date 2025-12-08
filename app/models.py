from flask_login import UserMixin
from app.extensions import db
from sqlalchemy import func

# -----------------------
# Tabela de Usuários
# -----------------------
class Usuarios(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id              = db.Column(db.Integer, primary_key=True)
    nome            = db.Column(db.String(200), nullable=False)
    sobrenome       = db.Column(db.String(200), nullable=False)
    email           = db.Column(db.String(150), nullable=False, unique=True, index=True)
    celular         = db.Column(db.String(50))
    cpf             = db.Column(db.String(50), nullable=False, unique=True)
    password_hash   = db.Column(db.String(256), nullable=False)
    criado_em       = db.Column(db.DateTime, default=func.current_timestamp())
    atualizado_em   = db.Column(db.DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relações
    contas          = db.relationship('Contas', back_populates='usuario', cascade="all, delete-orphan", lazy=True)
    cartoes         = db.relationship('Cartoes', back_populates='usuario', cascade="all, delete-orphan", lazy=True)
    categorias      = db.relationship('Categorias', back_populates='usuario', cascade="all, delete-orphan", lazy=True)
    transacoes      = db.relationship('Transacoes', back_populates='usuario', cascade="all, delete-orphan", lazy=True)
    extratos        = db.relationship('Extratos', back_populates='usuario', cascade="all, delete-orphan", lazy=True)
    projecoes       = db.relationship('Projecoes', back_populates='usuario', cascade="all, delete-orphan", lazy=True)
    key_validations = db.relationship('KeyValidation', back_populates='usuario', cascade="all, delete-orphan", lazy=True)

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"<Usuario {self.id} {self.email}>"


# -----------------------
# Tabela Contas
# -----------------------
class Contas(db.Model):
    __tablename__ = "contas"

    id              = db.Column(db.Integer, primary_key=True)
    usuario_id      = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    nome_conta      = db.Column(db.String, nullable=True)
    instituicao     = db.Column(db.String, nullable=False)
    tipo_conta      = db.Column(db.String, nullable=False)
    saldo_inicial   = db.Column(db.Float, default=0)
    criado_em       = db.Column(db.DateTime, default=func.current_timestamp())

    # Relações
    usuario         = db.relationship('Usuarios', back_populates='contas', lazy=True)
    cartoes         = db.relationship('Cartoes', back_populates='conta', cascade="all, delete-orphan", lazy=True)
    transacoes      = db.relationship('Transacoes', back_populates='conta', lazy=True)

    def __repr__(self):
        return f"<Conta {self.id} {self.nome_conta}>"


# -----------------------
# Tabela de Saldo Inicial
# -----------------------
class SaldoInicial(db.Model):
    __tablename__ = 'saldo_inicial'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    conta_id = db.Column(db.Integer, db.ForeignKey('contas.id'), nullable=False)
    saldo_inicial = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    mes_ano = db.Column(db.Date, nullable=False)

    conta = db.relationship('Contas', backref='saldos_iniciais')

    __table_args__ = (
        db.UniqueConstraint('conta_id', 'mes_ano', name='_conta_mes_uc'),
    )
    
    def __repr__(self):
        return f"<SaldoInicial Conta {self.conta_id} - {self.mes_ano}: R${self.saldo_inicial}>"


# -----------------------
# Tabela de Categorias
# -----------------------
class Categorias(db.Model):
    __tablename__ = "categorias"

    id              = db.Column(db.Integer, primary_key=True)
    usuario_id      = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    nome            = db.Column(db.String, nullable=False)
    tipo            = db.Column(db.String, nullable=True)
    criado_em       = db.Column(db.DateTime, default=func.current_timestamp())

    usuario         = db.relationship('Usuarios', back_populates='categorias', lazy=True)
    transacoes      = db.relationship('Transacoes', back_populates='categoria', lazy=True)

    def __repr__(self):
        return f"<Categoria {self.id} {self.nome} ({self.tipo})>"


# -----------------------
# Tabela de Cartões
# -----------------------
class Cartoes(db.Model):
    __tablename__ = "cartoes"

    id                      = db.Column(db.Integer, primary_key=True)
    usuario_id              = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    nome_cartao             = db.Column(db.String(100), nullable=False)
    bandeira                = db.Column(db.String(50))
    limite                  = db.Column(db.Float, nullable=False, default=0.0)
    limite_disponivel       = db.Column(db.Float, nullable=False, default=0.0)
    dia_fechamento_fatura   = db.Column(db.Integer, nullable=False)
    dia_vencimento_fatura   = db.Column(db.Integer, nullable=False)
    conta_id                = db.Column(db.Integer, db.ForeignKey("contas.id", ondelete="CASCADE"), nullable=False)
    criado_em               = db.Column(db.DateTime, default=func.current_timestamp())

    usuario                 = db.relationship('Usuarios', back_populates='cartoes', lazy=True)
    conta                   = db.relationship('Contas', back_populates='cartoes', lazy=True)
    transacoes              = db.relationship('Transacoes', back_populates='cartao', lazy=True)

    def __repr__(self):
        return f"<Cartao {self.id} {self.nome_cartao}>"


# -----------------------
# Tabela de Transações (CORRIGIDA)
# -----------------------
class Transacoes(db.Model):
    __tablename__ = "transacoes"

    id              = db.Column(db.Integer, primary_key=True)
    usuario_id      = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    conta_id        = db.Column(db.Integer, db.ForeignKey("contas.id", ondelete="CASCADE"), nullable=True)
    cartao_id       = db.Column(db.Integer, db.ForeignKey("cartoes.id", ondelete="CASCADE"), nullable=True)
    categoria_id    = db.Column(db.Integer, db.ForeignKey("categorias.id", ondelete="SET NULL"), nullable=True)
    tipo            = db.Column(db.String, nullable=False)
    descricao       = db.Column(db.Text)
    valor           = db.Column(db.Float, nullable=False)
    data_transacao  = db.Column(db.Date, nullable=False)
    recorrencia     = db.Column(db.String)
    parcelas_total  = db.Column(db.Integer, default=1)
    parcela_atual   = db.Column(db.Integer, default=1)
    parcelado       = db.Column(db.Boolean, default=False)
    id_original     = db.Column(db.Integer, db.ForeignKey("transacoes.id", ondelete="SET NULL"), nullable=True)
    recorrente      = db.Column(db.Boolean, default=False)
    criado_em       = db.Column(db.DateTime, default=func.current_timestamp())

    # Relações normais
    usuario  = db.relationship('Usuarios', back_populates='transacoes', lazy=True)
    conta    = db.relationship('Contas', back_populates='transacoes', lazy=True)
    categoria = db.relationship('Categorias', back_populates='transacoes', lazy=True)
    cartao   = db.relationship('Cartoes', back_populates='transacoes', lazy=True)

    # Relação pai-filho (CORREÇÃO)
    mestra = db.relationship(
        'Transacoes',
        remote_side=[id],
        foreign_keys=[id_original],
        passive_deletes=True
    )

    ocorrencias_geradas = db.relationship(
        'Transacoes',
        foreign_keys=[id_original],
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy='dynamic'
    )

    def __repr__(self):
        return f"<Transacao {self.id} {self.tipo} {self.valor}>"


# -----------------------
# Tabela de Extratos
# -----------------------
class Extratos(db.Model):
    __tablename__ = "extratos"

    id              = db.Column(db.Integer, primary_key=True)
    usuario_id      = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    nome_arquivo    = db.Column(db.String, nullable=False)
    importado_em    = db.Column(db.DateTime, default=func.current_timestamp())
    status          = db.Column(db.String)

    usuario         = db.relationship('Usuarios', back_populates='extratos', lazy=True)

    def __repr__(self):
        return f"<Extrato {self.id} {self.nome_arquivo}>"


# -----------------------
# Tabela de Projeções
# -----------------------
class Projecoes(db.Model):
    __tablename__ = "projecoes"

    id              = db.Column(db.Integer, primary_key=True)
    usuario_id      = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    data_inicio     = db.Column(db.DateTime, nullable=False)
    data_final      = db.Column(db.DateTime, nullable=False)
    criado_em       = db.Column(db.DateTime, default=func.current_timestamp())

    usuario         = db.relationship('Usuarios', back_populates='projecoes', lazy=True)

    def __repr__(self):
        return f"<Projecao {self.id} {self.data_inicio} -> {self.data_final}>"


# -----------------------
# Tabela de KeyValidation
# -----------------------
class KeyValidation(db.Model):
    __tablename__ = "keyvalidation"

    id              = db.Column(db.Integer, primary_key=True)
    usuario_id      = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    key_value       = db.Column(db.String(100), nullable=False)

    usuario         = db.relationship('Usuarios', back_populates='key_validations', lazy=True)

    def __repr__(self):
        return f"<KeyValidation {self.id} user={self.usuario_id}>"
