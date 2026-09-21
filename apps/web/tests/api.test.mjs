import assert from 'node:assert/strict';
import test from 'node:test';
import { apiRequest, ApiError } from '../src/api.ts';

test('uses same-origin CTFd Token authentication without browser cookies', async () => {
  const fetcher = async (path, options) => {
    assert.equal(path, '/api/qctf/v1/me');
    assert.equal(options.headers.get('Authorization'), 'Token user-token');
    assert.equal(options.headers.get('Content-Type'), 'application/json');
    assert.equal(options.credentials, 'omit');
    assert.equal(options.redirect, 'error');
    return Response.json({ success: true, data: { team_id: 42 } });
  };
  assert.deepEqual(await apiRequest('/api/qctf/v1/me', 'user-token', {}, fetcher), { team_id: 42 });
});

test('rejects external URLs before sending a token', async () => {
  await assert.rejects(apiRequest('https://example.com/api', 'secret'), /same-origin/);
});

test('does not render HTML login responses as API data', async () => {
  await assert.rejects(apiRequest('/api/v1/challenges', '', {}, async () => new Response('<html>Login</html>')), /non-JSON/);
});

test('preserves actionable JSON API error and status', async () => {
  const fetcher = async () => Response.json({ success: false, errors: { message: 'Join a team first' } }, { status: 403 });
  await assert.rejects(apiRequest('/api/qctf/v1/me', '', {}, fetcher), (error) => error instanceof ApiError && error.status === 403 && error.message === 'Join a team first');
});

