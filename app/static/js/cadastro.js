// -------------------------------------------------------------
// Responsável por: validação e formatação automática do CPF no
// formulário de cadastro, incluindo feedback visual, máscara
// dinâmica e bloqueio de envio se inválido.
// -------------------------------------------------------------
document.addEventListener('DOMContentLoaded', function () {

  // -----------------------------------------------------------
  // Seleção de elementos essenciais (formulário e campo CPF)
  // -----------------------------------------------------------
  const form = document.querySelector('form.formulario-cadastro') || document.querySelector('form');
  const campoCpf = document.getElementById('campo-cpf');

  if (!form || !campoCpf) {
    console.warn('Form ou campo CPF não encontrado — verifique os IDs/classes no HTML.');
    return;
  }

  // -----------------------------------------------------------
  // Validação de CPF (aceita com ou sem máscara)
  // Verifica tamanho, repetições e dígitos verificadores
  // -----------------------------------------------------------
  function validarCPF(cpf) {
    if (!cpf) return false;

    const cpfLimpo = cpf.replace(/\D/g, '');
    if (cpfLimpo.length !== 11) return false;
    if (/^(\d)\1{10}$/.test(cpfLimpo)) return false;

    const nums = cpfLimpo.split('').map(d => parseInt(d, 10));

    // Primeiro dígito verificador
    let soma = 0;
    for (let i = 0; i < 9; i++) soma += nums[i] * (10 - i);
    let resto = soma % 11;
    let dig1 = resto < 2 ? 0 : 11 - resto;
    if (nums[9] !== dig1) return false;

    // Segundo dígito verificador
    soma = 0;
    for (let i = 0; i < 10; i++) soma += nums[i] * (11 - i);
    resto = soma % 11;
    let dig2 = resto < 2 ? 0 : 11 - resto;
    if (nums[10] !== dig2) return false;

    return true;
  }

  // -----------------------------------------------------------
  // Cria ou obtém o elemento que exibirá mensagens de erro
  // (posicionado logo abaixo do campo CPF)
  // -----------------------------------------------------------
  function getErroElem() {
    let aviso = campoCpf.parentElement.querySelector('#erro-cpf');
    if (!aviso) {
      aviso = document.createElement('div');
      aviso.id = 'erro-cpf';
      aviso.style.color = 'red';
      aviso.style.fontSize = '0.9rem';
      aviso.style.marginTop = '4px';
      aviso.style.fontWeight = '500';
      campoCpf.parentElement.appendChild(aviso);
    }
    return aviso;
  }

  function mostrarErro(mensagem) {
    const aviso = getErroElem();
    aviso.textContent = mensagem || '';
  }

  // -----------------------------------------------------------
  // Máscara dinâmica de CPF conforme o usuário digita
  // Inclui limpeza, limite de caracteres e formatação
  // -----------------------------------------------------------
  campoCpf.addEventListener('input', function () {
    const apenasDigitos = this.value.replace(/\D/g, '').slice(0, 11);
    let formatted = apenasDigitos;

    if (apenasDigitos.length > 9) {
      formatted = apenasDigitos.replace(/(\d{3})(\d{3})(\d{3})(\d{1,2})/, '$1.$2.$3-$4');
    } 
    else if (apenasDigitos.length > 6) {
      formatted = apenasDigitos.replace(/(\d{3})(\d{3})(\d{1,3})/, '$1.$2.$3');
    } 
    else if (apenasDigitos.length > 3) {
      formatted = apenasDigitos.replace(/(\d{3})(\d{1,3})/, '$1.$2');
    }

    this.value = formatted;

    if (formatted.length < 14) mostrarErro('');
  });

  // -----------------------------------------------------------
  // Validação ao perder o foco (blur)
  // Mostra mensagem apenas quando o CPF está completo e inválido
  // -----------------------------------------------------------
  campoCpf.addEventListener('blur', function () {
    const value = this.value.trim();

    if (value === '') {
      mostrarErro('');
      return;
    }

    if (!validarCPF(value)) mostrarErro('CPF inválido ❌');
    else mostrarErro('');
  });

  // -----------------------------------------------------------
  // Impede envio caso o CPF seja inválido
  // -----------------------------------------------------------
  form.addEventListener('submit', function (e) {
    const cpf = campoCpf.value.trim();

    if (!validarCPF(cpf)) {
      e.preventDefault();
      mostrarErro('CPF inválido. Corrija antes de enviar ❌');
      campoCpf.focus();
    } else {
      mostrarErro('');
    }
  });
});
