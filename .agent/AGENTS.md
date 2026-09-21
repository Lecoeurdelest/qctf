# qctf engineering contract

qctf is a new headless CTFd-based platform. React is the product UI, CTFd is
the API/domain backend, kCTF is the challenge runtime, and KoTH is a dedicated
plugin with a shared arena and durable ownership/tick ledger.

Keep TeamId server-derived from the authenticated CTFd principal. Normal
instances are keyed by `(event_id, challenge_id, team_id)`. KoTH ownership
changes and scoring ticks must be serialized and idempotent.

Keep Kubernetes and kCTF details behind the orchestrator contract. Do not use
unmanaged port-forward processes, in-process timers, or Redis as the sole
deployment authority in new code. Keep challenge workloads away from CTFd
databases, Redis, and orchestrator credentials.

Use English for engineering artifacts. Keep comments minimal and explain only
non-obvious invariants or concurrency behavior.
