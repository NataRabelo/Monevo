document.addEventListener("DOMContentLoaded", () => {
  const btnSelecionar = document.getElementById("btnSelecionar");
  const inputArquivo = document.getElementById("inputArquivo");

  btnSelecionar.addEventListener("click", () => {
    inputArquivo.click(); // abre o Windows Explorer
  });

  // quando o usuário selecionar o arquivo
  inputArquivo.addEventListener("change", () => {
    if (inputArquivo.files.length > 0) {
      alert("Arquivo selecionado: " + inputArquivo.files[0].name);
    }
  });
  
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
