# TASK-005 — Define runtime security and release gates

- Objective: establish network, secret, and runtime boundaries for untrusted challenges.
- Requirements: REQ-005; criteria AC-009, AC-010.
- Dependencies: TASK-002, TASK-003.
- Outputs: `docs/technical/security-boundary.md`.

## Scaffold handoff

State is `todo`; TASK-002/TASK-003 remain incomplete. TASK-006 adds loopback-only
gateway publishing, internal Docker networks, random ignored credentials and a
non-root read-only Go container. No challenge workload exists in this stack.
Do not treat Docker network topology as AC-009 Kubernetes isolation evidence.
AC-010 has partial configuration evidence only; production secret lifecycle,
RBAC, audit, resource limits and upstream authorization review remain open.
Use `docs/technical/security-boundary.md` and the current source hash index.
