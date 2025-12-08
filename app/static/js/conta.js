// -------------------------------------------------------------
// Controle dos modais de edição (contas e cartões):
// - Preenche automaticamente os campos ao abrir o modal
// - Aplica máscara de moeda nos inputs financeiros
// - Mantém a aba ativa entre recargas usando localStorage
// -------------------------------------------------------------
document.addEventListener("DOMContentLoaded", function () {

    // ---------------------------------------------------------
    // Inicializa a máscara de moeda em todos os campos .currency
    // ---------------------------------------------------------
    aplicarMascaraMoeda();

    // ---------------------------------------------------------
    // Modal: Editar Conta
    // Preenche os campos do modal com os dados enviados no botão
    // ---------------------------------------------------------
    const modalEditarConta = document.getElementById("modalEditarConta");

    modalEditarConta.addEventListener("show.bs.modal", function (event) {
        const button = event.relatedTarget;

        const id = button.getAttribute("data-conta-id");
        const nome = button.getAttribute("data-nome");
        const instituicao = button.getAttribute("data-instituicao");
        const saldo = button.getAttribute("data-saldo");
        const tipo = button.getAttribute("data-tipo");

        document.getElementById("edit-conta-id").value = id;
        document.getElementById("edit-nome-conta").value = nome;
        document.getElementById("edit-instituicao").value = instituicao;

        document.getElementById("edit-saldo-inicial").value =
            new Intl.NumberFormat("pt-BR", {
                style: "currency",
                currency: "BRL"
            }).format(saldo);

        document.getElementById("edit-tipo_conta").value = tipo;
    });

    // ---------------------------------------------------------
    // Modal: Editar Cartão
    // Preenche dados do cartão e formata limite como moeda
    // ---------------------------------------------------------
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

        document.getElementById("edit-cartao-id").value = id;
        document.getElementById("edit-nome-cartao").value = nome;
        document.getElementById("edit-bandeira").value = bandeira;

        document.getElementById("edit-limite").value =
            new Intl.NumberFormat("pt-BR", {
                style: "currency",
                currency: "BRL"
            }).format(limite);

        document.getElementById("edit-dia-fechamento-fatura").value = fechamento;
        document.getElementById("edit-dia-vencimento-fatura").value = vencimento;
        document.getElementById("edit-conta-cartao").value = conta;
    });

    // ---------------------------------------------------------
    // Mantém a aba selecionada após recarregar a página
    // ---------------------------------------------------------
    const abaAtiva = localStorage.getItem("abaAtiva");
    if (abaAtiva) {
        const aba = document.querySelector(`[data-bs-target="${abaAtiva}"]`);
        if (aba) {
            const tab = new bootstrap.Tab(aba);
            tab.show();
        }
    }

    // ---------------------------------------------------------
    // Salva a aba ativa no localStorage quando o usuário troca
    // ---------------------------------------------------------
    const tabs = document.querySelectorAll('button[data-bs-toggle="tab"]');
    tabs.forEach(tab => {
        tab.addEventListener("shown.bs.tab", function (event) {
            const target = event.target.getAttribute("data-bs-target");
            localStorage.setItem("abaAtiva", target);
        });
    });
});
