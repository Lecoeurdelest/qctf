# qctf platform plan

## Goal

Build a headless CTF platform that retains CTFd's user, team, challenge,
submission, solve, award, and scoreboard domain while replacing its rendered UI
with React. Retain kCTF for challenge builds and sandboxed execution. Add
durable team-scoped instances and a KoTH mode with shared arenas, proof claims,
ownership history, and periodic CTFd Awards.

## Architecture decisions

- React is the only product-facing UI.
- CTFd/Flask remains the domain and REST backend.
- qctf-specific APIs live under `/api/qctf/v1`; upstream APIs remain `/api/v1`.
- kCTF remains the challenge build/runtime substrate.
- An orchestrator and reconciler own Kubernetes lifecycle.
- Go is the orchestrator implementation language. This resolves the earlier
  open choice using the discussed replacement architecture; no C# is imported.
- MariaDB is the initial durable store, matching the retained CTFd stack.
  PostgreSQL is not a second supported database in this increment.
- CTFd 3.8.7 is checked into `apps/ctfd/upstream` and built locally so core
  Flask behavior can be customized and reviewed; the source tag is pinned.

## Invariants

- Team identity comes from the authenticated CTFd token, never from trusted
  client input.
- Normal instance identity is `(event_id, challenge_id, team_id)`.
- KoTH claim transitions are serialized and score ticks are idempotent.
- Durable business state lives in MariaDB; Redis is cache, queue,
  and lock infrastructure.
- Challenge workloads cannot access CTFd data stores or orchestrator secrets.
- No future evidence is marked passing without an actual check.

## Delivery slices

1. Freeze the headless API boundary and React routing.
2. Define durable instance state and the orchestrator contract.
3. Preserve kCTF templates and managed web/pwn exposure.
4. Implement the KoTH plugin, shared arena, proof verification, and Awards.
5. Add reconciler, security policy, observability, and migration gates.

## Non-goals for the first increment

- Rewriting CTFd's score aggregation.
- Multi-cluster scheduling.
- Production deployment to a public domain.
- Deleting legacy code before contract parity is demonstrated.

## Runnable scaffold increment

The user authorized continuing initialization in the sibling `qctf` directory.
Deliver a locally runnable React/Vite/TypeScript UI, headless CTFd plugins,
Go service, MariaDB/Redis development stack, tests, CI configuration, and
updated plan-driven records. This work is TASK-006, independent of completing
the production behavior gates of TASK-001 through TASK-005.

Use upstream CTFd 3.8.7 as the new backend baseline instead of copying the
modified legacy 3.7.3 tree. The source is checked into qctf and built locally
for customization. Legacy custom behavior and data migration require explicit
parity work before cutover. Retain Flask and upstream UI files as internal
source dependencies, but block all CTFd-rendered product routes.
React owns contestant and admin product surfaces. Token entry is a temporary
local-development access flow, not completed end-user authentication.

The `/api/fctf/v1` namespace in the initial document-only scaffold is replaced
before release by `/api/qctf/v1`. No compatibility alias or data migration is
needed for that unimplemented document contract; legacy consumers are not
automatically migrated.

Do not connect to Kubernetes or deploy challenge containers in this increment.
Preserve kCTF as the intended runtime and record the legacy template source.
Unimplemented instance and KoTH writes must fail explicitly. Scaffold success
means build, startup, bounded smoke checks, and manual review, not proof of
runtime isolation, concurrency correctness, production readiness, or migration.
