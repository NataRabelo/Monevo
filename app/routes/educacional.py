from flask import Blueprint, render_template

# Certifique-se de que o Blueprint está configurado com o nome correto 'educacional'
educacional_bp = Blueprint('educacional', __name__, url_prefix='/educacao')

# 1. Central Educacional (Dashboard)
@educacional_bp.route('/')
def acessarEducacional():
    """Rota principal que carrega a Central de Educação Financeira (educacional.html)."""
    # Dados de exemplo para simular progresso do usuário
    dados_usuario = {
        'progresso_modulo1': '40%',
        'progresso_modulo2': '0%',
    }
    return render_template('dashboard/educacional.html', dados_usuario=dados_usuario)

# 2. Rotas dos Módulos/Trilhas de Aprendizagem
# Estas rotas exigirão templates em 'templates/educacional/moduloX.html'

@educacional_bp.route('/modulo-1')
def modulo1():
    """Página de conteúdo do Módulo 1: Orçamento Descomplicado."""
    return render_template('educacional/modulo1.html', titulo='Módulo 1: Orçamento Descomplicado')

@educacional_bp.route('/modulo-2')
def modulo2():
    """Página de conteúdo do Módulo 2: Livre-se das Dívidas."""
    return render_template('educacional/modulo2.html', titulo='Módulo 2: Livre-se das Dívidas')

@educacional_bp.route('/modulo-3')
def modulo3():
    """Página de conteúdo do Módulo 3: Seus Primeiros Investimentos."""
    return render_template('educacional/modulo3.html', titulo='Módulo 3: Seus Primeiros Investimentos')

# 3. Rotas das Ferramentas/Calculadoras
# Estas rotas exigirão templates em 'templates/ferramentas/nome_ferramenta.html'

@educacional_bp.route('/calc/juros-compostos')
def jurosCompostos():
    """Calculadora de Juros Compostos."""
    return render_template('ferramentas/juros_compostos.html', titulo='Calculadora de Juros Compostos')

@educacional_bp.route('/calc/reserva-emergencia')
def reservaEmergencia():
    """Calculadora de Reserva de Emergência."""
    return render_template('ferramentas/reserva_emergencia.html', titulo='Calculadora de Reserva de Emergência')

@educacional_bp.route('/calc/aposentadoria')
def projecaoAposentadoria():
    """Projeção de Aposentadoria e Independência Financeira."""
    return render_template('ferramentas/projecao_aposentadoria.html', titulo='Projeção Aposentadoria')

@educacional_bp.route('/calc/amortizacao-dividas')
def amortizacaoDividas():
    """Calculadora de Amortização de Dívidas."""
    return render_template('ferramentas/amortizacao_dividas.html', titulo='Simulador de Amortização')

# 4. Rotas de Recursos Adicionais
# Estas rotas exigirão templates em 'templates/educacional/nome_recurso.html'

@educacional_bp.route('/glossario')
def glossario():
    """Página do Glossário Financeiro Completo."""
    return render_template('educacional/glossario.html', titulo='Glossário Financeiro')

@educacional_bp.route('/quizes')
def quizes():
    """Página com Quizes e Desafios de Conhecimento."""
    return render_template('educacional/quizes.html', titulo='Quizes e Desafios')