  // ----------------- MODAL EDITAR CONTA -----------------
document.addEventListener("DOMContentLoaded", function () {

    // Ativa máscara nos campos currency
    aplicarMascaraMoeda();

    // Modal de edição de conta
    const modalEditarConta = document.getElementById("modalEditarConta");

    modalEditarConta.addEventListener("show.bs.modal", function (event) {

        const button = event.relatedTarget;

        const id = button.getAttribute("data-conta-id");
        const nome = button.getAttribute("data-nome");
        const instituicao = button.getAttribute("data-instituicao");
        const saldo = button.getAttribute("data-saldo");
        const tipo = button.getAttribute("data-tipo");

        // Preenche os campos do modal
        document.getElementById("edit-conta-id").value = id;
        document.getElementById("edit-nome-conta").value = nome;
        document.getElementById("edit-instituicao").value = instituicao;

        // saldo precisa ser formatado como currency antes
        document.getElementById("edit-saldo-inicial").value =
            new Intl.NumberFormat("pt-BR", {
                style: "currency",
                currency: "BRL"
            }).format(saldo);

        document.getElementById("edit-tipo_conta").value = tipo;
    });

    // Modal de edição do cartão
    const modalEditarCartao = document.getElementById("modalEditarCartao");

    modalEditarCartao.addEventListener("show.bs.modal", function (event) {

        const button = event.relatedTarget;

        const id = button.getAttribute("data-cartao-id");
        const nome = button.getAttribute("data-nome");
        const bandeira = button.getAttribute("data-bandeira");
        const limite = button.getAttribute("data-limite");
        const fechamento = button.getAttribute("data-fechamento");
        const vencimento = button.getAttribute("data-vencimento");
        const conta = button.getAttribute("data-conta");

        // Preenche os campos do modal
        document.getElementById("edit-cartao-id").value = id;
        document.getElementById("edit-nome-cartao").value = nome;
        document.getElementById("edit-bandeira").value = bandeira;

        // saldo precisa ser formatado como currency antes
        document.getElementById("edit-limite").value =
            new Intl.NumberFormat("pt-BR", {
                style: "currency",
                currency: "BRL"
            }).format(limite);

        document.getElementById("edit-dia-fechamento-fatura").value = fechamento;
        document.getElementById("edit-dia-vencimento-fatura").value = vencimento;
        document.getElementById("edit-conta-cartao").value = conta;
    });

    const abaAtiva = localStorage.getItem("abaAtiva");
    if (abaAtiva) {
        const aba = document.querySelector(`[data-bs-target="${abaAtiva}"]`);
        if (aba) {
        const tab = new bootstrap.Tab(aba);
        tab.show();
        }
    }

    // --- Salvar a aba quando o usuário trocar ---
    const tabs = document.querySelectorAll('button[data-bs-toggle="tab"]');
    tabs.forEach(tab => {
        tab.addEventListener("shown.bs.tab", function (event) {
        const target = event.target.getAttribute("data-bs-target");
        localStorage.setItem("abaAtiva", target);
        });
    });
});

