# kCTF infrastructure

The selected runtime remains kCTF. The adapter is not enabled in local Compose.
No Kubernetes resource is deployed by `make dev`.

## Inspected legacy source (not vendored)

- Toolkit: `../F-CTF_Platform-master/ctf-directory/kctf/`, VERSION `1.7.2`.
- Web template: `challenge-templates/web/challenge.yaml` and adjacent
  challenge Dockerfiles, nsjail configuration and healthcheck directory.
- Pwn template: `challenge-templates/pwn/` with the same structure.
- Additional existing template: `challenge-templates/xss-bot/`.

Paths above are relative to the **qctf project root**, not this document.
The original files remain intact. No legacy kubeconfig, built binary, secret,
registry credential, challenge flag or cluster configuration is copied.

Next slice must pin a reviewed kCTF CLI/operator pair, import approved templates
with attribution/licenses, validate image and healthcheck compatibility, and
test the Challenge CRD against a disposable cluster. The legacy scripts contain
project-specific changes, so VERSION alone does not prove upstream equivalence.
See `docs/technical/kctf-contract.md` for resource ownership and exposure rules.
