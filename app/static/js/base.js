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
document.addEventListener("DOMContentLoaded", aplicarMascaraMoeda);
