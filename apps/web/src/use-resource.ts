import { useEffect, useState } from 'react';
import { apiRequest } from './api';

type Resource<T> = { data: T | null; error: string | null; loading: boolean };

export function useResource<T>(path: string, token = ''): Resource<T> {
  const [state, setState] = useState<Resource<T>>({ data: null, error: null, loading: true });
  useEffect(() => {
    const controller = new AbortController();
    setState({ data: null, error: null, loading: true });
    apiRequest<T>(path, token, { signal: controller.signal }).then(
      (data) => { if (!controller.signal.aborted) setState({ data, error: null, loading: false }); },
      (error: Error) => { if (!controller.signal.aborted) setState({ data: null, error: error.message, loading: false }); },
    );
    return () => controller.abort();
  }, [path, token]);
  return state;
}

