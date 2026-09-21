# qctf

Headless CTF platform with a React UI, CTFd backend, and Go orchestrator.
kCTF runtime and KoTH gameplay are planned; the project is currently a development scaffold.

## Run locally

Requires Docker with Compose v2 and Node.js 24+.

```sh
make dev
```

Open http://localhost:8088. Startup creates `.env` with local credentials.
Use its `QCTF_ADMIN_TOKEN` in **Connect account**; the token clears on reload.
Keep it private. Change `QCTF_PORT` in `.env` to use another port.
This stack is for local development only.

## Status

- React challenge and scoreboard pages use the CTFd API.
- CTFd source lives in `apps/ctfd/upstream`; React replaces its original UI.
- Go orchestrator provides authenticated diagnostics; instance creation is not implemented.
- kCTF integration, KoTH gameplay, and account/team management flows are pending.

## Development

```sh
make down           # Stop containers, keep data
make logs           # Follow logs
make check          # Go tests/vet + frontend checks (Go 1.26+)
make test-plugins   # Plugin tests; requires running CTFd
make test-bootstrap # Check bootstrap idempotency
make smoke          # Check the running stack
make sync           # Refresh planning indexes
make verify         # Record verification evidence
```

For frontend hot reload, run `npm ci && npm run dev` in `apps/web` with the
stack running. Vite proxies APIs to port 8088. Run `make dev` to rebuild containers.

See [project.yaml](project.yaml) for the plan, [tasks](docs/task/README.md)
for progress, and [technical docs](docs/technical/) for architecture.
