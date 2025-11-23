# utils.py

import locale

# Configurar locale para moeda brasileira
try:
    locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
except:
    pass  # Caso o sistema não tenha o locale, evita crash


def limpar_currency(valor_str):
    """
    Remove máscara de moeda (R$ 1.234,56 → 1234.56)
    Retorna float.
    """
    if not valor_str:
        return 0.0

    valor_str = str(valor_str)

    # Remove R$, espaços e pontos de milhar
    valor_str = valor_str.replace("R$", "").replace(" ", "").replace(".", "")

    # Troca a vírgula decimal por ponto
    valor_str = valor_str.replace(",", ".")

    try:
        return float(valor_str)
    except:
        return 0.0


def formatar_currency(valor):
    """
    Converte número em formato de moeda brasileiro.
    1234.56 → R$ 1.234,56
    """
    try:
        return locale.currency(valor, grouping=True)
    except:
        # Fallback caso locale falhe
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def limpar_espacos(texto):
    """
    Remove espaços no início e final da string.
    ' Natã ' → 'Natã'
    """
    if texto is None:
        return None
    return texto.strip()


def normalizar_texto(texto):
    """
    Remove múltiplos espaços no meio.
    'João   da   Silva' → 'João da Silva'
    """
    if texto is None:
        return None
    return " ".join(texto.split())
