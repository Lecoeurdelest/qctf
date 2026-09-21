import { spawn } from 'node:child_process';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { root, snapshot, sha256 } from './project-snapshot.mjs';

const before = await snapshot();
const runId = new Date().toISOString().replace(/[:.]/g, '-');
const evidence = join(root, '.project/evidence/TASK-006', runId);
await mkdir(evidence, { recursive: true });
await writeFile(join(evidence, 'inputs.json'), JSON.stringify(before, null, 2) + '\n');
const commands = [
  ['node-version', 'node', ['--version'], '.'],
  ['go-version', 'go', ['version'], '.'],
  ['plan-validation', 'python3', ['/Users/quyn28654/.codex/skills/plan-driven-development/scripts/check_project.py', 'validate', 'project.yaml'], '.'],
  ['preservation-audit', 'python3', ['/Users/quyn28654/.codex/skills/plan-driven-development/scripts/check_project.py', 'audit-preservation', 'project.yaml', '--root', '.'], '.'],
  ['task-index-audit', 'python3', ['/Users/quyn28654/.codex/skills/plan-driven-development/scripts/check_project.py', 'audit-task-status', 'docs/task/README.md'], '.'],
  ['go-tests', 'go', ['test', '-race', '-count=1', '-v', './...'], 'services/orchestrator'],
  ['go-vet', 'go', ['vet', './...'], 'services/orchestrator'],
  ['npm-ci', 'npm', ['ci'], 'apps/web'],
  ['web-check', 'npm', ['run', 'check'], 'apps/web'],
  ['compose-config', 'docker', ['compose', 'config', '--quiet'], '.'],
  ['compose-start', 'docker', ['compose', 'up', '--build', '-d', '--wait'], '.'],
  ['plugin-tests', 'make', ['test-plugins'], '.'],
  ['fresh-bootstrap', 'make', ['test-bootstrap'], '.'],
  ['api-smoke', 'make', ['smoke'], '.'],
  ['compose-status', 'docker', ['compose', 'ps'], '.'],
  ['image-ids', 'docker', ['image', 'inspect', 'qctf-ctfd', 'qctf-orchestrator', 'qctf-gateway', '--format', '{{.Id}}'], '.'],
];
const checks = [];
for (const [id, program, args, directory] of commands) {
  console.log(`Running ${id}…`);
  const started = Date.now();
  const result = await new Promise((resolve) => {
    const child = spawn(program, args, { cwd: join(root, directory), env: { ...process.env, NO_COLOR: '1' }, timeout: 600000 });
    let output = '';
    child.stdout.on('data', (chunk) => { output += chunk; });
    child.stderr.on('data', (chunk) => { output += chunk; });
    child.on('error', (error) => { output += `\n${error.message}\n`; });
    child.on('close', (code, signal) => resolve({ code, signal, output }));
  });
  const artifact = `${id}.log`;
  await writeFile(join(evidence, artifact), result.output);
  checks.push({ id, command: [program, ...args], directory, exit_code: result.code, signal: result.signal, status: result.code === 0 ? 'pass' : 'fail', duration_ms: Date.now() - started, artifact, sha256: sha256(result.output) });
  console.log(`${result.code === 0 ? 'PASS' : 'FAIL'} ${id}`);
  if (result.code !== 0) {
    console.error(result.output.slice(-6000));
    break;
  }
}
const after = await snapshot();
const passed = checks.length === commands.length && checks.every((check) => check.status === 'pass') && before.sha256 === after.sha256;
const report = {
  schema_version: 1,
  task_id: 'TASK-006',
  run_id: runId,
  spec_hash: sha256(await readFile(join(root, 'project.yaml'))),
  source_hash: before.sha256,
  source_unchanged_during_run: before.sha256 === after.sha256,
  scope: 'Local scaffold build and bounded smoke checks only; not a production logic gate',
  status: passed ? 'pass' : 'fail',
  calibrated_logic_confidence: null,
  calibration: { status: 'unavailable', reason: 'No applicable calibrated logic evaluator; scaffold uses build/smoke/manual criteria' },
  checks,
  manual_review_required: ['AC-013: current docs, routes, topology and explicit pending work'],
  limitations: ['No Kubernetes workloads or isolation tests', 'No ownership/tick concurrency implementation', 'No full end-user authentication or legacy parity', 'Runtime secrets and mutable database contents excluded from source snapshot', 'Image IDs recorded; no supply-chain or vulnerability certification', 'No complete AST/data-flow or calibrated requirement-alignment analysis'],
};
await writeFile(join(evidence, 'report.json'), JSON.stringify(report, null, 2) + '\n');
console.log(`Evidence: ${evidence}`);
process.exitCode = passed ? 0 : 1;
