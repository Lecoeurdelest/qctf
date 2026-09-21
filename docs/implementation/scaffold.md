# Runnable scaffold implementation boundary

## TASK-006 scope

This increment adds runnable source and local integration to the earlier
document-only scaffold. Architecture choices and namespace changes are recorded
in `plan.md`; original REQ/TASK IDs are preserved in `project.yaml`.

Implemented: React shell and real API reads, in-memory token entry, token-based
qctf identity/role guards, JSON-only CTFd boundary, internal Go HTTP service,
disabled instance/KoTH operations, Docker Compose and real CI configuration.
Core CTFd code is not forked. The new backend baseline is upstream 3.8.7;
legacy behavior parity is not assumed.

## Verification and evidence

`make verify` records actual stdout/stderr, exit codes, tool versions, local
image IDs and SHA-256 source inputs under `.project/evidence/TASK-006/<run>/`.
It rebuilds the stack before integration checks to avoid testing stale images.
The snapshot includes lockfiles and uncommitted source, excluding secrets,
generated build output and execution evidence. Input changes during a run fail
the report. Runtime secrets/database state are not a complete reproducible
production snapshot; no calibrated logic confidence is claimed.

Checks cover frontend API token format/redirect handling, Go service auth and
readiness, plugin team/role/ban guards, JSON errors, fresh/repeated bootstrap,
gateway routing, original CTFd challenge/score APIs and live runtime inspection.
The fresh bootstrap probe runs in a disposable SQLite container and does not
replace the MariaDB integration checks. No mock competition data is inserted.

Observed defects and repairs are preserved in the two `initial-*-failure.md`
records: bootstrap missing request IP, and upstream invalid-token HTML errors.
Manual review is recorded separately from runner results; local test success
does not mean CI has executed remotely.

## Pending product obligations

- TASK-001: complete end-user auth/team/admin/solve flows and full upstream
  authorization/legacy compatibility review.
- TASK-002: durable instance schema/outbox, trusted event selection, restart
  recovery and an actual reconciler. Current endpoints return 501.
- TASK-003: vetted kCTF toolchain/template import, real CRD/healthcheck tests and
  managed exposure. The original kCTF source remains in the legacy sibling.
- TASK-004: proof policy, transactional claims, ownership intervals, a durable
  tick scheduler and exactly-once Award effect. All game functionality disabled.
- TASK-005: cluster isolation, RBAC, resource limits, secret lifecycle,
  observability, migration and release checks. Docker networking is not proof
  of Kubernetes security.

No production cluster, public endpoint, git remote, PR, migration, scheduler or
background automation is created. Locally started Compose resources belong
only to project `qctf`; `make down` preserves its data volumes.
