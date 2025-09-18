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
});
