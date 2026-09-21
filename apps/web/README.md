# qctf web

React 19 + Vite + TypeScript. `npm ci && npm run dev` starts hot reload and
proxies `/api` and `/files` to the gateway on 8088. `npm run check` runs the
API-client tests, typecheck and production build.

Routes cover overview, API-backed challenge/score lists, development token
entry, KoTH status and admin runtime inspection. No fake competition data is
seeded. Tokens remain in memory. Full account/team/admin and solve flows are
pending; backend permissions must never be replaced with route-only guards.
