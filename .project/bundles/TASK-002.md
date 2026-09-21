# TASK-002 — Define durable challenge-instance contract

- Objective: specify durable `(event, challenge, team)` identity and lifecycle.
- Requirements: REQ-002; criteria AC-003, AC-004.
- Dependencies: TASK-001.
- Outputs: `docs/technical/instance-contract.md`.

## Scaffold handoff

Go is selected (DEC-005); MariaDB is the durable-store target (DEC-006).
`services/orchestrator/internal/server` exposes authenticated diagnostics and
501 instance responses only. State is `todo`; TASK-001 is not complete.
Preserve canonical server-derived TeamId and event/challenge/team uniqueness.
Next work must design migrations/outbox/generations and recovery tests, not
replace durability with an in-memory map. All AC-003/AC-004 gates remain pending.
See the current contract and `.project/generated-manifest.json` for inputs.
