# Challenge instance contract

Normal instances are keyed by `(event_id, challenge_id, team_id)`. The client
does not provide an authoritative TeamId. The durable state machine is:

```text
PENDING -> STARTING -> RUNNING -> STOPPING -> STOPPED
                    \-> FAILED
RUNNING -> EXPIRED -> STOPPING
```

The contract must include immutable challenge version/image digest, resource
identity, endpoint, expiry, and observed Kubernetes state.

## Current implementation boundary

The Go service exposes `GET /healthz` (200) and `GET /readyz` (503 until a
real kCTF adapter exists). `GET /internal/v1/runtime` requires a distinct
service Bearer token; `POST /internal/v1/instances` authenticates then returns
501. There is no database, queue, timer, Kubernetes client or in-memory fake
instance store in this service yet.

## Required next design slice

CTFd owns authorization and the durable desired-state record. The Go
reconciler owns observed Kubernetes state, not the identity source of truth.
MariaDB must enforce uniqueness on `(event_id, challenge_id, team_id)` for
ordinary instances; define retry/restart semantics and generation separately.
Select an active event in trusted backend configuration; do not accept a
client-supplied event/team scope as authorization.

Commit instance intent and an outbox event atomically. A durable worker sends
an idempotent request carrying instance_id, generation, canonical team_id,
challenge version/digests, TTL and an approved template reference. The
orchestrator must re-read desired state after restarts and compare resource
labels/generation; it cannot depend on request-process lifetime or Redis alone.
Validation, schema migrations, idempotency keys, retries, auth rotation and
delete/recreate race handling remain TASK-002, not implemented guarantees.

KoTH uses `(event_id, challenge_id, round_id)` for a shared arena; never
derive its runtime identity from the claimant's team_id.
