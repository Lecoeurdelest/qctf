export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

export async function apiRequest<T>(
  path: string,
  token = '',
  options: RequestInit = {},
  fetcher: typeof fetch = fetch,
): Promise<T> {
  if (!path.startsWith('/api/')) throw new Error('Only same-origin API paths are allowed');
  const headers = new Headers(options.headers);
  headers.set('Accept', 'application/json');
  headers.set('Content-Type', 'application/json');
  if (token) headers.set('Authorization', `Token ${token}`);
  const response = await fetcher(path, { ...options, headers, credentials: 'omit', redirect: 'error', cache: 'no-store' });
  if (!response.headers.get('Content-Type')?.includes('application/json')) {
    throw new ApiError('The API returned a non-JSON response. Check the gateway and CTFd configuration.', response.status);
  }
  const result = await response.json();
  if (!response.ok || result.success !== true) {
    const fallback = response.status === 401 ? 'Your token is invalid or expired.' : `API request failed (${response.status}).`;
    throw new ApiError(typeof result.errors?.message === 'string' ? result.errors.message : fallback, response.status);
  }
  return result.data as T;
}

