#!/usr/bin/env python3
"""Render the human task index from project.yaml and .project/state.json."""

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
MODEL = yaml.safe_load((ROOT / "project.yaml").read_text())
STATE = __import__("json").loads((ROOT / ".project/state.json").read_text())
DETAILS = {
    "TASK-001": "Finish end-user auth/team/admin/solve boundary and full upstream permission review; scaffold evidence is partial.",
    "TASK-002": "Design MariaDB uniqueness, outbox, generations, restart recovery and reconciler behavior.",
    "TASK-003": "Pin the operator/CRD and validate retained templates in a disposable cluster.",
    "TASK-004": "Define proof policy, serialized ownership, tick ledger and Award retry semantics.",
    "TASK-005": "Verify workload isolation, RBAC, secret lifecycle, limits and release checks.",
    "TASK-006": "React, headless CTFd plugins, Go service, Compose, CI and bounded tests are complete under the scaffold policy.",
}
MARKERS = {"todo": "[]", "ready": "[]", "in_progress": "[!]", "verifying": "[!]", "blocked": "[!]", "needs_revalidation": "[!]", "done": "[x]"}


def evidence_for(task_id, execution):
    if execution != "done":
        if task_id == "TASK-001":
            return "`.project/evidence/TASK-006/` (partial scaffold evidence)"
        return "—"
    return f"`.project/evidence/{task_id}/`; `docs/implementation/{task_id}.md`"


rows = []
for task in MODEL["tasks"]:
    task_id = task["id"]
    execution = STATE["tasks"].get(task_id, "todo")
    relevance = "current"
    dependencies = ", ".join(task.get("depends_on", [])) or "—"
    rows.append(
        f"| {MARKERS[execution]} | `{task_id}` | {task['title']} | `{execution}` | `{relevance}` | {dependencies} | {DETAILS.get(task_id, 'See the task bundle for the next condition.')} | {evidence_for(task_id, execution)} |"
    )

content = """# qctf task index

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
""" + "\n".join(rows) + """

## Dependency path

`TASK-001` → `TASK-002` → `TASK-003` → `TASK-005`

`TASK-001` + `TASK-002` → `TASK-004`

`TASK-006` is an independent runnable-scaffold slice. Its `[x]` does not close
the critical product gates in TASK-001 through TASK-005. `TASK-001` remains
`[!]` because the scaffold only proves a bounded API/UI boundary; complete
authentication and compatibility evidence is still required.
"""
(ROOT / "docs/task/README.md").write_text(content)
print("Rendered docs/task/README.md from project.yaml and .project/state.json")
