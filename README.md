# qctf

Runnable development scaffold for a React-only CTF platform backed by CTFd,
with a Go control plane and planned kCTF/KoTH integration. No C# code is used.
The sibling legacy project is unchanged by this increment.

## Start locally

Requires Docker with Compose v2 and Node.js 24+. First startup downloads images.

```sh
cd /Users/quyn28654/Documents/personal/qctf
make dev
```

Open http://localhost:8088. `make env` creates an ignored, mode-0600 `.env`
with random local credentials; existing files are never overwritten. Use
`QCTF_ADMIN_TOKEN` from that file in **Connect account**. The token is kept in
browser memory only and is lost on reload. Do not distribute this admin token.
Self-service login, registration, team management and password reset are pending.

Only the gateway is published, on loopback. CTFd, MariaDB, Redis and the Go
service have no published host ports. `make down` stops this project's stack
without deleting database or upload volumes. `make logs` follows service logs.
Change `QCTF_PORT` in `.env` if 8088 is occupied. Never use this Compose file as
a public production deployment.

## Available now

- React routes: overview, challenges, scoreboard, KoTH status, control center,
  and development token access. Challenge/score lists use the real CTFd API.
- CTFd 3.8.7 + Flask source is checked into `apps/ctfd/upstream/` and built
  locally, so core behavior can be customized. Original rendered UI routes
  are disabled; React handles product routes.
- Server-derived user/team identity and admin-only runtime inspection.
- Internal Go HTTP service with liveness, explicit non-readiness, and service
  authentication. No Kubernetes client, workload, or cluster credentials yet.
- KoTH plugin namespace and disabled capability endpoints. Arena/claim writes
  return 501; no ownership, claims, ticks or Awards are fabricated.
- Persistent MariaDB, Redis cache, generated local secrets, tests and CI jobs.

## Architecture

```text
Browser → gateway → React static assets
                 → /api/v1/*       → CTFd core → MariaDB / Redis
                 → /api/qctf/v1/*  → qctf plugins
                                      └→ internal Go orchestrator
                                          └→ kCTF / Kubernetes [pending]
KoTH: shared arena + ownership/award ledger [pending], not one arena per team.
```

## Development and verification

```sh
make check          # Go race tests/vet + frontend tests/build; Go 1.26+ required
make test-plugins   # Run plugin tests inside the running CTFd container
make test-bootstrap # Bootstrap twice in a fresh temporary SQLite container
make smoke          # Check the live gateway/API stack without seeding data
make sync           # Regenerate task index/manifest and validate plan preservation
make verify         # Record real logs and a source snapshot under .project/evidence
```

For frontend hot reload, start the Compose stack, then run `npm ci` and
`npm run dev` in `apps/web`. Vite proxies API requests to port 8088; update
`vite.config.ts` if you change that port. Runtime code changes require
`make dev` to rebuild images. CI uses the same checks; its remote run is not
claimed until the repository is published and a workflow actually executes.

## Next implementation slices

1. Complete React account/team/admin flows and CTFd challenge solving UI.
2. Add durable instance records, uniqueness, outbox/reconciliation and TeamId checks.
3. Integrate kCTF Challenge CRs, image digests, healthchecks and managed exposure.
4. Add KoTH trusted proof verification, transactional ownership and idempotent Awards.
5. Verify cluster isolation, quotas, audit/metrics, migration parity and production auth.

See `plan.md`, `project.yaml`, `.project/state.json`, `docs/technical/`, and
`docs/task/README.md`, `docs/implementation/`. Passing scaffold checks do not close the
critical product requirements REQ-001 through REQ-005.
