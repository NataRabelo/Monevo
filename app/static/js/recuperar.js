// Aguarda o carregamento completo do DOM
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("recuperacao-form");

    // Validação ao enviar o formulário
    form.addEventListener("submit", function (event) {
        const email = document.getElementById("email").value;

        // Verificação básica de email
        if (!email.includes("@")) {
            event.preventDefault(); // Impede envio do formulário
            alert("Por favor, insira um email válido.");
        }
    });
});
