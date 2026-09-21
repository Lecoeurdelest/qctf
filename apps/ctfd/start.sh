#!/bin/sh
set -eu
python ping.py
flask db upgrade
python /opt/qctf/bootstrap.py
exec gunicorn 'CTFd:create_app()' --bind 0.0.0.0:8000 --workers 1 --worker-class gevent --access-logfile - --error-logfile -

