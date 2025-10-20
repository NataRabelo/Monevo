document.addEventListener("DOMContentLoaded", function () {
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