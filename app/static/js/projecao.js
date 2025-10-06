// Gráfico de Barras - Receitas x Despesas
const ctxBarra = document.getElementById('graficoBarra');
new Chart(ctxBarra, {
    type: 'bar',
    data: {
        labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
        datasets: [
            {
                label: 'Receitas',
                data: [200, 180, 350, 400, 600, 700, 900, 1000, 650, 500, 750, 900],
                backgroundColor: '#306733'
            },
            {
                label: 'Despesas',
                data: [400, 500, 200, 250, 800, 300, 100, 700, 100, 300, 100, 450],
                backgroundColor: '#C62828'
            }
        ]
    },
    options: {
        scales: {
            x: { ticks: { color: 'white' } },
            y: { ticks: { color: 'white' } }
        },
        plugins: {
            legend: { labels: { color: 'white' } }
        }
    }
});

// Gráfico de Linha - Fluxo de Caixa
const ctxLinha = document.getElementById('graficoLinha');
new Chart(ctxLinha, {
    type: 'line',
    data: {
        labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
        datasets: [{
            label: 'Fluxo de caixa',
            data: [200, 180, 350, 400, 600, 700, 900, 1000, 650, 500, 750, 900],
            borderColor: '#3C90C0',
            fill: false,
            tension: 0.3
        }]
    },
    options: {
        scales: {
            x: { ticks: { color: 'white' } },
            y: { ticks: { color: 'white' } }
        },
        plugins: {
            legend: { labels: { color: 'white' } }
        }
    }
});

// Gráfico de Pizza - Proporção
const ctxPizza = document.getElementById('graficoPizza');
new Chart(ctxPizza, {
    type: 'pie',
    data: {
        labels: ['Receitas - 60%', 'Despesas - 40%'],
        datasets: [{
            data: [60, 40],
            backgroundColor: ['#306733', '#C62828']
        }]
    },
    options: {
        plugins: {
            legend: {
                labels: { color: 'white' },
                position: 'bottom'
            }
        }
    }
});