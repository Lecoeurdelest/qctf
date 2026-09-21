# Runtime security boundary

Challenge workloads are untrusted. NetworkPolicy, least-privilege service
accounts, resource/PID limits, non-privileged containers, and runtime secret
injection must prevent access to CTFd databases, Redis, and orchestrator
credentials. Secrets must not be committed to application configuration.

## Development safeguards implemented

- Gateway bound to loopback:8088; no published DB, Redis, CTFd or Go ports.
- Separate Docker edge, internal data and internal control networks. Only
  CTFd bridges the API to its stores and the control plane.
- Random, ignored local `.env` with mode 0600; no secrets copied into images.
- Distinct CTFd user token and service Bearer token; backend role/team guards.
- Go binary runs non-root with read-only root, no Linux capabilities and no
  Kubernetes credentials. Requests have HTTP timeouts.
- React renders plain text API fields and keeps tokens in memory; gateway
  supplies a restrictive CSP and does not issue upstream session cookies.

This Compose topology is not Kubernetes workload isolation evidence. There
are no challenge workloads in this stack. NetworkPolicies, RBAC, gVisor/nsjail
compatibility, quotas, resource/PID restrictions and deny-egress tests remain
release gates. Never mount Docker socket, kubeconfig, database credentials or
service tokens into challenge containers.

Before production: replace local preset-admin/environment secret provisioning
with a rotated secret mechanism, implement end-user authentication, TLS,
rate limiting, audit logging, backup/restore and image/dependency scanning.
Do not log Authorization or submitted flags. Upstream API permissions and
legacy extensions require separate review. No security certification is claimed.
