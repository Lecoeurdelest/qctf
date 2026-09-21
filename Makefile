.PHONY: env dev down logs check test-go test-web test-plugins test-bootstrap smoke verify sync

env:
	node scripts/init-env.mjs

dev: env
	docker compose up --build -d --wait

down:
	docker compose down

logs:
	docker compose logs --tail=100 -f

test-go:
	cd services/orchestrator && go test -race ./... && go vet ./...

test-web:
	cd apps/web && npm ci && npm run check

test-plugins:
	docker compose exec -T ctfd python -m unittest discover -s /opt/qctf/tests -v

test-bootstrap:
	docker compose run --rm --no-deps --entrypoint python -e DATABASE_URL=sqlite:////tmp/qctf-bootstrap.sqlite -e REDIS_URL= -e UPLOAD_FOLDER=/tmp/qctf-probe-uploads ctfd /opt/qctf/tests/bootstrap_probe.py

smoke:
	node scripts/smoke.mjs

check: test-go test-web

verify:
	node scripts/verify-scaffold.mjs

sync:
	python3 scripts/render-task-index.py
	node scripts/refresh-project-index.mjs
	python3 /Users/quyn28654/.codex/skills/plan-driven-development/scripts/check_project.py validate project.yaml
	python3 /Users/quyn28654/.codex/skills/plan-driven-development/scripts/check_project.py audit-preservation project.yaml --root .
	python3 /Users/quyn28654/.codex/skills/plan-driven-development/scripts/check_project.py audit-task-status docs/task/README.md
