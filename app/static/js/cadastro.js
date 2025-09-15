document.getElementById("cadastroForm").addEventListener("submit", function(event) {
    event.preventDefault();
    
    // Captura os valores dos campos
    let nome = document.getElementById("nome").value.trim();
    let email = document.getElementById("email").value.trim();
    let senha = document.getElementById("senha").value.trim();

    // Verifica se todos os campos foram preenchidos
    if (nome && email && senha) {
        alert("Cadastro realizado com sucesso!");
        
        // Envia o formulário manualmente após validação
        event.target.submit(); 
    } else {
        alert("Preencha todos os campos!");
    }
});
