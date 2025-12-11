document.addEventListener("DOMContentLoaded", function () {

    const formatBRL = (v) =>
        new Intl.NumberFormat("pt-BR", {
            style: "currency",
            currency: "BRL"
        }).format(v);

    const selectFiltroMes = document.querySelector("#filtro_cartao_mes");
    
    // Iniciar a projeção automaticamente ao carregar a página
    fetchDataAndRender(); 

    let graficoBarra, graficoLinha, graficoPizzaReceita, graficoPizzaDespesa;
    let dadosCache = null; // Cache para os dados completos dos 12 meses

    selectFiltroMes.addEventListener("change", () => {
        const mesSelecionado = selectFiltroMes.value;
        
        // Se a opção selecionada for a Visão Anual (Macro), os cards mostram o total do período
        if (mesSelecionado === "anual") {
            // Re-renderiza os cards com os totais anuais (você precisaria calcular os totais anuais no backend e enviar)
            // Por simplicidade, se for "anual", vamos pegar o saldo final.
            // Para Receita/Despesa Anual, precisaríamos de uma nova consulta no backend,
            // mas por agora, voltamos ao default (Mês Atual). 
            // Para uma solução simples, vamos manter a visão mensal, exceto para o card final.
            
            // Refaz a requisição SEM filtros para resetar os cards para o mês atual
            fetchDataAndRender();
        } else {
             const [mes, ano] = mesSelecionado.split('/');
             // Dispara a requisição para buscar os dados de CARD do mês/ano selecionado
             fetchDataAndRender(mes, ano); 
        }
    });


    function fetchDataAndRender(filtroMes, filtroAno) {
        
        let url = '/projecao/dados';
        
        // Se houver filtros, a URL é alterada. Isso acontece APENAS no 'change' do select
        if (filtroMes && filtroAno) {
             url += `?mes=${filtroMes}&ano=${filtroAno}`;
        }

        fetch(url)
            .then(r => r.json())
            .then(dados => {
                
                // Se estivermos na chamada inicial (sem filtros), cacheamos e montamos tudo
                if (!filtroMes && !filtroAno) { 
                    dadosCache = dados;
                    
                    // 1. Popula o filtro de meses
                    popularFiltroMeses(dados.meses_disponiveis);
                    
                    // 2. Renderiza todos os gráficos (fixos em 12 meses)
                    renderizarGraficos(dados);
                }
                
                // 3. Atualiza os cards (baseado no filtro ou no default do servidor)
                atualizarCards(dados);
            });
    }
    
    function popularFiltroMeses(meses) {
        // Limpa o select e adiciona a opção de Visão Anual (Macro)
        selectFiltroMes.innerHTML = ''; 
        
        // Cria as opções Mensais (Micro)
        meses.forEach((chave, index) => {
            const option = document.createElement('option');
            const [mes, ano] = chave.split('/');
            
            // Formatando o mês (Ex: "01/2025" -> "Janeiro/2025")
            const nomeMes = new Date(ano, mes - 1, 1).toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' });
            
            option.value = chave;
            option.textContent = nomeMes.charAt(0).toUpperCase() + nomeMes.slice(1);
            
            // Define o primeiro mês como default (Mês Atual)
            if (index === 0) {
                option.selected = true;
            }
            selectFiltroMes.appendChild(option);
        });
        
        // Adiciona a opção Anual por último (Visão Macro)
        const optionAnual = document.createElement('option');
        optionAnual.value = 'anual';
        optionAnual.textContent = 'Visão Macro (Total 12 meses)';
        selectFiltroMes.appendChild(optionAnual);
    }


    function atualizarCards(d) {
        
        const cards = d.cards;
        const recomendacoes = d.recomendacoes_card;

        // Saldo Inicial da Projeção (Fixo)
        document.querySelector(".text-saldo").textContent =
            formatBRL(cards.saldo_inicial_projecao);
            
        // Cards do Mês Selecionado
        document.querySelector(".text-receita").textContent =
            formatBRL(cards.receita_card);

        document.querySelector(".text-despesa").textContent =
            formatBRL(cards.despesa_card);

        const resultElem = document.querySelector(".text-resultado-pos");
        const resultado = cards.resultado_card;

        resultElem.textContent =
            (resultado >= 0 ? "+ " : "- ") + formatBRL(Math.abs(resultado));

        resultElem.classList.toggle("text-resultado-neg", resultado < 0);
        
        document.querySelector(".text-saldo-acumulado-card").textContent =
            formatBRL(cards.saldo_acumulado_card);
            
        // Saldo Projetado Final (Fixo - última data da projeção)
        document.querySelector(".text-saldo-final-projecao").textContent =
            formatBRL(cards.saldo_final_projecao);


        // Recomendação (Mês Selecionado)
        document.querySelector(".text-necessidade-max").textContent =
            formatBRL(recomendacoes.gasto_mensal_recomendado);
        
        document.querySelector(".text-investimento-min").textContent =
            formatBRL(recomendacoes.investimentos_sugerido);
    }

    function renderizarGraficos(d) {
        
        // CORREÇÃO: Usar a lista ordenada (meses_disponiveis) para os labels
        const labelsOrdenados = d.meses_disponiveis;
        const agrupados = d.dados_mensais_agrupados;

        // --- PREPARAÇÃO DOS DADOS DE LINHA E BARRA ---
        const receitasBarra = labelsOrdenados.map(m => agrupados[m] ? agrupados[m].Receita : 0.0);
        const despesasBarra = labelsOrdenados.map(m => agrupados[m] ? agrupados[m].Despesa : 0.0);

        const fluxoLinha = d.fluxo_linha;
        const saldosLinha = fluxoLinha.map(i => i.saldo);
        const receitasLinha = fluxoLinha.map(i => i.receita);
        const despesasLinha = fluxoLinha.map(i => i.despesa);
        const investimentoLinha = fluxoLinha.map(i => i.investimento_sugerido_acumulado);

        
        // --- GRÁFICO BARRA (Receita x Despesa) ---
        const ctxBarra = document.getElementById("graficoBarra");
        if (graficoBarra) graficoBarra.destroy();

        graficoBarra = new Chart(ctxBarra, {
            type: "bar",
            data: {
                labels: labelsOrdenados, // CHAVES ORDENADAS
                datasets: [
                    {
                        label: "Receita",
                        data: receitasBarra,
                        backgroundColor: "#4CAF50",
                    },
                    {
                        label: "Despesa",
                        data: despesasBarra,
                        backgroundColor: "#FF5252",
                    }
                ]
            }
        });

        // --- GRÁFICO LINHA (4 Linhas) ---
        const ctxLinha = document.getElementById("graficoLinha");
        if (graficoLinha) graficoLinha.destroy();

        graficoLinha = new Chart(ctxLinha, {
            type: "line",
            data: {
                labels: labelsOrdenados, // CHAVES ORDENADAS
                datasets: [
                    {
                        label: "Saldo Acumulado (R$) - Principal",
                        data: saldosLinha,
                        borderColor: "#3C90C0",
                        tension: 0.4,
                        fill: false,
                        yAxisID: 'y'
                    },
                    {
                        label: "Investimento Sugerido (Acumulado R$)",
                        data: investimentoLinha,
                        borderColor: "#FFC107", // Amarelo
                        tension: 0.4,
                        fill: false,
                        yAxisID: 'y'
                    },
                    {
                        label: "Receita (Mensal R$)",
                        data: receitasLinha,
                        borderColor: "#4CAF50",
                        tension: 0.4,
                        fill: true,
                        backgroundColor: 'rgba(76, 175, 80, 0.2)',
                        yAxisID: 'y2' // Novo Eixo
                    },
                    {
                        label: "Despesa (Mensal R$)",
                        data: despesasLinha,
                        borderColor: "#FF5252",
                        tension: 0.4,
                        fill: true,
                        backgroundColor: 'rgba(255, 82, 82, 0.2)',
                        yAxisID: 'y2' // Novo Eixo
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: { // Eixo principal (Saldo/Investimento)
                        type: 'linear',
                        display: 'auto',
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Saldo Acumulado / Investimento (R$)'
                        }
                    },
                    y2: { // Eixo secundário (Receita/Despesa Mensal)
                        type: 'linear',
                        display: 'auto',
                        position: 'right',
                        grid: {
                            drawOnChartArea: false,
                        },
                        title: {
                            display: true,
                            text: 'Receita / Despesa Mensal (R$)'
                        }
                    }
                }
            }
        });

        // --- GRÁFICO PIZZA RECEITA ---
        const ctxPizzaReceita = document.getElementById("graficoPizzaReceita");
        if (graficoPizzaReceita) graficoPizzaReceita.destroy();

        graficoPizzaReceita = new Chart(ctxPizzaReceita, {
            type: "pie",
            data: {
                labels: d.pizza_receita.map(i => i.categoria),
                datasets: [{
                    data: d.pizza_receita.map(i => i.valor),
                    backgroundColor: ["#4CAF50", "#009688", "#3C90C0", "#FFC107", "#9C27B0", "#FF5252"],
                }]
            },
            options: {
                plugins: {
                    legend: {
                        position: 'right',
                    }
                }
            }
        });

        // --- GRÁFICO PIZZA DESPESA ---
        const ctxPizzaDespesa = document.getElementById("graficoPizzaDespesa");
        if (graficoPizzaDespesa) graficoPizzaDespesa.destroy();

        graficoPizzaDespesa = new Chart(ctxPizzaDespesa, {
            type: "pie",
            data: {
                labels: d.pizza_despesa.map(i => i.categoria),
                    datasets: [{
                    data: d.pizza_despesa.map(i => i.valor),
                    backgroundColor: ["#FF5252", "#FFC107", "#3C90C0", "#9C27B0", "#4CAF50", "#009688"],
                }]
            },
            options: {
                plugins: {
                    legend: {
                        position: 'right',
                    }
                }
            }
        });
    }
});