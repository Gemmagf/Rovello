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
