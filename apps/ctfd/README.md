# qctf CTFd integration

Builds the checked-in upstream CTFd 3.8.7 source with qctf plugins. Startup waits for the database,
runs migrations, bootstraps a preset development administrator idempotently,
and starts Gunicorn. React in `apps/web` is the only product UI. The vendored
backend has no CTFd page controllers, themes, forms, template loaders, plugin
HTML/JS assets, UI extension hooks, or social-share page renderer. Flask,
CTFd domain models, JSON APIs, protected file downloads, migrations and
backend plugins remain. API challenge/flag responses contain data only.

Bootstrap sets defaults only when setup is incomplete, refuses to promote an
existing non-admin email, and does not overwrite configured competition data.
All credentials come from ignored runtime `.env` values. Test first-run
behavior with `make test-bootstrap`, which uses a disposable SQLite container
without changing the running MariaDB. The same probe verifies the real app
route map, JSON errors, challenge/flag CRUD, file upload/download, solves,
scoreboard and statistics using disposable fixtures. MariaDB remains the supported dev store.
See `UPSTREAM.md` for the source provenance and customization workflow.

## Python dependencies

Manage Python packages in `upstream/pyproject.toml` with uv 0.11.32 and Python
3.11. Commit `upstream/uv.lock` with dependency changes; this generated TOML
lockfile pins the complete resolution. Docker installs runtime dependencies
with `uv sync --locked --no-dev` and fails if the lockfile is stale.

From `apps/ctfd/upstream`:

```sh
uv sync --locked                  # Runtime and development dependencies
uv sync --locked --group lint     # Include lint tools
uv add 'package==version'         # Add a runtime dependency
uv add --dev 'package==version'   # Add a development dependency
uv lock                          # Refresh the lock after manual TOML edits
uv run --locked python serve.py
```

The migration retains existing runtime pins in `constraint-dependencies`.
When upgrading a constrained package, update or remove its constraint too.
The old requirements, development, linting and pip-compile files are replaced
by the TOML manifest and lockfile. Frontend npm and orchestrator Go manifests
continue to use their ecosystem formats.
