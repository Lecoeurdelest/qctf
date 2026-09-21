# Evidence store

Store real task evidence under `.project/evidence/<task-id>/<run-id>/`.
Initial scaffold checks are structural only; do not mark future behavior as
passing without implementation evidence.

TASK-006 now has a real local runner report, input manifest, individual command
logs, retained initial failures, and a separate manual completion review.
Use `make verify` to generate a new immutable run folder. Build/smoke pass is
scoped to initialization and does not close critical domain requirements.
Secrets and mutable database contents are excluded from source snapshots.

The 2026-09-21 skill refresh changed the planning/verification policy and
preservation model. The prior TASK-006 report remains historical; run `make
verify` again before treating it as current evidence.
