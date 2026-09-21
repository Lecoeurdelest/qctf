import { readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { root, snapshot, sha256 } from './project-snapshot.mjs';

const source = await snapshot();
const managed = ['project.yaml', 'AGENTS.md', '.agent/AGENTS.md',
  'docs/task/README.md',
  ...['headless-api', 'instance-contract', 'kctf-contract', 'koth-contract', 'security-boundary'].map((name) => `docs/technical/${name}.md`),
  ...[1, 2, 3, 4, 5, 6].map((id) => `.project/bundles/TASK-${String(id).padStart(3, '0')}.md`)];
const outputs = {};
for (const path of managed) outputs[path] = { sha256: sha256(await readFile(join(root, path))), owner: 'plan-driven-development', managed_region: 'whole_file', overwrite_policy: 'review_diff_before_regeneration' };
const manifest = {
  schema_version: 1, generator: 'qctf plan-driven index', template_version: '2',
  source_files: ['plan.md'], source_sha256: source.files['plan.md'],
  input_snapshot_sha256: source.sha256,
  inputs: source.files, managed_outputs: outputs,
  execution_state_owner: '.project/state.json is hand-maintained execution history, not generated code',
  application_code_owner: 'Hand-maintained project source; index generation never overwrites it',
};
await writeFile(join(root, '.project/generated-manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
console.log(`Indexed ${Object.keys(source.files).length} source inputs and ${managed.length} managed artifacts.`);
