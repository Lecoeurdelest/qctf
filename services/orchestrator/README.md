# qctf orchestrator

Go HTTP service using only the standard library. The Compose image is non-root
and read-only. `ORCHESTRATOR_TOKEN` must have at least 32 characters; it is
separate from any CTFd user token.

- `GET /healthz`: 200, process liveness only.
- `GET /readyz`: 503 because Kubernetes integration is disabled.
- `GET /internal/v1/runtime`: authenticated scaffold capabilities.
- `POST /internal/v1/instances`: authenticated 501, no mutation.

Internal endpoints require `Authorization: Bearer <service-token>`. They are
not published by the gateway. `go test -race ./...` and `go vet ./...` verify
the bounded scaffold. There is no deployment, fake store or reconciler yet.
Next: durable instance/outbox contract and a reviewed kCTF adapter.
