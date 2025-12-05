document.addEventListener("DOMContentLoaded", function () {

    const btn = document.querySelector(".btn-custom");
    const formatBRL = (v) =>
        new Intl.NumberFormat("pt-BR", {
            style: "currency",
            currency: "BRL"
        }).format(v);

    btn.addEventListener("click", () => {
        const inicio = document.querySelector("#data_inicio").value;
        const fim = document.querySelector("#data_fim").value;
        const tipo = document.querySelector("#tipo_projecao").value;

        if (!inicio || !fim) {
            alert("Selecione o período!");
            return;
        }

        fetch(`/projecao/dados?inicio=${inicio}&fim=${fim}&tipo=${tipo}`)
            .then(r => r.json())
            .then(dados => atualizarTela(dados));
    });

    let graficoBarra, graficoPizza, graficoLinha;

    function atualizarTela(d) {

        // ----------------------------
        //  Atualizar cards com BRL
        // ----------------------------
        document.querySelector(".text-saldo").textContent =
            formatBRL(d.cards.saldo_anterior);

        document.querySelector(".text-receita").textContent =
            formatBRL(d.cards.receitas);

        document.querySelector(".text-despesa").textContent =
            formatBRL(d.cards.despesas);

        const resultElem = document.querySelector(".text-resultado-pos");
        const resultado = d.cards.resultado;

        resultElem.textContent =
            (resultado >= 0 ? "+ " : "- ") + formatBRL(Math.abs(resultado));

        resultElem.classList.toggle("text-resultado-neg", resultado < 0);

        // ----------------------------
        //   GRÁFICO BARRA
        // ----------------------------
        const ctxBarra = document.getElementById("graficoBarra");

        if (graficoBarra) graficoBarra.destroy();

        const labels = Object.keys(d.barra);
        const receitas = labels.map(m => d.barra[m].Receita);
        const despesas = labels.map(m => d.barra[m].Despesa);

        graficoBarra = new Chart(ctxBarra, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Receita",
                        data: receitas,
                        backgroundColor: "#4CAF50",
                    },
                    {
                        label: "Despesa",
                        data: despesas,
                        backgroundColor: "#FF5252",
                    }
                ]
            }
        });

        // ----------------------------
        //   GRÁFICO PIZZA
        // ----------------------------
        const ctxPizza = document.getElementById("graficoPizza");

        if (graficoPizza) graficoPizza.destroy();

        graficoPizza = new Chart(ctxPizza, {
            type: "pie",
            data: {
                labels: d.pizza.map(i => i.categoria),
                datasets: [{
                    data: d.pizza.map(i => i.valor),
                    backgroundColor: [
                        "#3C90C0", "#4CAF50", "#FF5252", "#FFC107",
                        "#9C27B0", "#009688", "#FF9800"
                    ]
                }]
            }
        });

        // ----------------------------
        //   GRÁFICO LINHA (fluxo)
        // ----------------------------
        const ctxLinha = document.getElementById("graficoLinha");

        if (graficoLinha) graficoLinha.destroy();

        graficoLinha = new Chart(ctxLinha, {
            type: "line",
            data: {
                labels: d.linha.map(i => i.data),
                datasets: [{
                    label: "Saldo",
                    data: d.linha.map(i => i.saldo),
                    borderColor: "#3C90C0",
                    tension: 0.3,
                    fill: false,
                }]
            }
        });

    }

});
