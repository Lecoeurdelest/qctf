# TASK-006 implementation record — runnable scaffold

## Result

The qctf sibling project now contains a runnable React/Vite UI, checked-in and
locally built upstream CTFd 3.8.7 with qctf headless/KoTH plugins, a Go orchestrator boundary, local
MariaDB/Redis/Compose wiring, CI and bounded tests. The browser and gateway do
not expose CTFd's product UI. The scaffold intentionally reports instance and
KoTH mutations as 501 until their durable contracts are implemented.

## Criteria

- AC-011: pass — TypeScript/Vite build, Node API-client tests, Go race tests and
  `go vet` passed in the recorded run.
- AC-012: pass — Compose boot, plugin tests, disposable SQLite bootstrap and 13
  gateway/API smoke checks passed.
- AC-013: pass — manual review confirms routes, contracts, README, pending
  work, source ownership and evidence scope are explicit.

This completion is scoped to REQ-006 scaffold criteria. It does not pass or
complete the critical domain gates REQ-001 through REQ-005. Calibrated logic
confidence is `null`; no calibrated evaluator was available or claimed.

## Evidence and deviations

Primary runner evidence: `.project/evidence/TASK-006/` (the exact current report
path is recorded in `.project/state.json`).
The two initial failures and repairs are retained beside that run. A skill
refresh changes planning policy and therefore requires a new verification run;
the previous report must not be reused as fresh evidence until regenerated.

Known gaps: no Kubernetes cluster or workload, no instance persistence/outbox,
no KoTH proof/ownership/tick/Award ledger, no complete user/team/auth flows,
no legacy migration or production security certification.

## Changed areas

`apps/web`, `apps/ctfd`, `plugins/ctfd-headless`, `plugins/ctfd-koth`,
`services/orchestrator`, `infra/gateway`, `compose.yaml`, `scripts`, tests,
technical contracts, CI and plan-driven artifacts. No file in the sibling
`F-CTF_Platform-master` project was modified by this refresh.
