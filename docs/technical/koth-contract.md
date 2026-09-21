# KoTH contract

KoTH uses one shared arena per challenge round. Claims derive TeamId from the
authenticated CTFd token and submit a short-lived proof. A transaction lock or
equivalent invariant serializes concurrent claims. Ownership intervals and tick
records are durable; each tick maps to at most one CTFd Award.

## Implemented now

Only the plugin loader, capability endpoint, authorization guards, and explicit
501 responses exist. No KoTH challenge type is registered: registering a
standard solvable type prematurely could incorrectly award normal solve points.
The React route is a disabled status view, not a playable arena.

## Required before enabling play

- Separate arena rounds, ownership intervals, claims/nonces and tick ledger
  records with schema migrations.
- Verify short-lived, replay-resistant proofs against a trusted external
  checker. Bind proof to arena/round/team/expiry. Do not trust a browser's
  claimed owner or assume a writable file proves durable control.
- Serialize transitions using a database transaction and row lock. Record
  claimant identity and server timestamps; concurrent valid claims must have
  one deterministic committed order.
- Define whether points reward the last accepted claim or freshly verified
  ongoing control. This policy is unresolved and must be explicit before ticks.
- Give every scoring tick a unique `(arena_id, round_id, tick_index)` and link
  exactly one CTFd Award in the same durable transaction (or an equally proven
  retry-safe protocol). Define no-owner, ties, expiry, downtime and freeze rules.
- Validate kCTF/nsjail process isolation against the intended shared-arena
  semantics; per-connection sandboxes do not automatically provide a persistent
  KoTH machine. Never weaken isolation implicitly to make the mode work.

Durable scheduler/recovery, authorized reset flows, proof threat model and
concurrency/duplicate-delivery tests are pending. No tick worker is started.
