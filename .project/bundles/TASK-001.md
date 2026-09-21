# TASK-001 — Freeze the headless CTFd and React API boundary

- Objective: define the route and authentication boundary for React-only UI.
- Requirements: REQ-001; criteria AC-001, AC-002.
- Dependencies: none; state `in_progress` (partial scaffold only).
- Outputs: `docs/technical/headless-api.md`.
- Exclusions: admin implementation and runtime deletion.

## Scaffold handoff

TASK-006 now provides API-backed React routes and token/role/team guards.
See `docs/technical/headless-api.md` and `docs/implementation/scaffold.md`.
The namespace is `/api/qctf/v1`; CTFd uses Token auth, not Bearer. Full auth,
team/admin/solve flows and upstream permission parity remain pending.
Do not mark AC-001/AC-002 as fully proven by the bounded scaffold tests.
Current source revisions are indexed in `.project/generated-manifest.json`;
scoped build/smoke inputs and outcomes live under `.project/evidence/TASK-006/`.
