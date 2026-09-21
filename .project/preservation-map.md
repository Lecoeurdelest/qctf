# Preservation baseline — 2026-09-21

This map records the accepted structure before reinstalling the GitHub
`Lecoeurdelest/plan-driven-development` skill. The refresh is additive: it
reconciles the existing qctf scaffold instead of deleting or renumbering it.

## Baselines

| Baseline | Source | Revision inspected | Use |
| --- | --- | --- | --- |
| BASE-QCTF-SCAFFOLD | current qctf working tree | prior source snapshot `39ae7c836726b16b836b25220d487f0fbc35a8df0fb4d90cabba9b72a042b017` | Preserve the runnable React/CTFd/Go/Compose scaffold and historical evidence |
| BASE-FCTF-LEGACY | `../F-CTF_Platform-master` | working tree inspected on 2026-09-21; no usable git revision | Preserve as compatibility/provenance source for CTFd, legacy UI and kCTF review |

## Structural dispositions

| Artifact | Disposition | Decision |
| --- | --- | --- |
| `plan.md` | preserve | Keep goal, invariants, non-goals and delivery slices; add the runnable increment |
| `project.yaml` | enhance | Add accepted Go/MariaDB decisions and this preservation model |
| `.project/state.json` | preserve | Keep execution history and TASK-006 completion; add revalidation reason |
| `.project/bundles/TASK-001..006.md` | enhance | Preserve stable IDs and add handoff/revalidation context |
| `docs/technical/*` | enhance | Retain contract content; make current route/security/runtime boundaries explicit |
| `docs/implementation/*` | enhance | Add a task-scoped implementation record for the runnable scaffold |
| `apps`, `plugins`, `services`, `infra` | enhance | Keep source ownership with the implementation; no generated rewrite |
| `apps/ctfd/upstream` | enhance | Preserve the pinned CTFd 3.8.7 source tree as the local customization baseline |
| legacy F-CTF source | preserve externally | Do not copy or delete the sibling project; inspect it for migration and kCTF parity only |

No artifact is marked `supersede` or `remove`; those dispositions would require
explicit approval. The old `/api/fctf/v1` proposal is documented as an
unimplemented namespace correction to `/api/qctf/v1`, not a destructive rewrite
of a deployed API.

## Authority and status

`plan.md` owns intent. `project.yaml` validates and indexes it. `.project/state.json`
owns execution history; every task also has a relevance dimension (`current`,
`superseded` or `retired`) when a migration needs it. `.project/evidence` holds
original runner output; generated manifests only record ownership and hashes.
