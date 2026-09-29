# Config de gunicorn — es carrega automàticament perquè el start command fa
# `cd backend && gunicorn ...` i gunicorn busca ./gunicorn.conf.py per defecte.
#
# El primer /predict pot trigar >30 s (descàrrega del model + càrrega de torch),
# així que pugem el timeout per evitar que gunicorn mati el worker.
workers = 1
threads = 2            # gthread: /health respon mentre un /predict s'executa
timeout = 300
graceful_timeout = 60
keepalive = 5


def post_worker_init(worker):
    """Arrenca l'escalfament del model DINS del worker, un cop l'app ja està
    carregada (funciona igual amb i sense --preload; en cap cas al master).

    Nota macOS: numpy hi usa Accelerate/GCD, que no és fork-safe; per
    desenvolupar en local fes servir gunicorn SENSE --preload.
    """
    try:
        import server as app_module  # ja és a sys.modules: gunicorn acaba de carregar server:app
        if app_module.start_warmup():
            worker.log.info("Warmup del model iniciat al worker pid %s", worker.pid)
    except Exception as e:  # mai bloquejar l'arrencada del worker
        worker.log.warning("No s'ha pogut iniciar el warmup: %r", e)
