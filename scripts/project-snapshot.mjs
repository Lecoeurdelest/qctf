import { createHash } from 'node:crypto';
import { readFile, readdir } from 'node:fs/promises';
import { join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

export const root = fileURLToPath(new URL('../', import.meta.url));
export const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const excluded = new Set(['.git', '.project', 'node_modules', 'dist', '__pycache__', '.venv', '.DS_Store']);

export async function snapshot() {
  const files = {};
  async function walk(directory) {
    const entries = (await readdir(directory, { withFileTypes: true })).sort((a, b) => a.name.localeCompare(b.name));
    for (const entry of entries) {
      if (excluded.has(entry.name) || entry.name.endsWith('.tsbuildinfo')) continue;
      if (entry.name.startsWith('.env') && entry.name !== '.env.example') continue;
      const path = join(directory, entry.name);
      if (entry.isDirectory()) await walk(path);
      else if (entry.isFile()) files[relative(root, path)] = sha256(await readFile(path));
      else throw new Error(`Unsupported snapshot input: ${path}`);
    }
  }
  await walk(root);
  return { files, sha256: sha256(JSON.stringify(files)), exclusions: [...excluded, '.env* except .env.example', '*.tsbuildinfo'] };
}

