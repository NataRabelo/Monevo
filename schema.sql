"""
==================================================
    MODELO DE BANCO DE DADOS - SISTEMA MONEVO
==================================================
Autor: Natã Rabelo e Natã Santa Fé
Descrição:
    Definição das tabelas do banco de dados 
    utilizando SQLAlchemy + Flask.
Banco Suportado: PostgreSQL / MySQL
==================================================
"""

-- ========================================
-- Tabela de Usuários
-- ========================================
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    sobrenome VARCHAR(200) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    celular VARCHAR(50),
    cpf VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- Tabela de Contas
-- ========================================
CREATE TABLE contas (
    id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL,
    nome_conta VARCHAR(255),
    instituicao VARCHAR(255) NOT NULL,
    tipo_conta VARCHAR(100) NOT NULL,
    saldo_inicial DECIMAL(15,2) DEFAULT 0,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- ========================================
-- Tabela de Saldo Inicial
-- ========================================
CREATE TABLE saldo_inicial (
    id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL,
    conta_id INT NOT NULL,
    saldo_inicial DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    mes_ano DATE NOT NULL,

    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (conta_id) REFERENCES contas(id) ON DELETE CASCADE,

    CONSTRAINT conta_mes_un UNIQUE (conta_id, mes_ano)
);

-- ========================================
-- Tabela de Categorias
-- ========================================
CREATE TABLE categorias (
    id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL,
    nome VARCHAR(255) NOT NULL,
    tipo VARCHAR(100),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- ========================================
-- Tabela de Cartões
-- ========================================
CREATE TABLE cartoes (
    id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL,
    nome_cartao VARCHAR(100) NOT NULL,
    bandeira VARCHAR(50),
    limite DECIMAL(15,2) DEFAULT 0,
    limite_disponivel DECIMAL(15,2) DEFAULT 0,
    dia_fechamento_fatura INT NOT NULL,
    dia_vencimento_fatura INT NOT NULL,
    conta_id INT NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (conta_id) REFERENCES contas(id) ON DELETE CASCADE
);

-- ========================================
-- Tabela de Transações
-- ========================================
CREATE TABLE transacoes (
    id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL,
    conta_id INT,
    cartao_id INT,
    categoria_id INT,

    tipo VARCHAR(50) NOT NULL,
    descricao TEXT,
    valor DECIMAL(15,2) NOT NULL,
    data_transacao DATE NOT NULL,
    recorrencia VARCHAR(100),

    parcelas_total INT DEFAULT 1,
    parcela_atual INT DEFAULT 1,
    parcelado BOOLEAN DEFAULT FALSE,

    id_original INT,
    recorrente BOOLEAN DEFAULT FALSE,

    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (conta_id) REFERENCES contas(id) ON DELETE CASCADE,
    FOREIGN KEY (cartao_id) REFERENCES cartoes(id) ON DELETE CASCADE,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL,
    FOREIGN KEY (id_original) REFERENCES transacoes(id) ON DELETE SET NULL
);

-- ========================================
-- Tabela de Extratos
-- ========================================
CREATE TABLE extratos (
    id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL,
    nome_arquivo VARCHAR(255) NOT NULL,
    importado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50),

    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- ========================================
-- Tabela de Projeções
-- ========================================
CREATE TABLE projecoes (
    id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL,
    data_inicio TIMESTAMP NOT NULL,
    data_final TIMESTAMP NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- ========================================
-- Tabela de KeyValidation
-- ========================================
CREATE TABLE keyvalidation (
    id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL,
    key_value VARCHAR(100) NOT NULL,

    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);
