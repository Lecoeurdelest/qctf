# TASK-003 — Preserve kCTF inputs and define managed exposure

- Objective: retain kCTF while replacing unmanaged port-forward exposure.
- Requirements: REQ-003; criteria AC-005, AC-006.
- Dependencies: TASK-002.
- Outputs: `docs/technical/kctf-contract.md`.

## Scaffold handoff

State is `todo`; TASK-002 is not complete. Legacy toolkit VERSION is 1.7.2,
with project-specific changes; provenance is recorded in `infra/kctf/README.md`.
No toolkit, templates, credentials or workloads were migrated by TASK-006.
The next adapter must use the actual Challenge CRD and operator-owned exposure.
AC-005/AC-006 require a pinned toolchain and disposable-cluster evidence;
current build/smoke results are not compatibility or networking evidence.
