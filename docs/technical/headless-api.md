# Headless CTFd API boundary

React owns product routes. CTFd owns users, teams, challenges, submissions,
solves, Awards and scoreboard aggregation. CTFd 3.8.7 is the initial
checked-in/build-from-source baseline; the modified legacy 3.7.3 backend is not
copied or automatically migrated. Core Flask code can be customized under
`apps/ctfd/upstream/`, while qctf-specific behavior belongs in plugin
namespaces where possible.

## Public gateway

| Route | Behavior in this increment |
| --- | --- |
| `/`, `/login`, `/challenges`, `/scoreboard`, `/koth`, `/control-center` | React SPA |
| `/api/v1/*` | Original CTFd API and authorization |
| `/api/qctf/v1/health` | Plugin liveness |
| `/api/qctf/v1/capabilities` | Explicit enabled/disabled features |
| `/api/qctf/v1/me` | Token principal; canonical team_id |
| `/api/qctf/v1/admin/runtime` | Admin-only Go service inspection |
| `/api/qctf/v1/challenges/{id}/instance` | Team required; GET/POST/DELETE return 501 |
| `/api/qctf/v1/koth/capabilities` | Shared-arena mode, disabled |
| `/api/qctf/v1/koth/arenas` | Token required; 501 |
| `/api/qctf/v1/koth/arenas/{id}/claims` | Team required; 501 |
| `/files/*` | CTFd download endpoint; per-file policy stays in CTFd |

The backend accepts only `/api/` and `/files/` paths. Legacy HTML, setup,
login, admin, theme and plugin asset paths return JSON 404. Their controllers,
forms, themes, template loaders and HTML/JS assets are physically removed.
Flask-RESTX Swagger UI asset registration is disabled; JSON OpenAPI remains.
React implements challenge views and administration.

Challenge list/detail/type and flag type/detail responses no longer include
`template`, `templates`, `script`, `scripts`, rendered `view` or rendered
`create` fields. Challenge `type_data` retains its `id` and `name`. Account
and statistics links refer to JSON API resources rather than removed page
controllers. `/api/v1/shares` is removed with its legacy social-share renderer.
Backend scoring, challenge types, flag comparison and protected downloads
remain. Historical database migrations and content/Markdown fields remain
for data compatibility; they do not enable server-rendered UI.

## Authentication

Clients send `Authorization: Token <ctfd-token>` and
`Content-Type: application/json` for JSON bodies. Token authentication also
works on GETs without Content-Type and multipart file uploads. Do not use Bearer for CTFd tokens.
Bearer is reserved for the separate internal orchestrator service credential.

The scaffold has token-entry development access only. Tokens remain in React
memory, not localStorage, URLs or bundles; fetch omits cookies and disallows
redirects. The gateway hides Set-Cookie for API/file responses. Production
login/session design, expiry UX, CSRF/CORS review and rate limits are pending.
Do not enable upstream self-service UI as a shortcut.

qctf decorators resolve tokens in the backend, reject banned users/teams,
enforce role/team requirements, and read `user.team_id`. Query/body/header
TeamId values never grant authority. Core CTFd endpoint behavior remains
upstream and needs its own full parity/security test suite before release.

Plugin errors have `{success:false,errors:{code,message}}`; successes use
`{success:true,data:...}`. Disabled operations return 501, missing/invalid
identity 401, missing role/team 403, unavailable internal runtime 503.

## Compatibility

The prior document-only `/api/fctf/v1` proposal is superseded before release
by `/api/qctf/v1`. No qctf implementation or client used the old proposal.
Do not claim compatibility for legacy F-CTF consumers; migrate them explicitly.

References: [CTFd token authentication](https://docs.ctfd.io/docs/api/getting-started/),
[API reference](https://docs.ctfd.io/docs/api/redoc/),
[pinned upstream source](https://github.com/CTFd/CTFd/tree/3.8.7).
