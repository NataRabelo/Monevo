
# Monevo

**Project**: Monevo is a web application for personal financial management (controle financeiro pessoal). It helps users track accounts, cards, categories, transactions, imports (OFX), and projections. Developed as an academic capstone project.

**Authors**: Natã Rabelo and Natã Santa Fé

**Tech Stack**
- **Backend**: Python, Flask (Blueprints, Flask-Login, Flask-Mail, Flask-Migrate, Flask-SQLAlchemy)
- **Database**: SQLite (via SQLAlchemy), migrations via Alembic/Flask-Migrate
- **Templates**: Jinja2

**Features**
- User registration, login and authentication
- Accounts and credit cards management
- Categories and transaction tracking (Receita / Despesa)
- OFX import support (bank statement import)
- Monthly summaries and projections
- Email sending for account workflows (password recovery, notifications)

**Requirements**
- See `requirements.txt` for precise package versions. Key packages include `Flask`, `Flask-SQLAlchemy`, `Flask-Migrate`, `Flask-Login`, `Flask-Mail`, and `ofxparse`.

**Quick Start (Windows / PowerShell)**
1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Set required environment variables (example):

```powershell
#$env:FLASK_APP = "run.py"                # optional for flask CLI
#$env:FLASK_ENV = "development"          # development or production
#$env:SECRET_KEY = "change-me"
#$env:EMAIL_REMETENTE = "you@example.com"
#$env:EMAIL_SENHA_APP = "app-password"   # app-specific password for SMTP
```

4. Initialize / apply database migrations (if needed):

```powershell
#$env:FLASK_APP = "run.py"
flask db upgrade
```

5. Run the app:

```powershell
python run.py
```

Open `http://127.0.0.1:5000/` and you will be redirected to the login page.

**Project Structure (important files/folders)**
- `run.py` — Application entrypoint that constructs the Flask app via `create_app`.
- `config.py` — Configuration classes (`DevelopmentConfig`, `ProductionConfig`).
- `requirements.txt` — Python package dependencies.
- `app/` — Main application package:
	- `__init__.py` — App factory, extension initialization, blueprint registration.
	- `models.py` — SQLAlchemy models (Usuarios, Contas, Cartoes, Transacoes, etc.).
	- `routes/` — Blueprints for routes (auth, contas, cartoes, categorias, transacoes, projecoes, ofx, etc.).
	- `services/` — Helper services (OFX parsing, currency formatting, request logging).
	- `static/` and `templates/` — Frontend assets and Jinja2 templates.
- `migrations/` — Alembic/Flask-Migrate files (already present).

**Environment & Email**
The application uses environment variables for sensitive values (SECRET_KEY, email credentials). Example variables used in the app: `SECRET_KEY`, `EMAIL_REMETENTE`, `EMAIL_SENHA_APP`, and `FLASK_ENV`.

**Notes on Database**
- By default the app config uses SQLite and stores the DB inside the `instance/` folder as `development.db` or `production.db` depending on `DEBUG`.
- Use the Flask-Migrate commands to manage schema changes: `flask db migrate` and `flask db upgrade`.

**Contributing**
- Feel free to open issues or submit pull requests. Keep changes focused and add tests where appropriate.

**License**
- See the `LICENSE` file in the repository for licensing information.

**Contact**
- Project authors: Natã Rabelo and Natã Santa Fé

---

If you want, I can:
- add a short walkthrough (register → add account → import OFX)
- add example `.env` file template
- create a minimal Dockerfile for local development

Tell me which of the above you'd like next.