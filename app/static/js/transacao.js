document.addEventListener("DOMContentLoaded", function() {

  // ===================== MODAIS ENCADEADOS  =====================

  const modalGerenciar = document.getElementById("modalGerenciarCategorias")
    ? new bootstrap.Modal("#modalGerenciarCategorias")
    : null;

  const modalNova = document.getElementById("modalNovaCategoria")
    ? new bootstrap.Modal("#modalNovaCategoria")
    : null;

  const modalEditar = document.getElementById("modalEditarCategoria")
    ? new bootstrap.Modal("#modalEditarCategoria")
    : null;

  const btnNova = document.querySelector("[data-bs-target='#modalNovaCategoria']");
  if (btnNova && modalGerenciar && modalNova) {
    btnNova.addEventListener("click", (e) => {
      e.preventDefault();
      modalGerenciar.hide();

      setTimeout(() => modalNova.show(), 300);
    });

    document.getElementById("modalNovaCategoria")
      .addEventListener("hidden.bs.modal", () => {
        modalGerenciar.show();
      });
  }

  const btnsEditar = document.querySelectorAll("[data-bs-target='#modalEditarCategoria']");
  if (btnsEditar.length > 0 && modalGerenciar && modalEditar) {
    btnsEditar.forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        modalGerenciar.hide();

        setTimeout(() => modalEditar.show(), 300);
      });
    });

    document.getElementById("modalEditarCategoria")
      .addEventListener("hidden.bs.modal", () => {
        modalGerenciar.show();
      });
  }


  // ===================== Função auxiliar para BRL =====================
  function formatarParaBRL(valor) {
    return new Intl.NumberFormat("pt-BR", {
      style: "currency",
      currency: "BRL"
    }).format(Number(valor));
  }



  // ===================== EDIÇÃO DE CATEGORIA =====================
  const modalEditarCategoria = document.getElementById("modalEditarCategoria");

  if (modalEditarCategoria) {
    modalEditarCategoria.addEventListener("show.bs.modal", function(event) {
      const button = event.relatedTarget;
      const categoria_id = button.getAttribute("data-categoria-id");
      const nome = button.getAttribute("data-nome");
      const tipo = button.getAttribute("data-tipo");

      const form = document.getElementById("formEditarCategoria");

      form.action = `/categoria/editar/${categoria_id}`;

      document.getElementById("edit-categoria-id").value = categoria_id;
      document.getElementById("edit-categoria-nome").value = nome;
      document.getElementById("edit-categoria-tipo").value = tipo;
    });
  }



  // ===================== EDIÇÃO DE RECEITA =====================
  const modalEditarReceita = document.getElementById("modalEditarReceita");

  if (modalEditarReceita) {
    modalEditarReceita.addEventListener("show.bs.modal", function(event){

      const button = event.relatedTarget;

      const receita_id   = button.getAttribute("data-receita-id");
      const conta        = button.getAttribute("data-conta-id");
      const categoria    = button.getAttribute("data-categoria-id");
      const descricao    = button.getAttribute("data-descricao");
      const valor        = button.getAttribute("data-valor");
      const data         = button.getAttribute("data-data-transacao");
      const recorrencia  = button.getAttribute("data-recorrencia");

      document.getElementById("receita-id").value = receita_id;
      document.getElementById("edit-descricao-receita").value = descricao;
      document.getElementById("edit-conta-transacao-receita").value = conta;

      const categoriaSelect = document.getElementById("edit-categoria-receita");
      if (categoriaSelect) categoriaSelect.value = categoria;

      document.getElementById("edit-data-transacao-receita").value = data;
      document.getElementById("edit-recorrencia-receita").value = recorrencia;

      document.getElementById("edit-valor-transacao-receita").value = formatarParaBRL(valor);
    });
  }



  // ===================== EDIÇÃO DE DESPESA =====================
  const modalEditarDespesa = document.getElementById("modalEditarDespesa");

  if (modalEditarDespesa) {
    modalEditarDespesa.addEventListener("show.bs.modal", function(event){

      const button = event.relatedTarget;

      const despesa_id   = button.getAttribute("data-receita-id");
      const conta        = button.getAttribute("data-conta-id");
      const categoria    = button.getAttribute("data-categoria-id");
      const descricao    = button.getAttribute("data-descricao");
      const valor        = button.getAttribute("data-valor");
      const data         = button.getAttribute("data-data-transacao");
      const recorrencia  = button.getAttribute("data-recorrencia");

      document.getElementById("despesa_id").value = despesa_id;
      document.getElementById("edit-descricao-despesa").value = descricao;
      document.getElementById("edit-conta-transacao-despesa").value = conta;

      const categoriaSelect = document.getElementById("edit-categoria-despesa");
      if (categoriaSelect) categoriaSelect.value = categoria;

      document.getElementById("edit-tipo-transacao-despesa").value = "Despesa";
      document.getElementById("edit-data-transacao-despesa").value = data;
      document.getElementById("edit-recorrencia-despesa").value = recorrencia;

      document.getElementById("edit-valor-transacao-despesa").value = formatarParaBRL(valor);
    });
  }



  // ===================== INPUT DE MOEDA =====================
  document.querySelectorAll(".currency").forEach(input => {
    input.addEventListener("input", function() {
        let value = this.value.replace(/\D/g, "");

        if (value.length > 0) {
            value = (parseInt(value) / 100).toLocaleString("pt-BR", {
                style: "currency",
                currency: "BRL"
            });
        } else {
            value = "";
        }
        this.value = value;
    });
  });

});
