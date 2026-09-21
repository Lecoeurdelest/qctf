# qctf CTFd integration

Builds the checked-in upstream CTFd 3.8.7 source with qctf plugins. Startup waits for the database,
runs migrations, bootstraps a preset development administrator idempotently,
and starts Gunicorn. CTFd/Flask is retained; its rendered UI is disabled by
the plugin and is never the gateway's product UI.

Bootstrap sets defaults only when setup is incomplete, refuses to promote an
existing non-admin email, and does not overwrite configured competition data.
All credentials come from ignored runtime `.env` values. Test first-run
behavior with `make test-bootstrap`, which uses a disposable SQLite container
without changing the running MariaDB. MariaDB remains the supported dev store.
See `UPSTREAM.md` for the source provenance and customization workflow.
