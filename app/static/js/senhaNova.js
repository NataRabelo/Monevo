  /* =============================
     Flash Message Fade Out
  ============================= */
const flashMessages = document.querySelectorAll('.flash-message');

flashMessages.forEach(msg => {
    setTimeout(() => {
        msg.classList.add('fade-out');
    }, 3000);

    msg.addEventListener('transitionend', () => {
        msg.remove();
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const campoSenha = document.getElementById("campo-senha");
    const campoConfirmacao = document.getElementById("campo-senha-confirmacao");
    const form = document.getElementById("formulario-nova-senha");

    // Mensagem de validação
    const msg = document.createElement("div");
    msg.style.color = "red";
    msg.style.marginTop = "5px";
    msg.style.fontSize = "14px";
    campoSenha.closest(".nova-senha").appendChild(msg);

    function validarSenha(senha) {
        const regras = [
            { teste: /.{8,}/, msg: "• mínimo 8 caracteres" },
            { teste: /[a-z]/, msg: "• pelo menos 1 letra minúscula" },
            { teste: /[A-Z]/, msg: "• pelo menos 1 letra maiúscula" },
            { teste: /[^A-Za-z0-9]/, msg: "• pelo menos 1 caractere especial" }
        ];

        const faltando = regras.filter(r => !r.teste.test(senha));

        if (faltando.length === 0) {
            return "";
        }

        return "A senha deve conter:<br>" + faltando.map(f => f.msg).join("<br>");
    }

    function validarConfirmacao(senha, confirmacao) {
        if (confirmacao.trim() !== "" && senha !== confirmacao) {
            return "• A confirmação da senha não corresponde";
        }
        return "";
    }

    function atualizarMensagem() {
        const mensagemSenha = validarSenha(campoSenha.value);
        const mensagemConfirmacao = validarConfirmacao(campoSenha.value, campoConfirmacao.value);

        const mensagens = [];
        if (mensagemSenha) mensagens.push(mensagemSenha);
        if (mensagemConfirmacao) mensagens.push(mensagemConfirmacao);

        msg.innerHTML = mensagens.join("<br>");
    }

    campoSenha.addEventListener("input", atualizarMensagem);
    campoConfirmacao.addEventListener("input", atualizarMensagem);

    form.addEventListener("submit", (e) => {
        atualizarMensagem();
        if (msg.innerHTML !== "") {
            e.preventDefault();
            alert("Corrija os erros antes de continuar.");
        }
    });
});
