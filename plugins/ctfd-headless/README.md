# ctfd-headless plugin

`qctf_headless` implements JSON-only backend routing, token identity, disabled
instance endpoints, and admin-only orchestrator inspection. The Docker image
installs it under `CTFd/plugins/qctf_headless`. The vendored core also removes
legacy UI implementations; see `apps/ctfd/UPSTREAM.md` for that source delta.

Use `/api/qctf/v1`, separate from original `/api/v1`. Upstream Token auth and
service Bearer auth are distinct. Tests cover missing/expired tokens, banned
accounts, role gates, team spoofing and explicit unimplemented operations.
Read `docs/technical/headless-api.md` before extending the boundary.
