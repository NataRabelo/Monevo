// Obtém o contexto do canvas onde o gráfico será renderizado
const ctx = document.getElementById('graficoFinanceiro').getContext('2d');

// Cria o gráfico de linhas
new Chart(ctx, {
    type: 'line',
    data: {
        // Rótulos dos meses
        labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai'],
        datasets: [
            {
                label: 'Receitas',
                data: [80, 120, 250, 340, 470],
                borderColor: 'green',
                backgroundColor: 'rgba(0, 253, 0, 0.1)',
                fill: true, // Preenche a área sob a linha
                tension: 0.4 // Suaviza a curva da linha
            },
            {
                label: 'Despesas',
                data: [100, 250, 350, 450, 500],
                borderColor: 'red',
                backgroundColor: 'rgba(255, 0, 0, 0.1)',
                fill: true,
                tension: 0.4
            }
        ]
    },
    options: {
        responsive: true, // Adapta o gráfico ao tamanho da tela
        plugins: {
            legend: {
                position: 'top' // Posição da legenda
            }
        }
    }
});
