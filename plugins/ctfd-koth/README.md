# ctfd-koth plugin

`qctf_koth` loads through CTFd and exposes disabled capabilities plus guarded
501 responses for arena listing and claims. It intentionally does not register
a challenge type or create ownership/Award tables until the transactional
contract is implemented. It renders no CTFd pages and starts no timer.

Read `docs/technical/koth-contract.md` for the shared-arena model and pending
proof, ownership, tick, retry and scoring obligations.
