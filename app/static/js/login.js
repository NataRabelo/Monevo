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
