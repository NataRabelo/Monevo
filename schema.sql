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
    nome_completo VARCHAR(200) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
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
    instituicao VARCHAR(255) NOT NULL,
    tipo_conta VARCHAR(100) NOT NULL,
    saldo_inicial DECIMAL(15,2) DEFAULT 0,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- ========================================
-- Tabela de Categorias
-- ========================================
CREATE TABLE categorias (
    id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL,
    nome VARCHAR(255) NOT NULL,
    tipo VARCHAR(100) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- ========================================
-- Tabela de Transações
-- ========================================
CREATE TABLE transacoes (
    id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL,
    conta_id INT NOT NULL,
    categoria_id INT NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    descricao TEXT,
    valor DECIMAL(15,2) NOT NULL,
    data_transacao TIMESTAMP NOT NULL,
    recorrencia VARCHAR(100),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (conta_id) REFERENCES contas(id) ON DELETE CASCADE,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE CASCADE
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
