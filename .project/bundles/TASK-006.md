# TASK-006 — Runnable local scaffold

## Objective and source

Implement the user-authorized runnable scaffold increment in `plan.md`.
REQ-006 / AC-011, AC-012, AC-013; all CMP components; DEC-001 through DEC-007.
No predecessor completion is required for this bounded initialization task.
It does not complete predecessor production behavior gates.

Exact code/config/lockfile input revisions are captured by
`scripts/project-snapshot.mjs` into each verification run's `inputs.json`;
`report.json` records the model hash and full source hash. The generated
ownership index references the same current source files. Do not reuse a
report if these inputs change.

## Inputs, outputs and invariants

Inputs: `plan.md`, `project.yaml`, `.agent/AGENTS.md`, all five files under
`docs/technical/`, and inspected legacy kCTF provenance in `infra/kctf/README.md`.
Outputs: `apps/web`, `apps/ctfd/upstream`, `plugins/ctfd-headless/qctf_headless`,
`plugins/ctfd-koth/qctf_koth`, `services/orchestrator`, `infra/gateway`,
`compose.yaml`, scripts, tests, CI and implementation/runbook records.

TeamId is backend-derived; normal instance identity will be event/challenge/team.
KoTH is shared per round, with serialized ownership and idempotent ticks still
required. CTFd owns scoring; the browser has no cluster/service credentials.
No secrets in source, no copied legacy C#, no unmanaged port forwards, no
fake live instances or generated scores.

## Verification and exclusions

- AC-011: `make check` — real TypeScript/Vite build, client tests, Go race/vet.
- AC-012: `make dev test-plugins test-bootstrap smoke` — actual local startup
  and bounded API checks, no workload deployment.
- AC-013: manual review of README, technical contracts, UI status and evidence.
- `make verify` retains machine-generated outcomes; manual review is separate.

The CTFd image must be built from the pinned checked-in source; a prebuilt
`ctfd/ctfd` image is not an acceptable substitute for this scaffold.

Exclude full login/admin/solve features, durable instances, Kubernetes setup,
KoTH claim/scoring implementation, legacy migration and production release.
Stop advancement on a failed build/smoke/manual criterion. Keep calibrated
domain-logic confidence null and TASK-001 through TASK-005 pending.

## User-requested legacy UI removal (2026-09-21)

The user explicitly requested physical removal of the remaining CTFd UI.
The source delta is documented in `apps/ctfd/UPSTREAM.md`: remove UI
controllers, forms, theme/template infrastructure, plugin assets and UI-only
extension APIs; keep CTFd models, scoring, data APIs and protected downloads.

Compatibility change: template/script/rendered-view response fields and the
legacy social-share API are removed; account links resolve to API resources.
Auth errors no longer redirect to deleted pages. Existing database migrations
and content fields remain compatible. Third-party UI plugins must be ported
to React/API contracts. This does not implement production login or admin UX.

Validation includes the expanded disposable bootstrap probe in
`tests/plugins/headless_probe.py`, plugin contract tests, image build and live
smoke checks. Full upstream API parity remains outside this bounded change.
