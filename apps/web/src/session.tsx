import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';
import { apiRequest } from './api';

export type Principal = { id: number; name: string; role: string; team_id: number | null; team_name: string | null };
type Session = { token: string; user: Principal | null; signIn: (token: string) => Promise<void>; signOut: () => void };
const SessionContext = createContext<Session | null>(null);

export function SessionProvider({ children }: { children: ReactNode }) {
  const [identity, setIdentity] = useState<{ token: string; user: Principal | null }>({ token: '', user: null });
  async function signIn(token: string) {
    const user = await apiRequest<Principal>('/api/qctf/v1/me', token);
    setIdentity({ token, user });
  }
  return <SessionContext value={{ ...identity, signIn, signOut: () => setIdentity({ token: '', user: null }) }}>{children}</SessionContext>;
}

export function useSession() {
  const session = useContext(SessionContext);
  if (!session) throw new Error('SessionProvider is required');
  return session;
}

