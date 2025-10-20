document.addEventListener("DOMContentLoaded", function () {
  const formularioConta = document.getElementById("formulario_conta");
  const botaoCadastrarConta = document.getElementById("botao_cadastrar_conta");
  const botaoCancelarConta = document.getElementById("botao_cancelar_conta");

  const formularioCartao = document.getElementById("formulario_cartao");
  const botaoCadastrarCartao = document.getElementById("botao_cadastrar_cartao");
  const botaoCancelarCartao = document.getElementById("botao_cancelar_cartao");

  // Mostrar/ocultar formulário de conta
  if (botaoCadastrarConta && formularioConta) {
    botaoCadastrarConta.addEventListener("click", () => {
      formularioConta.classList.remove("d-none");
    });
  }
  if (botaoCancelarConta && formularioConta) {
    botaoCancelarConta.addEventListener("click", () => {
      formularioConta.classList.add("d-none");
    });
  }

  // Mostrar/ocultar formulário de cartão
  if (botaoCadastrarCartao && formularioCartao) {
    botaoCadastrarCartao.addEventListener("click", () => {
      formularioCartao.classList.remove("d-none");
    });
  }
  if (botaoCancelarCartao && formularioCartao) {
    botaoCancelarCartao.addEventListener("click", () => {
      formularioCartao.classList.add("d-none");
    });
  }

    let flashMessages = document.querySelectorAll('.flash-message');
        if (flashMessages.length > 0) {
            setTimeout(() => {
                flashMessages.forEach(msg => {
                    msg.style.transition = "opacity 0.5s ease";
                    msg.style.opacity = "0";
                    setTimeout(() => msg.remove(), 500);
                });
            }, 3000);
        }
        
});
