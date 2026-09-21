# qctf task index

This index is a generated projection of `.project/state.json` and
`project.yaml`. Update the execution record first; never hand-edit a marker
independently. Relevance is separate from execution so historical completion is
not erased by later revalidation or supersession.

## Status legend

- `[]` — `todo` or `ready`
- `[!]` — `in_progress`, `verifying`, `blocked`, or `needs_revalidation`
- `[x]` — `done` with current evidence

## Status

| Status | ID | Title | Execution | Relevance | Depends on | Detail | Evidence |
|---|---|---|---|---|---|---|---|
| [!] | `TASK-001` | Freeze the headless CTFd and React API boundary | `in_progress` | `current` | — | Finish end-user auth/team/admin/solve boundary and full upstream permission review; scaffold evidence is partial. | `.project/evidence/TASK-006/` (partial scaffold evidence) |
| [] | `TASK-002` | Define durable challenge-instance contract | `todo` | `current` | TASK-001 | Design MariaDB uniqueness, outbox, generations, restart recovery and reconciler behavior. | — |
| [] | `TASK-003` | Preserve kCTF inputs and define managed exposure | `todo` | `current` | TASK-002 | Pin the operator/CRD and validate retained templates in a disposable cluster. | — |
| [] | `TASK-004` | Scaffold KoTH plugin and arena contract | `todo` | `current` | TASK-001, TASK-002 | Define proof policy, serialized ownership, tick ledger and Award retry semantics. | — |
| [] | `TASK-005` | Define runtime security and release gates | `todo` | `current` | TASK-002, TASK-003 | Verify workload isolation, RBAC, secret lifecycle, limits and release checks. | — |
| [x] | `TASK-006` | Initialize the runnable local scaffold | `done` | `current` | — | React, headless CTFd plugins, Go service, Compose, CI and bounded tests are complete under the scaffold policy. | `.project/evidence/TASK-006/`; `docs/implementation/TASK-006.md` |

## Dependency path

`TASK-001` → `TASK-002` → `TASK-003` → `TASK-005`

`TASK-001` + `TASK-002` → `TASK-004`

`TASK-006` is an independent runnable-scaffold slice. Its `[x]` does not close
the critical product gates in TASK-001 through TASK-005. `TASK-001` remains
`[!]` because the scaffold only proves a bounded API/UI boundary; complete
authentication and compatibility evidence is still required.
