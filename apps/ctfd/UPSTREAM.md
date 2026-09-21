# Local CTFd source

qctf vendors the upstream CTFd 3.8.7 source under `apps/ctfd/upstream/` so
Flask/CTFd internals can be reviewed and customized in this project. The
Dockerfile builds that source locally and overlays qctf plugins; it does not
pull a prebuilt `ctfd/ctfd` runtime image.

Source provenance: [CTFd 3.8.7](https://github.com/CTFd/CTFd/tree/3.8.7),
downloaded from the official release tag. The upstream Apache-2.0 `LICENSE`
is retained in the directory. Keep upstream changes reviewable and record
custom behavior in qctf plugins or a focused source diff.

## Customization workflow

1. Read the relevant upstream module under `apps/ctfd/upstream/CTFd/`.
2. Prefer a qctf plugin when behavior can be added through supported hooks.
3. If a core change is required, edit the checked-in source and document the
   reason, affected upstream module and compatibility risk in the task bundle.
4. Run `make dev`, `make test-plugins` and `make smoke` after the change.
5. Keep upstream upgrades as explicit plan tasks; do not silently replace the
   source tree with a newer tag.

The source tree is an application dependency, not a second planning authority.
`plan.md` and `project.yaml` continue to own qctf intent and acceptance.


## Headless source delta (2026-09-21)

Removed the legacy page blueprints, WTForms, themes and discovery/loaders,
plugin asset/template/menu hooks, social-share rendering and its API, font,
Swagger UI registration, UI enum generation and obsolete theme build jobs.
WTForms and Pillow are removed from the dependency lock. Jinja2 remains a
Flask dependency; Babel/locales remain for backend validation messages.

The retained `views.py` contains protected downloads only. Challenge and flag
APIs return structured data without template/script/rendered-view fields.
Account/statistics links point to API resources. Request processors and
permission decorators return API errors instead of redirecting to removed
pages; token identity is resolved before account-status checks for all request
content types. Schema and migration history remain intact; one migration
imports email constants from their defining module instead of a UI helper.

UI-only upstream tests are removed. Shared upstream fixtures use models and
sessions instead of removed setup/login forms. The retained upstream suite
is a reference for backend parity, not a claim of full upstream compatibility.
The supported qctf checks are `make test-plugins test-bootstrap smoke`.
