import { useState } from 'react';
import type { FormEvent, ReactNode } from 'react';
import { Link, NavLink, Route, Routes, useNavigate } from 'react-router-dom';
import { useSession } from './session';
import { useResource } from './use-resource';

type Capabilities = { headless: boolean; instances: { enabled: boolean; reason: string }; koth: { enabled: boolean; reason: string } };
type Challenge = { id: number; name: string; category: string; value: number; solves: number; type: string };
type Score = { pos: number; account_id: number; name: string; score: number };
type Runtime = { service: string; mode: string; kctf_connected: boolean; reconciler_enabled: boolean; instance_storage: string };

function Header({ eyebrow, title, children }: { eyebrow: string; title: string; children: ReactNode }) {
  return <header className="page-header"><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p className="lede">{children}</p></header>;
}

function Feedback({ loading, error }: { loading: boolean; error: string | null }) {
  if (loading) return <p role="status" className="notice">Connecting to CTFd…</p>;
  return error ? <p role="alert" className="notice error">{error}</p> : null;
}

function Overview() {
  const capabilities = useResource<Capabilities>('/api/qctf/v1/capabilities');
  const { user } = useSession();
  return <>
    <Header eyebrow="Your next challenge starts here" title="Think. Break. Capture.">A dedicated competition workspace, powered by CTFd. One interface for challenges, teams, and the arena.</Header>
    <section className="hero-panel">
      <div><span className="tag">DEVELOPMENT WORKSPACE</span><h2>The foundation is online.</h2><p>Explore the API-backed challenge board. Instance deployment and KoTH scoring are the next implementation slices.</p><Link className="button primary" to={user ? '/challenges' : '/login'}>{user ? 'Open challenge board' : 'Connect your account'} <span aria-hidden="true">↗</span></Link></div>
      <div className="terminal" aria-label="Platform architecture"><span className="terminal-label">qctf / architecture</span><p><i>01</i> React workspace</p><p><i>02</i> CTFd domain API</p><p><i>03</i> Go control plane</p><p className="muted"><i>04</i> kCTF adapter · pending</p></div>
    </section>
    <Feedback {...capabilities} />
    <div className="cards">
      <article className="card"><span className="card-index">01 / COMPETE</span><h2>Challenge board</h2><p>Challenges and scores come directly from the CTFd API.</p><Link to="/challenges">Browse challenges →</Link></article>
      <article className="card"><span className="card-index">02 / HOLD THE HILL</span><h2>Shared arena</h2><p>{capabilities.data?.koth.reason ?? 'KoTH ownership and scoring are pending implementation.'}</p><Link to="/koth">View arena status →</Link></article>
      <article className="card"><span className="card-index">03 / OPERATE</span><h2>Control center</h2><p>Inspect the internal control plane. Instance lifecycle is not enabled yet.</p><Link to="/control-center">Open control center →</Link></article>
    </div>
  </>;
}

function AuthRequired() {
  return <div className="empty"><h2>Connect to your workspace</h2><p>A CTFd token is required to access this page.</p><Link className="button primary" to="/login">Connect account</Link></div>;
}

function ChallengeBoard() {
  const { token, user } = useSession();
  if (!user) return <AuthRequired />;
  return <Challenges key={token} token={token} />;
}

function Challenges({ token }: { token: string }) {
  const result = useResource<Challenge[]>('/api/v1/challenges', token);
  return <>
    <Header eyebrow="Competition / challenges" title="Find your next flag.">Live challenge metadata from CTFd. Challenge solving and instance controls will be added in the next slice.</Header>
    <Feedback {...result} />
    {result.data?.length === 0 ? <div className="empty"><h2>A clean slate.</h2><p>No challenges are available. Add a challenge through the CTFd admin API to populate this board.</p></div> : null}
    <div className="cards">{result.data?.map((challenge) => <article className="card" key={challenge.id}><span className="tag">{challenge.category || 'Uncategorized'}</span><h2>{challenge.name}</h2><p>{challenge.value} points <span className="separator">/</span> {challenge.solves} solves</p><span className="muted">{challenge.type} · #{challenge.id}</span></article>)}</div>
  </>;
}

function Scoreboard() {
  const { token } = useSession();
  const result = useResource<Score[]>('/api/v1/scoreboard', token);
  return <>
    <Header eyebrow="Competition / standings" title="Every flag counts.">The CTFd scoreboard remains the source of truth for competition points.</Header>
    <Feedback {...result} />
    {result.data ? <div className="table-wrap"><table><caption className="sr-only">Competition scoreboard</caption><thead><tr><th scope="col">Rank</th><th scope="col">Team</th><th scope="col">Points</th></tr></thead><tbody>{result.data.map((row) => <tr key={row.account_id}><td className="muted">{String(row.pos).padStart(2, '0')}</td><td>{row.name}</td><td className="points">{row.score}</td></tr>)}</tbody></table>{result.data.length === 0 ? <p className="notice">No scores yet. The first solve starts the board.</p> : null}</div> : null}
  </>;
}

function Koth() {
  const result = useResource<{ enabled: boolean; reason: string }>('/api/qctf/v1/koth/capabilities');
  return <>
    <Header eyebrow="Game mode / king of the hill" title="Capture. Hold. Defend.">A shared arena with team ownership and periodic points awarded through CTFd.</Header>
    <Feedback {...result} />
    <div className="empty"><span className="tag">NOT ENABLED</span><h2>The arena is under construction.</h2><p>{result.data?.reason ?? 'Proof verification, ownership persistence, and scoring are not implemented.'}</p><button disabled>Claim hill — unavailable</button></div>
  </>;
}

function ControlCenter() {
  const { user, token } = useSession();
  if (!user) return <AuthRequired />;
  if (user.role !== 'admin') return <div className="empty"><h2>Administrator access required</h2><p>The control plane is not available to contestant accounts.</p></div>;
  return <RuntimePanel key={token} token={token} />;
}

function RuntimePanel({ token }: { token: string }) {
  const runtime = useResource<Runtime>('/api/qctf/v1/admin/runtime', token);
  const capabilities = useResource<Capabilities>('/api/qctf/v1/capabilities');
  return <>
    <Header eyebrow="Administration / control center" title="Know your runtime.">The browser talks to CTFd. Only the backend can reach the Go orchestrator.</Header>
    <Feedback {...runtime} /><Feedback {...capabilities} />
    {runtime.data ? <section className="panel"><div className="panel-heading"><h2>Orchestrator</h2><span className="tag">{runtime.data.mode}</span></div><dl><div><dt>Service connection</dt><dd>Reachable</dd></div><div><dt>kCTF cluster</dt><dd>{runtime.data.kctf_connected ? 'Connected' : 'Not connected'}</dd></div><div><dt>Reconciler</dt><dd>{runtime.data.reconciler_enabled ? 'Enabled' : 'Disabled'}</dd></div><div><dt>Instance storage</dt><dd>{runtime.data.instance_storage}</dd></div></dl></section> : null}
    <p className="notice">{capabilities.data?.instances.reason ?? 'Instance deployment is not available in this scaffold.'} No Kubernetes credentials are configured.</p>
  </>;
}

function Login() {
  const { signIn } = useSession();
  const navigate = useNavigate();
  const [token, setToken] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await signIn(token.trim());
      setToken('');
      navigate('/challenges');
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Could not connect.');
    } finally {
      setBusy(false);
    }
  }
  return <>
    <Header eyebrow="Account / development access" title="Connect your account.">Use your own CTFd API token. The token stays in memory and is cleared when you reload or sign out.</Header>
    <form className="panel login-form" onSubmit={submit}><label htmlFor="api-token">CTFd API token</label><input id="api-token" name="token" type="password" autoComplete="off" spellCheck={false} required value={token} onChange={(event) => setToken(event.target.value)} placeholder="ctfd_…" /><p className="muted">Local administrator: use QCTF_ADMIN_TOKEN from the project’s .env file. Never share this token with contestants.</p>{error ? <p role="alert" className="error">{error}</p> : null}<button className="primary" disabled={busy || !token.trim()}>{busy ? 'Connecting…' : 'Connect to qctf →'}</button></form>
  </>;
}

export function App() {
  const { user, signOut } = useSession();
  return <div className="app-shell"><a className="skip-link" href="#main">Skip to content</a><aside className="sidebar"><Link className="brand" to="/" aria-label="qctf home"><span className="brand-mark" aria-hidden="true">q</span>qctf<span className="brand-dot">.</span></Link><p className="nav-label">WORKSPACE</p><nav aria-label="Main navigation"><NavLink to="/" end>Overview</NavLink><NavLink to="/challenges">Challenges</NavLink><NavLink to="/scoreboard">Scoreboard</NavLink><NavLink to="/koth">King of the Hill <span className="nav-badge">WIP</span></NavLink>{!user || user.role === 'admin' ? <NavLink to="/control-center">Control center</NavLink> : null}</nav><div className="sidebar-bottom"><span className="status-dot" /> LOCAL DEVELOPMENT<p>CTFd core. A new surface.</p></div></aside><div className="workspace"><div className="topbar"><span className="breadcrumb">qctf <span>/</span> workspace</span>{user ? <div className="account"><span>{user.name} <small>{user.team_name ?? user.role}</small></span><button className="text-button" onClick={signOut}>Sign out</button></div> : <Link className="button small" to="/login">Connect account ↗</Link>}</div><main id="main"><Routes><Route path="/" element={<Overview />} /><Route path="/challenges" element={<ChallengeBoard />} /><Route path="/scoreboard" element={<Scoreboard />} /><Route path="/koth" element={<Koth />} /><Route path="/control-center" element={<ControlCenter />} /><Route path="/login" element={<Login />} /><Route path="*" element={<div className="empty"><h1>Page not found</h1><Link to="/">Back to overview</Link></div>} /></Routes></main><footer>qctf <span>Scaffold v0.1 · Not production-ready</span></footer></div></div>;
}

