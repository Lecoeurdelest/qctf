import { randomBytes } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';

const root = new URL('../', import.meta.url);
const secret = () => randomBytes(32).toString('hex');
const values = {
  CTFD_SECRET_KEY: secret(),
  DB_PASSWORD: secret(),
  DB_ROOT_PASSWORD: secret(),
  QCTF_ADMIN_PASSWORD: secret(),
  QCTF_ADMIN_TOKEN: `ctfd_${secret()}`,
  ORCHESTRATOR_TOKEN: secret(),
};
const template = await readFile(new URL('.env.example', root), 'utf8');
const result = template.replace(/^(\w+)=$/gm, (line, key) => values[key] ? `${key}=${values[key]}` : line);
try {
  await writeFile(new URL('.env', root), result, { flag: 'wx', mode: 0o600 });
  console.log('Created .env with local-only credentials. Existing files are never overwritten.');
} catch (error) {
  if (error.code !== 'EEXIST') throw error;
  console.log('.env already exists; preserved without changes.');
}

