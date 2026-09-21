# TASK-004 — Scaffold KoTH plugin and arena contract

- Objective: define shared arena, proof claim, ownership, and idempotent tick behavior.
- Requirements: REQ-004; criteria AC-007, AC-008.
- Dependencies: TASK-001, TASK-002.
- Outputs: `docs/technical/koth-contract.md`.

## Scaffold handoff

State is `todo`; TASK-001/TASK-002 remain incomplete. The loaded plugin under
`plugins/ctfd-koth/qctf_koth` exposes disabled capabilities and 501 operations.
It registers no solvable challenge type and creates no Awards.
Resolve continuous-control versus last-claim scoring, trusted proof verification,
schema/migrations, serialized ownership and tick retry semantics before enabling.
Team identity is server-derived; runtime arena identity is per round, not team.
AC-007/AC-008 require concurrency and duplicate-delivery tests and remain pending.
