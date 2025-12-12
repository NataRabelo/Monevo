# 🌐 Monevo — Sistema Inteligente de Gestão Financeira Pessoal

**Monevo** é uma aplicação web de desktop desenvolvida como Trabalho de Conclusão de Curso, oferecendo uma solução completa e intuitiva para **organização, controle e planejamento financeiro pessoal**. O sistema integra funcionalidades avançadas de gestão de contas, cartões de crédito, transações, análise de dados e educação financeira.

## 📋 Informações do Projeto

- **Nome:** Monevo (Money Evolution)
- **Autores:** Natã Rabelo Pires & Natã Santa Fé
- **Tipo:** Aplicação Web para Desktop
- **Linguagem:** Python 3.x
- **Framework:** Flask
- **Banco de Dados:** SQLite
- **Propósito:** TCC - Solução de Gestão Financeira Pessoal

---

## 🚀 Funcionalidades Principais

### 👤 **Módulo de Autenticação e Usuário**
- ✅ Cadastro com validação de CPF e e-mail
- ✅ Login seguro com hash bcrypt
- ✅ Recuperação de senha via e-mail
- ✅ Edição de perfil do usuário
- ✅ Logout seguro

### 💰 **Módulo de Contas Bancárias**
- ✅ Registro de múltiplas contas bancárias
- ✅ Gerenciamento de instituições financeiras
- ✅ Definição de tipos de conta (corrente, poupança, etc.)
- ✅ Saldo inicial e acompanhamento mensal
- ✅ Histórico de contas

### 💳 **Módulo de Cartões de Crédito**
- ✅ Registro de cartões vinculados às contas
- ✅ Gerenciamento de limite de crédito
- ✅ Vencimento de fatura configurável
- ✅ Histórico de transações por cartão
- ✅ Consolidação de débitos

### 📂 **Módulo de Categorias**
- ✅ Criação de categorias personalizadas
- ✅ Classificação de transações
- ✅ Organização por tipo (receita/despesa)
- ✅ Gestão flexível de categorias

### 🧾 **Módulo de Transações**
- ✅ Registro de receitas e despesas
- ✅ Associação a contas e cartões
- ✅ Vinculação com categorias
- ✅ Datas flexíveis e descrições
- ✅ Filtros avançados (período, categoria, tipo)
- ✅ Ordenação e busca
- ✅ Exclusão e edição de transações
- ✅ Suporte a transações recorrentes

### 📥 **Módulo de Importação OFX**
- ✅ Importação de extratos bancários em formato `.ofx`
- ✅ Leitura automática de dados bancários
- ✅ Integração com o sistema de transações
- ✅ Suporte a múltiplas instituições

### 📊 **Módulo de Projeções Financeiras**
- ✅ Simulação de cenários financeiros
- ✅ Projeção de saldo mensal
- ✅ Análise de tendências de gastos
- ✅ Planejamento futuro

### 📈 **Módulo de Relatórios**
- ✅ Resumo mensal de transações
- ✅ Consolidação de saldos
- ✅ Análise por categoria
- ✅ Agrupamento de dados financeiros
- ✅ Exportação de dados

### 🎓 **Módulo Educacional**
- ✅ Glossário de termos financeiros
- ✅ Módulos educativos (3 módulos principais)
- ✅ Conteúdo sobre educação financeira
- ✅ Aprendizado progressivo

### 🛠️ **Módulo de Ferramentas Financeiras**
- ✅ Calculadora de amortização de dívidas
- ✅ Simulador de juros compostos
- ✅ Calculadora de projeção de aposentadoria
- ✅ Calculadora de reserva de emergência

---

## 🛠️ Tecnologias Utilizadas

### Backend
- **Framework:** Flask 3.1.2
  - Flask-Login (autenticação)
  - Flask-SQLAlchemy (ORM)
  - Flask-Migrate (migrações)
  - Flask-Mail (envio de e-mails)
  - Flask-Bcrypt (hash de senha)
  - Blueprints (modularização)

### Banco de Dados
- **SQLite:** Banco de dados relacional
- **SQLAlchemy 2.0:** ORM (Object-Relational Mapping)
- **Alembic:** Sistema de migrações
- **Flask-Migrate:** Gerenciar migrações

### Frontend
- **Jinja2:** Motor de templates
- **HTML5:** Estrutura semântica
- **CSS3:** Estilização responsiva
- **JavaScript:** Interatividade

### Utilitários
- **ofxparse 0.21:** Parsing de arquivos OFX
- **python-dotenv:** Gerenciamento de variáveis de ambiente
- **bcrypt:** Hash seguro de senhas
- **BeautifulSoup4:** Parsing HTML/XML
- **logging:** Sistema de logs com rotação

---

## 📦 Estrutura do Projeto

```
monevo/
├── run.py                    # Entrypoint da aplicação
├── config.py                 # Configurações (desenvolvimento/produção)
├── requirements.txt          # Dependências Python
├── schema.sql                # Estrutura do banco de dados
├── README.md                 # Este arquivo
│
├── app/                      # Pacote principal da aplicação
│   ├── __init__.py          # Inicialização e factory do Flask
│   ├── extensions.py        # Extensões (db, bcrypt, migrate, login_manager, mail)
│   ├── models.py            # Modelos de dados (SQLAlchemy)
│   ├── utils.py             # Funções utilitárias
│   │
│   ├── routes/              # Blueprints de rotas
│   │   ├── autenticador.py  # Rotas de autenticação e login
│   │   ├── usuarios.py      # Rotas de gerenciamento de usuários
│   │   ├── contas.py        # Rotas de contas bancárias
│   │   ├── cartoes.py       # Rotas de cartões de crédito
│   │   ├── categorias.py    # Rotas de categorias
│   │   ├── transacoes.py    # Rotas de transações
│   │   ├── projecoes.py     # Rotas de projeções financeiras
│   │   ├── educacional.py   # Rotas do módulo educacional
│   │   └── main.py          # Rotas principais (home, dashboard)
│   │
│   ├── services/            # Serviços e lógica de negócio
│   │   ├── agrupador.py     # Agrupamento e consolidação de dados
│   │   └── recorrencia_servico.py  # Serviço de transações recorrentes
│   │
│   ├── static/              # Arquivos estáticos
│   │   ├── css/             # Folhas de estilo
│   │   │   ├── base.css             # Estilos globais
│   │   │   ├── login.css            # Estilos de login
│   │   │   ├── cadastro.css         # Estilos de cadastro
│   │   │   ├── menu.css             # Estilos do menu
│   │   │   ├── contas.css           # Estilos de contas
│   │   │   ├── transacao.css        # Estilos de transações
│   │   │   ├── editar.css           # Estilos de edição
│   │   │   ├── projecao.css         # Estilos de projeções
│   │   │   ├── educacional.css      # Estilos educacionais
│   │   │   ├── recuperar.css        # Estilos de recuperação
│   │   │   └── senhaNova.css        # Estilos de nova senha
│   │   ├── js/              # Scripts JavaScript
│   │   │   ├── base.js              # Scripts globais
│   │   │   ├── login.js             # Scripts de login
│   │   │   ├── cadastro.js          # Scripts de cadastro
│   │   │   ├── conta.js             # Scripts de contas
│   │   │   ├── transacao.js         # Scripts de transações
│   │   │   ├── editar.js            # Scripts de edição
│   │   │   └── projecao.js          # Scripts de projeções
│   │   └── img/             # Imagens e assets
│   │
│   └── templates/           # Templates Jinja2
│       ├── base.html        # Template base (herança)
│       ├── Dashboard/       # Templates do dashboard
│       │   ├── contas.html          # Página de contas
│       │   ├── menu.html            # Menu do dashboard
│       │   ├── transacao.html       # Página de transações
│       │   ├── projecao.html        # Página de projeções
│       │   └── educacional.html     # Página educacional
│       ├── usuario/         # Templates de autenticação
│       │   ├── login.html           # Página de login
│       │   ├── cadastro.html        # Página de cadastro
│       │   ├── editar.html          # Página de edição de perfil
│       │   ├── recuperar.html       # Página de recuperação
│       │   └── recuperarSenha.html  # Página de nova senha
│       ├── educacional/     # Templates educacionais
│       │   ├── modulo1.html         # Módulo 1
│       │   ├── modulo2.html         # Módulo 2
│       │   ├── modulo3.html         # Módulo 3
│       │   └── glossario.html       # Glossário financeiro
│       ├── ferramentas/     # Templates de calculadoras
│       │   ├── amortizacao_dividas.html        # Calculadora de dívidas
│       │   ├── juros_compostos.html            # Calculador de juros
│       │   ├── projecao_aposentadoria.html     # Projeção aposentadoria
│       │   └── reserva_emergencia.html         # Reserva de emergência
│       ├── email/           # Templates de e-mail
│       │   └── email_recuperacao.html  # E-mail de recuperação
│       └── partials/        # Templates reutilizáveis
│           ├── navbar.html          # Barra de navegação
│           └── flash_messages.html  # Mensagens flash
│
├── migrations/              # Migrações do banco de dados
│   ├── alembic.ini          # Configuração do Alembic
│   ├── env.py               # Environment do Alembic
│   ├── README               # Instruções de migrações
│   └── versions/            # Histórico de migrações
│       ├── 16c4663e4a96_initial_migrate.py
│       └── 4b7b689d0f5c_adiciona_campo_receita_ja_incluida_a_.py
│
├── logs/                    # Arquivos de log da aplicação
│   └── servidor.log         # Log rotativo
├── instance/                # Dados de instância local
│   ├── development.db       # Banco de dados (desenvolvimento)
│   └── production.db        # Banco de dados (produção)
├── Documentação/            # Documentação do projeto
│   ├── 1 - TAP/             # Termo de Abertura do Projeto
│   ├── 2 - Requisitos/      # Especificações funcionais
│   ├── 3 - Caso de Uso/     # Fluxos de usuário
│   ├── 4 - Prototipação/    # Wireframes e mockups
│   ├── 5 - Fluxograma/      # Diagramas de processo
│   ├── 6 - Teste-manual/    # Casos de teste manual
│   ├── 7 - Manual do usuario/ # Guias de uso
│   └── Logo/                # Identidade visual
│
└── __pycache__/             # Cache Python (ignorar)
```

---

## 🗄️ Modelos de Dados

A aplicação utiliza os seguintes modelos principais no banco de dados:

### **Usuários** (`Usuarios`)
- Identificação única com CPF e e-mail
- Autenticação com senha bcrypt
- Rastreamento de criação e atualização
- Relacionamento com todas as entidades do usuário

### **Contas** (`Contas`)
- Conta bancária com instituição e tipo
- Saldo inicial configurável
- Múltiplas contas por usuário
- Histórico de transações

### **Saldo Inicial** (`SaldoInicial`)
- Rastreamento mensal de saldos
- Associado a conta e período (mês/ano)
- Constraint único por conta/mês

### **Cartões** (`Cartoes`)
- Vinculado a uma conta
- Limite de crédito personalizável
- Data de vencimento da fatura
- Histórico de débitos

### **Categorias** (`Categorias`)
- Personalizadas por usuário
- Tipo de categoria (receita/despesa)
- Reutilizável em múltiplas transações

### **Transações** (`Transacoes`)
- Receita ou despesa
- Vinculada a conta/cartão e categoria
- Data flexível e descrição
- Suporte a recorrência
- Filtros avançados

### **Extratos** (`Extratos`)
- Importação de dados OFX
- Histórico de importações
- Rastreamento de origem

### **Projeções** (`Projecoes`)
- Simulações de cenários
- Análise de tendências
- Planejamento financeiro

---

## 🚀 Guia de Instalação e Execução

### **Requisitos do Sistema**
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Windows PowerShell 5.1+
- Conexão com internet (para e-mails)

### **Passo 1: Clonar o Repositório**

```powershell
git clone https://github.com/NataRabelo/Monevo.git
cd Monevo
```

### **Passo 2: Criar Ambiente Virtual**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

> **Nota:** Se receber erro de permissão, execute PowerShell como Administrador

### **Passo 3: Instalar Dependências**

```powershell
pip install -r requirements.txt
```

### **Passo 4: Configurar Variáveis de Ambiente**

Crie um arquivo `.env` na raiz do projeto:

```env
# Configurações Flask
FLASK_ENV=development
FLASK_APP=run.py
SECRET_KEY=sua-chave-secreta-muito-segura-aqui-min-16-chars

# Configurações de E-mail (opcional, necessário para recuperação de senha)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-de-app
```

### **Passo 5: Inicializar o Banco de Dados**

```powershell
flask db migrate

# Aplicar migrações
flask db upgrade
```

### **Passo 6: Executar a Aplicação**

```powershell
python run.py
```

A aplicação estará disponível em: **http://127.0.0.1:5000/**

---

## 🗄️ Banco de Dados

### **Armazenamento**
- **Localização:** `instance/`
- **Arquivos:**
  - `development.db` (banco de desenvolvimento)
  - `production.db` (banco de produção)

### **Comandos de Migração**

```powershell
# Criar uma nova migração
flask db migrate -m "Descrição da mudança"

# Aplicar todas as migrações pendentes
flask db upgrade

# Reverter para uma versão anterior
flask db downgrade

# Ver histórico de migrações
flask db history
```

### **Estrutura Principal de Tabelas**
- `usuarios` - Dados de autenticação e perfil
- `contas` - Contas bancárias
- `cartoes` - Cartões de crédito
- `categorias` - Categorias de transações
- `transacoes` - Histórico de transações
- `extratos` - Dados importados OFX
- `projecoes` - Cenários financeiros
- `saldo_inicial` - Controle mensal de saldos
- `key_validation` - Validações de recuperação de senha

---

## 📧 Configuração de E-mail

A aplicação utiliza **SMTP** para envio de e-mails (recuperação de senha, notificações).

### **Configuração com Gmail**

1. Ativar autenticação de dois fatores na sua conta Google
2. Gerar [Senha de App](https://myaccount.google.com/apppasswords)
3. Configurar variáveis de ambiente no arquivo `.env`:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-de-app-gerada
```

### **Outros Provedores SMTP**
- **Outlook:** smtp.outlook.com (porta 587)
- **Yahoo:** smtp.mail.yahoo.com (porta 587)
- **Hotmail:** smtp.live.com (porta 587)

---

## 📊 Módulos e Rotas Detalhadas

### **Autenticação** (`routes/autenticador.py`)
```
POST   /login                 - Fazer login
POST   /logout                - Fazer logout
POST   /registro              - Novo cadastro
GET    /recuperar-senha       - Formulário de recuperação
POST   /recuperar-senha       - Enviar e-mail de recuperação
GET    /nova-senha/<token>    - Definir nova senha
```

### **Usuários** (`routes/usuarios.py`)
```
GET    /perfil                - Visualizar perfil
POST   /perfil/editar         - Atualizar dados pessoais
DELETE /perfil                - Excluir conta
```

### **Contas** (`routes/contas.py`)
```
GET    /contas                - Listar contas
GET    /contas/<id>           - Detalhes da conta
POST   /contas/nova           - Criar conta
POST   /contas/<id>/editar    - Editar conta
DELETE /contas/<id>           - Deletar conta
```

### **Cartões** (`routes/cartoes.py`)
```
GET    /cartoes               - Listar cartões
GET    /cartoes/<id>          - Detalhes do cartão
POST   /cartoes/novo          - Adicionar cartão
POST   /cartoes/<id>/editar   - Editar cartão
DELETE /cartoes/<id>          - Deletar cartão
```

### **Categorias** (`routes/categorias.py`)
```
GET    /categorias            - Listar categorias
POST   /categorias/nova       - Criar categoria
POST   /categorias/<id>/editar - Editar categoria
DELETE /categorias/<id>       - Deletar categoria
```

### **Transações** (`routes/transacoes.py`)
```
GET    /transacoes            - Listar com filtros
GET    /transacoes/<id>       - Detalhes da transação
POST   /transacoes/nova       - Registrar transação
POST   /transacoes/<id>/editar - Editar transação
DELETE /transacoes/<id>       - Deletar transação
POST   /transacoes/importar-ofx - Importar arquivo OFX
GET    /transacoes/relatorio  - Gerar relatório
```

### **Projeções** (`routes/projecoes.py`)
```
GET    /projecoes             - Visualizar projeções
POST   /projecoes/simular     - Criar simulação
GET    /ferramentas           - Acessar calculadoras
POST   /ferramentas/dívidas   - Amortização
POST   /ferramentas/juros     - Juros compostos
POST   /ferramentas/aposentadoria - Projeção
POST   /ferramentas/emergencia    - Reserva
```

### **Educacional** (`routes/educacional.py`)
```
GET    /educacao/modulos      - Listar módulos
GET    /educacao/glossario    - Acessar glossário
GET    /educacao/modulo/<num> - Visualizar módulo
```

### **Main** (`routes/main.py`)
```
GET    /                      - Dashboard principal
GET    /home                  - Página inicial
GET    /sobre                 - Sobre a aplicação
```

---

## 🛠️ Desenvolvimento

### **Estrutura de Blueprints**

Os Blueprints organizam as rotas por funcionalidade:

```python
from flask import Blueprint

usuario_bp = Blueprint('usuario', __name__, url_prefix='/usuarios')

@usuario_bp.route('/perfil')
def perfil():
    return render_template('usuario/perfil.html')
```

### **Criação de Nova Funcionalidade**

1. **Criar modelo** em `app/models.py`
2. **Criar rota** em `app/routes/novo_modulo.py`
3. **Registrar blueprint** em `app/__init__.py`
4. **Criar template** em `app/templates/novo_modulo/`
5. **Adicionar estilos** em `app/static/css/novo_modulo.css`
6. **Criar migração:** `flask db migrate -m "Descrição"`
7. **Testar** a funcionalidade

### **Padrões de Código**
- Seguir [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Adicionar docstrings em funções
- Usar type hints quando apropriado
- Comentários explicativos em lógicas complexas
- Tratamento de erros apropriado

---

## 🔐 Segurança

### **Implementações de Segurança**
- ✅ Hash bcrypt para senhas (nunca armazenar em texto plano)
- ✅ Flask-Login para gerenciamento de sessões
- ✅ CSRF protection via Jinja2
- ✅ SQL Injection prevenido com SQLAlchemy ORM
- ✅ Variáveis de ambiente para dados sensíveis
- ✅ Validação de entrada do usuário
- ✅ Tokens para recuperação de senha

### **Boas Práticas**
- ❌ Nunca fazer commit de `.env` com dados reais
- ✅ Use `SECRET_KEY` complexa (mínimo 16 caracteres) em produção
- ✅ Valide todas as entradas de usuário
- ✅ Use HTTPS em produção
- ✅ Mantenha dependências atualizadas
- ✅ Implemente rate limiting em produção

---

## 📝 Sistema de Logs

A aplicação registra eventos em:

**Localização:** `logs/servidor.log`

**Configuração:**
- Rotação automática (5MB por arquivo, máximo 3 arquivos)
- Níveis: INFO, WARNING, ERROR, CRITICAL
- Formato: `%(asctime)s %(levelname)s: %(message)s`

**Visualizar logs:**
```powershell
Get-Content logs/servidor.log -Tail 50
```

---

## 🤝 Contribuindo

Contribuições são bem-vindas! O projeto está aberto para melhorias e sugestões.

### **Como Contribuir**
1. Faça um Fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Add NovaFuncionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request com descrição detalhada

### **Padrões de Contribuição**
- Código deve seguir PEP 8
- Adicione testes para novas funcionalidades
- Atualize documentação quando necessário
- Use commit messages descritivas

---

## 📚 Documentação Adicional

Consulte a pasta `Documentação/` para documentação completa:

- **TAP** - Termo de Abertura do Projeto
- **Requisitos** - Especificações funcionais detalhadas
- **Caso de Uso** - Fluxos de usuário e cenários
- **Prototipação** - Wireframes e mockups de interface
- **Fluxograma** - Diagramas de processo do sistema
- **Testes Manuais** - Casos de teste e validação
- **Manual do Usuário** - Guia completo de uso
- **Logo** - Identidade visual do projeto

---

## 📜 Licença

Este projeto está sob a licença especificada no arquivo `LICENSE`.

---

## 👥 Autores

**Natã Rabelo Pires**  
- GitHub: [@NataRabelo](https://github.com/NataRabelo)
- Desenvolvedor Full-Stack

**Natã Santa Fé**  
- Desenvolvedor Full-Stack

---

## 📞 Suporte e Feedback

Para dúvidas, sugestões ou reportar bugs:

- 📧 [Abra uma Issue](https://github.com/NataRabelo/Monevo/issues)
- 💬 [Envie uma Pull Request](https://github.com/NataRabelo/Monevo/pulls) com melhorias
- 📖 Consulte a documentação do projeto

---

## 🗓️ Histórico de Versões

### **v1.0.0** (Atual - TCC)
- ✅ Autenticação e gerenciamento de usuários
- ✅ Gestão de contas bancárias
- ✅ Gestão de cartões de crédito
- ✅ Sistema de transações com filtros avançados
- ✅ Importação de extratos OFX
- ✅ Projeções financeiras e simulações
- ✅ Módulo educacional com 3 módulos
- ✅ Calculadoras e ferramentas financeiras
- ✅ Sistema de logs com rotação
- ✅ Recuperação de senha por e-mail

### **Roadmap Futuro**
- 📋 Exportação de relatórios em PDF
- 📱 Aplicativo mobile
- 🔔 Notificações de vencimentos
- 💹 Integração com APIs bancárias
- 📊 Gráficos avançados
- 🔐 Autenticação de dois fatores

---

## 🙏 Agradecimentos

Agradecemos a todos os professores, mentores e colegas que contribuíram para o desenvolvimento deste projeto como Trabalho de Conclusão de Curso.

---

**Desenvolvido com ❤️ como Trabalho de Conclusão de Curso**

*Monevo - Money Evolution: Transformando Finanças Pessoais*

---

**Data de Última Atualização:** Dezembro de 2025

