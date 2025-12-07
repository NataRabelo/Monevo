import locale
from flask import current_app

# -------------------------------------
# Configurar locale para pt_BR
# -------------------------------------
try:
    locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
except:
    pass

# -------------------------------------
# Limpar e formatar valores monetários
# -------------------------------------
def limpar_currency(valor_str):
    if not valor_str:
        return 0.0

    valor_str = str(valor_str)
    valor_str = valor_str.replace("R$", "").replace(" ", "").replace(".", "")
    valor_str = valor_str.replace(",", ".")

    try:
        return float(valor_str)
    except:
        return 0.0

# -------------------------------------
# Formatar valores monetários
# -------------------------------------
def formatar_currency(valor):
    try:
        return locale.currency(valor, grouping=True)
    except:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# -------------------------------------
# Limpar e normalizar textos
# -------------------------------------
def limpar_espacos(texto):
    if texto is None:
        return None
    return texto.strip()


# -------------------------------------
# Limpar e normalizar textos com multiplos espaços
# -------------------------------------
def normalizar_texto(texto):
    if texto is None:
        return None
    return " ".join(texto.split())



# -------------------------------------
# Registrar requisições HTTP no log
# -------------------------------------
def registrar_requisicao(req, status_code: int, mensagem: str = ""):
    ip = req.remote_addr
    metodo = req.method
    caminho = req.path
    current_app.logger.info(f"{ip} {metodo} {caminho} -> {status_code} {mensagem}")