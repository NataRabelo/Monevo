// -------------------------------------------------------------
// Aplica máscara de moeda (R$) em todos os inputs com classe .currency.
// A cada digitação, mantém somente números, converte para centavos
// e formata automaticamente no padrão brasileiro.
// -------------------------------------------------------------
function aplicarMascaraMoeda() {
    const inputs = document.querySelectorAll(".currency");

    inputs.forEach(input => {
        input.addEventListener("input", function () {
            let value = this.value;

            value = value.replace(/\D/g, "");

            if (!value) {
                this.value = "";
                return;
            }

            const numericValue = (parseInt(value) / 100).toFixed(2);

            this.value = new Intl.NumberFormat("pt-BR", {
                style: "currency",
                currency: "BRL"
            }).format(numericValue);
        });
    });
}


// -------------------------------------------------------------
// Controla mensagens flash na tela:
// - adiciona efeito de fade-out após 3s
// - remove o elemento do DOM quando a transição termina
// -------------------------------------------------------------
const flashMessages = document.querySelectorAll('.flash-message');

flashMessages.forEach(msg => {
    setTimeout(() => {
        msg.classList.add('fade-out');
    }, 3000);

    msg.addEventListener('transitionend', () => {
        msg.remove();
    });
});


// -------------------------------------------------------------
// Inicializa a máscara de moeda quando o DOM estiver carregado
// -------------------------------------------------------------
document.addEventListener("DOMContentLoaded", aplicarMascaraMoeda);
