from decimal import Decimal
import locale

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

def formatar_currency(valor):
    try:
        return locale.currency(valor, grouping=True)
    except:
        return "R$ 0,00"
