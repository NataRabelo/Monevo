document.addEventListener("DOMContentLoaded", () => {
  // ----------------- FLASH MESSAGES -----------------
  const flashMessages = document.querySelectorAll('.flash-message');
  if (flashMessages.length > 0) {
    setTimeout(() => {
      flashMessages.forEach(msg => {
        msg.style.transition = "opacity 0.5s ease";
        msg.style.opacity = "0";
        setTimeout(() => msg.remove(), 500);
      });
    }, 3000);
  }

  // ----------------- FORMULÁRIO CONTA -----------------
  const botaoCadastrarConta = document.getElementById("botao_cadastrar_conta");
  const formularioConta = document.getElementById("formulario_conta");
  const botaoCancelarConta = document.getElementById("botao_cancelar_conta");

  botaoCadastrarConta.onclick = () => {
    formularioConta.classList.remove("d-none");
    formConta.reset();
    tituloFormConta.innerText = "Nova conta bancária";
    formConta.action = "{{ url_for('conta.cadastrarConta') }}";
  };

  botaoCancelarConta.onclick = () => formularioConta.classList.add("d-none");

  document.querySelectorAll(".botao-editar-conta").forEach(botao => {
    botao.onclick = () => {
      formularioConta.classList.remove("d-none");
      tituloFormConta.innerText = "Editar conta bancária";
      formConta.action = `/contas/editar/${botao.dataset.id}`;
      document.getElementById("nome_banco").value = botao.dataset.banco;
      document.getElementById("saldo_inicial").value = botao.dataset.saldo;
    };
  });

  // ----------------- FORMULÁRIO CARTÃO -----------------
  const botaoCadastrarCartao = document.getElementById("botao_cadastrar_cartao");
  const formularioCartao = document.getElementById("formulario_cartao");
  const botaoCancelarCartao = document.getElementById("botao_cancelar_cartao");

  botaoCadastrarCartao.onclick = () => {
    formularioCartao.classList.remove("d-none");
    formCartao.reset();
    tituloFormCartao.innerText = "Novo cartão de crédito";
    formCartao.action = "{{ url_for('cartao.cadastrar_cartao') }}";
  };

  botaoCancelarCartao.onclick = () => formularioCartao.classList.add("d-none");

  // ----------------- MODAL EDITAR CARTÃO -----------------
  document.querySelectorAll(".botao-editar-cartao").forEach(botao => {
    botao.addEventListener("click", () => {
      const id = botao.dataset.id;
      const credito = botao.dataset.credito;
      const conta = botao.dataset.conta;

      // Preenche os campos do modal
      document.getElementById("editar_cartao_id").value = id;
      document.getElementById("editar_credito_cartao").value = credito;
      document.getElementById("editar_conta_relacionada").value = conta;

      // Ajusta o action do form do modal
      document.getElementById("formEditarCartao").action = `/cartoes/editar/${id}`;

      // Mostra o modal usando Bootstrap
      const modal = new bootstrap.Modal(document.getElementById("modalEditarCartao"));
      modal.show();
    });
  });
});
