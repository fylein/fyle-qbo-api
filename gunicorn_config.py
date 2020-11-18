import os

# https://docs.gunicorn.org/en/stable/settings.html


backlog = int(os.environ.get('GUNICORN_BACKLOG', 2048))
workers = int(os.environ.get('GUNICORN_NUMBER_WORKERS', 1))
timeout = int(os.environ.get('GUNICORN_WORKER_TIMEOUT', 1500))
keepalive = int(os.environ.get('GUNICORN_KEEPALIVE', 2))

loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')
worker_class = os.environ.get('GUNICORN_WORKER_CLASS', 'sync')

limit_request_line = 0

spew = False

daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

errorlog = '-'
accesslog = '-'
access_log_format = '%({X-Real-IP}i)s - - - %(t)s.%(T)s "%(r)s" "%(f)s" "%(a)s" %({X-Request-Id}i)s %(L)s %(b)s %(s)s'
