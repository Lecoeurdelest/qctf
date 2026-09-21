# kCTF runtime contract

kCTF challenge templates, Dockerfiles, healthchecks, and sandbox settings are
retained inputs. Build/publish is separate from team instance start.

Production exposure is managed through `Service -> Ingress` for web challenges
and a managed TCP gateway or Service mapping for pwn challenges. New code must
not depend on an unmanaged `kubectl port-forward` process.

The new project retains the **kCTF interface**, not the old C# deployment
implementation. Legacy template provenance is in `infra/kctf/README.md`.
The original toolkit is not vendored, executed or mutated by this scaffold.

The inspected legacy templates use `apiVersion: kctf.dev/v1`, `kind: Challenge`,
`spec.deployed`, `spec.network` and `spec.healthcheck`; the web template includes
an HTTPS port targeting 1337. They are not bare Deployment manifests. The
adapter must respect the pinned operator's schema and let its controller own
child resources. Do not independently reconcile overlapping Services/Ingress
without an explicit ownership contract.

Before enabling the adapter: choose/pin the matching operator CRD, import and
review templates and healthchecks with licensing/provenance, verify kCTF builds,
publish immutable image digests, define unique resource names and approved
network/namespace boundaries, then test against a disposable cluster.
Source-to-runtime compatibility is not verified by the current smoke tests.

Reference: [kCTF documentation](https://google.github.io/kctf/),
[custom domains](https://google.github.io/kctf/custom-domains.html),
[threat model](https://google.github.io/kctf/security-threat-model.html).
