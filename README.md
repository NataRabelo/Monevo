# 🌐 Monevo — Sistema de Gestão Financeira Pessoal

**Monevo** é uma aplicação web desenvolvida como Trabalho de Conclusão de Curso, focada em **organização financeira pessoal**, oferecendo controle de contas, cartões, categorias, transações, importação OFX e projeções mensais.

> **Autores:** Natã Rabelo & Natã Santa Fé  
> **Tecnologias:** Python • Flask • SQLite • Jinja2

---

## 🚀 Funcionalidades Principais

- 👤 **Autenticação completa**  
  Cadastro, login, logout e recuperação de senha via e-mail.

- 💰 **Gerenciamento financeiro**  
  Contas bancárias, cartões de crédito e categorias personalizadas.

- 🧾 **Registro de transações**  
  Receitas, despesas, filtros, ordenação e organização por data.

- 📥 **Importação OFX**  
  Importação de extratos bancários via arquivo `.ofx`.

- 📊 **Relatórios e projeções**  
  Resumo mensal e projeção financeira.

- ✉️ **Envio de e-mails**  
  Utilizado para fluxo de recuperação de senha e notificações.

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Flask  
  (Blueprints, Flask-Login, Flask-Mail, Flask-Migrate, Flask-SQLAlchemy)

- **Banco de Dados:** SQLite  
- **Migrations:** Alembic / Flask-Migrate  
- **Templates:** Jinja2  
- **Importação Bancária:** ofxparse  

Para a lista completa de pacotes, consulte `requirements.txt`.

---

## 📦 Estrutura do Projeto

monevo/
├── run.py # Entrypoint da aplicação
├── config.py # Configurações (dev/prod)
├── requirements.txt
├── app/
│ ├── init.py # App Factory + extensões
│ ├── models.py # Modelos do banco de dados
│ ├── routes/ # Blueprints das rotas
│ ├── services/ # Serviços (helpers, logs)
│ ├── static/ # CSS, JS, imagens
│ └── templates/ # Templates Jinja2
└── migrations/ # Controle de versão do BD


---

## ⚙️ Instalação e Execução (Windows / PowerShell)

### 1️⃣ Criar e ativar o ambiente virtual

powershell
python -m venv .venv
.venv\Scripts\activate

### 2️⃣ Instalar dependências

pip install -r requirements.txt


### 3️⃣ Configurar variáveis de ambiente

# obrigatório
$env:SECRET_KEY = "troque-por-uma-chave-segura"

# opcional (envio de e-mails)
$env:EMAIL_REMETENTE = "seu-email@gmail.com"
$env:EMAIL_SENHA_APP = "sua-senha-de-app"

# flask
$env:FLASK_ENV = "development"


### 4️⃣ Aplicar migrações

flask db upgrade


### 5️⃣ Executar o sistema

python run.py


Acesse: http://127.0.0.1:5000/

---

## 🗄️ Banco de Dados

### O SQLite é salvo automaticamente na pasta instance/.

Arquivos possíveis:

* development.db
* production.db

### Comandos de migração

* flask db migrate
* flask db upgrade

---

## 📧 Configuração de E-mail

### A aplicação utiliza SMTP para envio de mensagens.

Variáveis utilizadas:

* EMAIL_REMETENTE
* EMAIL_SENHA_APP
* SECRET_KEY
* FLASK_ENV

--- 

## 🤝 Contribuindo

### Contribuições são bem-vindas!
### Sinta-se à vontade para abrir issues ou enviar pull requests.

---

## 📜 Licença

Este projeto está sob a licença especificada no arquivo LICENSE.

---

## 📞 Contato

Autores: Natã Rabelo & Natã Santa Fé
Para dúvidas ou melhorias, abra uma issue no repositório.

---

