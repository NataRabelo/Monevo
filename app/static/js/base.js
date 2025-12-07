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


const flashMessages = document.querySelectorAll('.flash-message');

flashMessages.forEach(msg => {
    setTimeout(() => {
        msg.classList.add('fade-out');
    }, 3000);

    msg.addEventListener('transitionend', () => {
        msg.remove();
    });
});


document.addEventListener("DOMContentLoaded", aplicarMascaraMoeda);
