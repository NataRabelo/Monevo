  // ----------------- MODAL EDITAR CONTA -----------------
document.addEventListener("DOMContentLoaded", function () {

    // Ativa máscara nos campos currency
    aplicarMascaraMoeda();

    // Modal de edição
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
});
