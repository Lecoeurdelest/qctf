import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const content = await readFile(new URL('../.env', import.meta.url), 'utf8');
const env = Object.fromEntries(content.split('\n').filter((line) => line && !line.startsWith('#')).map((line) => {
  const at = line.indexOf('=');
  return [line.slice(0, at), line.slice(at + 1)];
}));
const base = `http://127.0.0.1:${env.QCTF_PORT || '8088'}`;
assert.ok(env.QCTF_ADMIN_TOKEN, 'QCTF_ADMIN_TOKEN is required');
let passed = 0;

async function check(path, status, token, verify = () => {}, json = true) {
  const response = await fetch(`${base}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Token ${token}` } : {}) },
    redirect: 'manual', signal: AbortSignal.timeout(10000),
  });
  assert.equal(response.status, status, `${path}: unexpected status`);
  assert.equal(response.headers.get('set-cookie'), null, `${path}: gateway must not issue cookies`);
  const body = json ? await response.json() : await response.text();
  verify(body);
  passed += 1;
  console.log(`PASS ${path} (${status})`);
}

await check('/', 200, null, (html) => assert.match(html, /<div id="root"><\/div>/), false);
await check('/control-center', 200, null, (html) => assert.match(html, /<title>qctf/), false);
await check('/login', 200, null, (html) => assert.match(html, /<title>qctf/), false);
await check('/api/qctf/v1/health', 200);
await check('/api/qctf/v1/capabilities', 200, null, (body) => {
  assert.equal(body.data.headless, true);
  assert.equal(body.data.instances.enabled, false);
});
await check('/api/qctf/v1/me', 401);
await check('/api/qctf/v1/me', 401, 'invalid');
await check('/api/qctf/v1/me?team_id=999', 200, env.QCTF_ADMIN_TOKEN, (body) => {
  assert.equal(body.data.role, 'admin');
  assert.notEqual(body.data.team_id, 999);
});
await check('/api/v1/challenges', 200, env.QCTF_ADMIN_TOKEN, (body) => assert.ok(Array.isArray(body.data)));
await check('/api/v1/scoreboard', 200, null, (body) => assert.ok(Array.isArray(body.data)));
await check('/api/qctf/v1/admin/runtime', 200, env.QCTF_ADMIN_TOKEN, (body) => {
  assert.equal(body.data.mode, 'scaffold');
  assert.equal(body.data.kctf_connected, false);
});
await check('/api/qctf/v1/koth/capabilities', 200, null, (body) => assert.equal(body.data.enabled, false));
await check('/api/qctf/v1/koth/arenas', 501, env.QCTF_ADMIN_TOKEN);
console.log(`${passed} integration smoke checks passed. No fixture users, challenges, or scores were created.`);

