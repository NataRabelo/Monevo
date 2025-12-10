// ================= MÁSCARA DE MOEDA =================
document.addEventListener("input", function (e) {
    if (e.target.classList.contains("currency")) {
        let value = e.target.value.replace(/[^\d]/g, "");
        value = (value / 100).toFixed(2) + "";
        value = value.replace(".", ",");
        e.target.value = "R$ " + value.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    }
});

// ================= MODAL EDITAR RECEITA =================
const modalEditarReceita = document.getElementById("modalEditarReceita");

modalEditarReceita.addEventListener("show.bs.modal", function (event) {
    const button = event.relatedTarget;

    const receitaId = button.getAttribute("data-receita-id");
    const contaId = button.getAttribute("data-conta-id");
    const categoriaId = button.getAttribute("data-categoria-id");
    const descricao = button.getAttribute("data-descricao");
    const valor = button.getAttribute("data-valor");
    const dataTransacao = button.getAttribute("data-data-transacao");
    const recorrencia = button.getAttribute("data-recorrencia");

    document.getElementById("receita-id").value = receitaId;
    document.getElementById("edit-descricao-receita").value = descricao;
    document.getElementById("edit-valor-transacao-receita").value = 
            new Intl.NumberFormat("pt-BR", {
                style: "currency",
                currency: "BRL"
            }).format(valor);
    document.getElementById("edit-categoria-receita").value = categoriaId;
    document.getElementById("edit-conta-transacao-receita").value = contaId;
    document.getElementById("edit-data-transacao-receita").value = dataTransacao;
    document.getElementById("edit-recorrencia-receita").value = recorrencia;
});

// ================= MODAL EDITAR DESPESA =================
const modalEditarDespesa = document.getElementById("modalEditarDespesa");

modalEditarDespesa.addEventListener("show.bs.modal", function (event) {
    const button = event.relatedTarget;

    const despesaId = button.getAttribute("data-despesa-id");
    const contaId = button.getAttribute("data-conta-id");
    const categoriaId = button.getAttribute("data-categoria-id");
    const cartaoId = button.getAttribute("data-cartao-id");
    const descricao = button.getAttribute("data-descricao");
    const valor = button.getAttribute("data-valor");
    const dataTransacao = button.getAttribute("data-data-transacao");
    const recorrencia = button.getAttribute("data-recorrencia");

    document.getElementById("despesa-id").value = despesaId;
    document.getElementById("edit-descricao-despesa").value = descricao;
    document.getElementById("edit-valor-transacao-despesa").value = 
            new Intl.NumberFormat("pt-BR", {
                style: "currency",
                currency: "BRL"
            }).format(valor);
    document.getElementById("edit-categoria-despesa").value = categoriaId;
    document.getElementById("edit-conta-transacao-despesa").value = contaId;
    document.getElementById("edit-data-transacao-despesa").value = dataTransacao;
    document.getElementById("edit-recorrencia-despesa").value = recorrencia;

    document.getElementById("edit-cartao-despesa").value = cartaoId ? cartaoId : "";
});

// ================= MODAIS ENCADEADOS (CATEGORIAS) =================
const modalGerenciarCategorias = new bootstrap.Modal(document.getElementById("modalGerenciarCategorias"));
const modalNovaCategoria = new bootstrap.Modal(document.getElementById("modalNovaCategoria"));
const modalEditarCategoria = new bootstrap.Modal(document.getElementById("modalEditarCategoria"));

// Abrir modal nova categoria
document.querySelectorAll(".open-nova-categoria").forEach(btn => {
    btn.addEventListener("click", () => {
        modalGerenciarCategorias.hide();
        setTimeout(() => modalNovaCategoria.show(), 300);
    });
});

// Abrir modal editar categoria
document.querySelectorAll(".open-editar-categoria").forEach(btn => {
    btn.addEventListener("click", () => {
        const id = btn.dataset.id;
        const nome = btn.dataset.nome;
        const tipo = btn.dataset.tipo;

        document.getElementById("edit-categoria-id").value = id;
        document.getElementById("edit-categoria-nome").value = nome;
        document.getElementById("edit-categoria-tipo").value = tipo;

        modalGerenciarCategorias.hide();
        setTimeout(() => modalEditarCategoria.show(), 300);
    });
});

// Retornar para modal Gerenciar Categorias após fechar edição ou criação
document.getElementById("modalNovaCategoria").addEventListener("hidden.bs.modal", function () {
    modalGerenciarCategorias.show();
});

document.getElementById("modalEditarCategoria").addEventListener("hidden.bs.modal", function () {
    modalGerenciarCategorias.show();
});

// ================= FECHAR BACKDROP ZUMBI (SEGURANÇA) =================
document.addEventListener("hidden.bs.modal", () => {
    document.querySelectorAll(".modal-backdrop").forEach(el => el.remove());
});

// ================= BLOQUEIO DE CAMPOS RECORRÊNCIA E PARCELAS =================
document.addEventListener("DOMContentLoaded", function () {

  function configurarBloqueios(parcelasInputId, recorrenciaSelectId) {
    const parcelasInput = document.getElementById(parcelasInputId);
    const recorrenciaSelect = document.getElementById(recorrenciaSelectId);

    if (!parcelasInput || !recorrenciaSelect) return;

    // Quando número de parcelas muda
    parcelasInput.addEventListener("input", function () {
      const parcelas = parseInt(parcelasInput.value);

      if (parcelas > 1) {
        recorrenciaSelect.value = "Sem recorrencia";
        recorrenciaSelect.disabled = true;
      } else {
        recorrenciaSelect.disabled = false;
      }
    });

    // Quando recorrência muda
    recorrenciaSelect.addEventListener("change", function () {
      if (recorrenciaSelect.value !== "Sem recorrencia") {
        parcelasInput.value = 1;
        parcelasInput.disabled = true;
      } else {
        parcelasInput.disabled = false;
      }
    });
  }

  // Aplicar nos dois modais
  configurarBloqueios("parcelas-receita", "recorrencia-receita");
  configurarBloqueios("parcelas-despesa", "recorrencia-despesa");

});
