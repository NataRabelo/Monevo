from flask import current_app

def registrar_requisicao(req, status_code: int, mensagem: str = ""):
    ip = req.remote_addr
    metodo = req.method
    caminho = req.path
    current_app.logger.info(f"{ip} {metodo} {caminho} -> {status_code} {mensagem}")