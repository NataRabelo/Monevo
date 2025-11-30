document.addEventListener("DOMContentLoaded", function() {

  const modalEditarReceita = document.getElementById("modalEditarReceita");

  modalEditarReceita.addEventListener("show.bs.modal", function(event){

    const button = event.relatedTarget;

    const receita_id = button.getAttribute("data-receita-id");
    const conta = button.getAttribute("data-conta-id");
    const categoria = button.getAttribute("data-categoria-id");
    const descricao = button.getAttribute("data-descricao");
    const valor = button.getAttribute("data-valor");
    const data = button.getAttribute("data-data-transacao");
    const recorrencia = button.getAttribute("data-recorrencia");

    document.getElementById("receita-id").value = receita_id;
    document.getElementById("edit-descricao").value = descricao;
    document.getElementById("edit-conta-transacao").value = conta;

    if (document.getElementById("edit-categoria"))
      document.getElementById("edit-categoria").value = categoria;

    document.getElementById("edit-data-transacao").value = data;
    document.getElementById("edit-recorrencia").value = recorrencia;

    document.getElementById("edit-valor-transacao").value =
    new Intl.NumberFormat("pt-BR", {
        style: "currency",
        currency: "BRL"
    }).format(Number(valor));

  });

});
