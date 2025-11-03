// static/js/cadastro.js
document.addEventListener('DOMContentLoaded', function () {
  // Seletores (ajustados para serem específicos)
  const form = document.querySelector('form.formulario-cadastro') || document.querySelector('form');
  const campoCpf = document.getElementById('campo-cpf');

  if (!form || !campoCpf) {
    console.warn('Form ou campo CPF não encontrado — verifique os IDs/classes no HTML.');
    return;
  }

  // Função de validação do CPF (aceita com ou sem máscara)
  function validarCPF(cpf) {
    if (!cpf) return false;
    const cpfLimpo = cpf.replace(/\D/g, '');
    if (cpfLimpo.length !== 11) return false;
    if (/^(\d)\1{10}$/.test(cpfLimpo)) return false;

    const nums = cpfLimpo.split('').map(d => parseInt(d, 10));

    // Primeiro dígito
    let soma = 0;
    for (let i = 0; i < 9; i++) soma += nums[i] * (10 - i);
    let resto = soma % 11;
    let dig1 = resto < 2 ? 0 : 11 - resto;
    if (nums[9] !== dig1) return false;

    // Segundo dígito
    soma = 0;
    for (let i = 0; i < 10; i++) soma += nums[i] * (11 - i);
    resto = soma % 11;
    let dig2 = resto < 2 ? 0 : 11 - resto;
    if (nums[10] !== dig2) return false;

    return true;
  }

  // Cria/obtém elemento de erro
  function getErroElem() {
    let aviso = campoCpf.parentElement.querySelector('#erro-cpf');
    if (!aviso) {
      aviso = document.createElement('div');
      aviso.id = 'erro-cpf';
      aviso.style.color = 'red';
      aviso.style.fontSize = '0.9rem';
      aviso.style.marginTop = '4px';
      aviso.style.fontWeight = '500';
      // adiciona depois do input-group (mantém layout do bootstrap)
      campoCpf.parentElement.appendChild(aviso);
    }
    return aviso;
  }

  function mostrarErro(mensagem) {
    const aviso = getErroElem();
    aviso.textContent = mensagem || '';
  }

  // Formatação automática do CPF enquanto digita (opcional, melhora UX)
  campoCpf.addEventListener('input', function (e) {
    const apenasDigitos = this.value.replace(/\D/g, '').slice(0, 11); // limita a 11 dígitos
    let formatted = apenasDigitos;
    if (apenasDigitos.length > 9) {
      formatted = apenasDigitos.replace(/(\d{3})(\d{3})(\d{3})(\d{1,2})/, '$1.$2.$3-$4');
    } else if (apenasDigitos.length > 6) {
      formatted = apenasDigitos.replace(/(\d{3})(\d{3})(\d{1,3})/, '$1.$2.$3');
    } else if (apenasDigitos.length > 3) {
      formatted = apenasDigitos.replace(/(\d{3})(\d{1,3})/, '$1.$2');
    }
    // preserva cursor simples: substitui valor formatado
    this.value = formatted;
    // limpa mensagem enquanto digita
    if (formatted.length < 14) mostrarErro(''); // 14 quando com máscara completa
  });

  // Valida ao perder o foco (blur)
  campoCpf.addEventListener('blur', function () {
    const value = this.value.trim();
    if (value === '') {
      mostrarErro('');
      return;
    }
    if (!validarCPF(value)) mostrarErro('CPF inválido ❌');
    else mostrarErro('');
  });

  // Impede envio do form se CPF inválido
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

  // === Ajuste sugerido no HTML ===
  // Garanta que no seu HTML o campo CPF tenha maxlength="14" (máscara) ou remova o maxlength:
  // <input ... id="campo-cpf" maxlength="14" placeholder="000.000.000-00" ...>
});
