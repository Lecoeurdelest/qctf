# Initial local integration failure

The first `docker compose up --build -d --wait` exited 1. CTFd migrations
completed, then preset-admin creation failed while logging from a synthetic
request without a remote address. The admin transaction had already committed;
no database reset was needed.

Observed traceback excerpt:

```text
File "/opt/qctf/bootstrap.py", line 9, in bootstrap
    if generate_preset_admin() is None:
File "/opt/CTFd/CTFd/utils/security/auth.py", line 60, in generate_preset_admin
    log(
File "/opt/CTFd/CTFd/utils/logging/__init__.py", line 15, in log
    "ip": get_ip(),
File "/opt/CTFd/CTFd/utils/user/__init__.py", line 241, in get_ip
    if not re.match(combined, addr):
TypeError: expected string or bytes-like object, got 'NoneType'
```

Repair: set REMOTE_ADDR=127.0.0.1 in the bootstrap-only request context.
Fresh-database bootstrap needs a separate regression check; restarting the
partially initialized database alone does not cover the first-creation path.

The first fresh-database probe subsequently reached both successful bootstrap
calls but failed its own `get_config("setup") is True` assertion. A direct
read against the running CTFd reported `SETUP_TYPE int 1`: CTFd persists the
setting as integer 1, not a Python boolean singleton. The assertion was
corrected to `== 1` without changing bootstrap behavior or acceptance criteria.
