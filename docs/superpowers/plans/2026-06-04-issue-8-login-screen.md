# Issue 8 Login Screen Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the frontend login experience with React, Tailwind, and Supabase so users can sign in with email/password, keep a session across reloads, and access the protected app shell.

**Architecture:** Create a new Vite React app in `frontend/`, wire a small Supabase auth layer around it, and protect the app with React Router. Keep the protected area minimal for this issue so login/session behavior is isolated from the later Monaco and xterm work.

**Tech Stack:** React, TypeScript, Vite, Tailwind CSS, Supabase JS, React Router, Vitest, React Testing Library, Monaco Editor, xterm.js

---

### Task 1: Bootstrapping the frontend workspace

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/index.html`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tsconfig.node.json`
- Create: `frontend/tailwind.config.ts`
- Create: `frontend/postcss.config.cjs`
- Create: `frontend/.gitignore`
- Create: `frontend/.env.example`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/index.css`
- Create: `frontend/src/env.d.ts`
- Create: `frontend/src/test/setup.ts`

- [ ] **Step 1: Scaffold the Vite app and install dependencies**

Run:

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install @supabase/supabase-js react-router-dom monaco-editor xterm
npm install -D @vitejs/plugin-react tailwindcss postcss autoprefixer vitest jsdom @testing-library/react @testing-library/user-event @testing-library/jest-dom @types/react @types/react-dom
npx tailwindcss init -p
```

Expected: `frontend/` exists with a React TypeScript starter, the listed dependencies are in `frontend/package.json`, and Tailwind config files are present.

- [ ] **Step 2: Replace the starter files with a clean app shell**

`frontend/package.json`

```json
{
  "name": "frontend",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "dependencies": {
    "@supabase/supabase-js": "^2.0.0",
    "monaco-editor": "^0.52.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.26.0",
    "xterm": "^5.3.0"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^6.5.0",
    "@testing-library/react": "^16.0.0",
    "@testing-library/user-event": "^14.5.2",
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "autoprefixer": "^10.4.20",
    "jsdom": "^24.1.1",
    "postcss": "^8.4.41",
    "tailwindcss": "^3.4.10",
    "typescript": "^5.5.4",
    "vite": "^5.4.0",
    "vitest": "^2.0.5",
    "@vitejs/plugin-react": "^4.3.1"
  }
}
```

`frontend/vite.config.ts`

```ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts']
  }
});
```

`frontend/tailwind.config.ts`

```ts
import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {}
  },
  plugins: []
} satisfies Config;
```

`frontend/postcss.config.cjs`

```js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {}
  }
};
```

`frontend/src/index.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  color-scheme: dark;
}

html,
body,
#root {
  height: 100%;
}

body {
  margin: 0;
  background: #020617;
  color: #e2e8f0;
  font-family: Inter, system-ui, sans-serif;
}
```

`frontend/src/main.tsx`

```tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
```

`frontend/src/App.tsx`

```tsx
export default function App() {
  return (
    <main className="flex min-h-full items-center justify-center px-6">
      <section className="max-w-md rounded-2xl border border-slate-800 bg-slate-900/80 p-8 shadow-2xl shadow-black/30">
        <p className="text-sm uppercase tracking-[0.3em] text-sky-400">Simples Editor</p>
        <h1 className="mt-3 text-3xl font-semibold text-white">Frontend scaffold ready</h1>
        <p className="mt-4 text-sm leading-6 text-slate-300">
          This shell will be replaced by the login flow and protected app routes in the next tasks.
        </p>
      </section>
    </main>
  );
}
```

`frontend/src/env.d.ts`

```ts
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_SUPABASE_URL: string;
  readonly VITE_SUPABASE_ANON_KEY: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
```

`frontend/src/test/setup.ts`

```ts
import '@testing-library/jest-dom/vitest';
```

`frontend/.env.example`

```env
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
```

`frontend/.gitignore`

```gitignore
node_modules
dist
coverage
.env
```

- [ ] **Step 3: Run the starter build to confirm the scaffold is healthy**

Run:

```bash
cd frontend
npm run build
```

Expected: the starter app builds successfully before auth code is added.

- [ ] **Step 4: Commit**

```bash
git add frontend
git commit -m "feat(frontend): bootstrap React Tailwind workspace"
```

### Task 2: Adding required env validation and Supabase client setup

**Files:**
- Create: `frontend/src/lib/env.ts`
- Create: `frontend/src/lib/supabase.ts`
- Create: `frontend/src/lib/env.test.ts`

- [ ] **Step 1: Write the failing env validation test**

`frontend/src/lib/env.test.ts`

```ts
import { describe, expect, it, vi } from 'vitest';
import { requiredEnv } from './env';

describe('requiredEnv', () => {
  it('throws when a required env var is missing', () => {
    vi.stubEnv('VITE_SUPABASE_URL', '');

    expect(() => requiredEnv('VITE_SUPABASE_URL')).toThrow('VITE_SUPABASE_URL is required');
  });
});
```

- [ ] **Step 2: Run the test to confirm it fails before the helper exists**

Run:

```bash
cd frontend
npm run test -- src/lib/env.test.ts
```

Expected: fail because `requiredEnv` is not implemented yet.

- [ ] **Step 3: Implement the minimal env helper and Supabase client**

`frontend/src/lib/env.ts`

```ts
export function requiredEnv(name: 'VITE_SUPABASE_URL' | 'VITE_SUPABASE_ANON_KEY'): string {
  const value = import.meta.env[name];

  if (!value) {
    throw new Error(`${name} is required`);
  }

  return value;
}
```

`frontend/src/lib/supabase.ts`

```ts
import { createClient } from '@supabase/supabase-js';
import { requiredEnv } from './env';

export const supabase = createClient(
  requiredEnv('VITE_SUPABASE_URL'),
  requiredEnv('VITE_SUPABASE_ANON_KEY')
);
```

- [ ] **Step 4: Run the env test again and verify it passes**

Run:

```bash
cd frontend
npm run test -- src/lib/env.test.ts
```

Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/lib/env.ts frontend/src/lib/supabase.ts frontend/src/lib/env.test.ts
git commit -m "feat(frontend): add Supabase env bootstrap"
```

### Task 3: Building auth state and route protection

**Files:**
- Create: `frontend/src/auth/AuthContext.tsx`
- Create: `frontend/src/auth/useAuth.ts`
- Create: `frontend/src/auth/ProtectedRoute.tsx`
- Create: `frontend/src/auth/AuthContext.test.tsx`

- [ ] **Step 1: Write the failing auth state test**

`frontend/src/auth/AuthContext.test.tsx`

```tsx
import { render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { AuthProvider } from './AuthContext';
import { useAuth } from './useAuth';

const mockSession = { user: { email: 'student@example.edu' } } as never;

vi.mock('../lib/supabase', () => ({
  supabase: {
    auth: {
      getSession: vi.fn().mockResolvedValue({ data: { session: mockSession } }),
      onAuthStateChange: vi.fn().mockReturnValue({
        data: { subscription: { unsubscribe: vi.fn() } }
      }),
      signInWithPassword: vi.fn(),
      signOut: vi.fn()
    }
  }
}));

function Probe() {
  const { loading, session } = useAuth();

  return (
    <div>
      <span data-testid="loading">{loading ? 'loading' : 'ready'}</span>
      <span data-testid="user">{session?.user.email ?? 'none'}</span>
    </div>
  );
}

describe('AuthProvider', () => {
  it('renders a session from Supabase on startup', async () => {
    render(
      <AuthProvider>
        <Probe />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('ready');
      expect(screen.getByTestId('user')).toHaveTextContent('student@example.edu');
    });
  });
});
```

- [ ] **Step 2: Run the test to confirm it fails before the provider exists**

Run:

```bash
cd frontend
npm run test -- src/auth/AuthContext.test.tsx
```

Expected: fail because `AuthProvider` and `useAuth` are not implemented yet.

- [ ] **Step 3: Implement the auth context, hook, and protected route**

`frontend/src/auth/AuthContext.tsx`

```tsx
import { createContext, useContext, useEffect, useMemo, useState, type PropsWithChildren } from 'react';
import type { Session } from '@supabase/supabase-js';
import { supabase } from '../lib/supabase';

type AuthContextValue = {
  session: Session | null;
  loading: boolean;
  signIn: typeof supabase.auth.signInWithPassword;
  signOut: typeof supabase.auth.signOut;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: PropsWithChildren) {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    supabase.auth.getSession().then(({ data }) => {
      if (active) {
        setSession(data.session);
        setLoading(false);
      }
    });

    const {
      data: { subscription }
    } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      setSession(nextSession);
      setLoading(false);
    });

    return () => {
      active = false;
      subscription.unsubscribe();
    };
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      session,
      loading,
      signIn: (email, password) => supabase.auth.signInWithPassword({ email, password }),
      signOut: () => supabase.auth.signOut()
    }),
    [loading, session]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }

  return context;
}
```

`frontend/src/auth/useAuth.ts`

```ts
export { useAuth } from './AuthContext';
```

`frontend/src/auth/ProtectedRoute.tsx`

```tsx
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from './useAuth';

export function ProtectedRoute() {
  const { loading, session } = useAuth();

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center text-slate-300">
        Loading session...
      </main>
    );
  }

  if (!session) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
```

- [ ] **Step 4: Run the auth test again and verify it passes**

Run:

```bash
cd frontend
npm run test -- src/auth/AuthContext.test.tsx
```

Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/auth/AuthContext.tsx frontend/src/auth/useAuth.ts frontend/src/auth/ProtectedRoute.tsx frontend/src/auth/AuthContext.test.tsx
git commit -m "feat(frontend): add Supabase auth state"
```

### Task 4: Building the login page, protected shell, and router

**Files:**
- Create: `frontend/src/pages/LoginPage.tsx`
- Create: `frontend/src/pages/AppShell.tsx`
- Modify: `frontend/src/App.tsx`
- Create: `frontend/src/pages/LoginPage.test.tsx`
- Create: `frontend/src/App.test.tsx`

- [ ] **Step 1: Write the failing login and route tests**

`frontend/src/pages/LoginPage.test.tsx`

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { LoginPage } from './LoginPage';

const navigate = vi.fn();
const signIn = vi.fn().mockResolvedValue({ error: null });

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom');

  return {
    ...actual,
    useNavigate: () => navigate
  };
});

vi.mock('../auth/useAuth', () => ({
  useAuth: () => ({
    loading: false,
    session: null,
    signIn,
    signOut: vi.fn()
  })
}));

describe('LoginPage', () => {
  beforeEach(() => {
    navigate.mockReset();
    signIn.mockReset();
    signIn.mockResolvedValue({ error: null });
  });

  it('shows the email and password fields', () => {
    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/senha/i)).toBeInTheDocument();
  });

  it('blocks empty submission', async () => {
    const user = userEvent.setup();

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    await user.click(screen.getByRole('button', { name: /entrar/i }));

    expect(screen.getByRole('alert')).toHaveTextContent(/informe/i);
  });

  it('submits credentials and redirects on success', async () => {
    const user = userEvent.setup();

    render(
      <MemoryRouter>
        <LoginPage />
      </MemoryRouter>
    );

    await user.type(screen.getByLabelText(/email/i), 'student@example.edu');
    await user.type(screen.getByLabelText(/senha/i), 'secret123');
    await user.click(screen.getByRole('button', { name: /entrar/i }));

    expect(signIn).toHaveBeenCalledWith('student@example.edu', 'secret123');
    expect(navigate).toHaveBeenCalledWith('/', { replace: true });
  });
});
```

`frontend/src/App.test.tsx`

```tsx
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import App from './App';

vi.mock('./lib/supabase', () => ({
  supabase: {
    auth: {
      getSession: vi.fn().mockResolvedValue({ data: { session: null } }),
      onAuthStateChange: vi.fn().mockReturnValue({
        data: { subscription: { unsubscribe: vi.fn() } }
      }),
      signInWithPassword: vi.fn(),
      signOut: vi.fn()
    }
  }
}));

vi.mock('./auth/useAuth', () => ({
  useAuth: () => ({
    loading: false,
    session: null,
    signIn: vi.fn(),
    signOut: vi.fn()
  })
}));

describe('App routing', () => {
  it('redirects unauthenticated users to /login', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading', { name: /entrar na ide/i })).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run the tests to confirm they fail before the page and router exist**

Run:

```bash
cd frontend
npm run test -- src/pages/LoginPage.test.tsx src/App.test.tsx
```

Expected: fail because `LoginPage`, `AppShell`, and the routing glue are not implemented yet.

- [ ] **Step 3: Implement the login page, shell, and router**

`frontend/src/pages/LoginPage.tsx`

```tsx
import { FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/useAuth';

export function LoginPage() {
  const navigate = useNavigate();
  const { signIn } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedEmail = email.trim();
    if (!trimmedEmail || !password) {
      setError('Informe um email e uma senha.');
      return;
    }

    if (!trimmedEmail.includes('@')) {
      setError('Informe um email valido.');
      return;
    }

    setLoading(true);
    setError(null);

    const { error: signInError } = await signIn(trimmedEmail, password);

    setLoading(false);

    if (signInError) {
      setError(signInError.message);
      return;
    }

    navigate('/', { replace: true });
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-6">
      <section className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900/90 p-8 shadow-2xl shadow-black/30">
        <p className="text-sm uppercase tracking-[0.3em] text-sky-400">Simples Editor</p>
        <h1 className="mt-3 text-3xl font-semibold text-white">Entrar na IDE</h1>
        <p className="mt-3 text-sm leading-6 text-slate-300">
          Use seu email institucional e senha do Supabase para acessar o ambiente.
        </p>

        <form className="mt-8 space-y-4" onSubmit={handleSubmit} noValidate>
          <label className="block text-sm font-medium text-slate-200">
            Email
            <input
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none ring-0 focus:border-sky-500"
              type="email"
              name="email"
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </label>

          <label className="block text-sm font-medium text-slate-200">
            Senha
            <input
              className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none ring-0 focus:border-sky-500"
              type="password"
              name="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>

          {error ? (
            <p role="alert" className="rounded-xl border border-rose-900 bg-rose-950 px-4 py-3 text-sm text-rose-200">
              {error}
            </p>
          ) : null}

          <button
            className="w-full rounded-xl bg-sky-500 px-4 py-3 font-medium text-slate-950 transition hover:bg-sky-400 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-300"
            type="submit"
            disabled={loading}
          >
            {loading ? 'Entrando...' : 'Entrar'}
          </button>
        </form>
      </section>
    </main>
  );
}
```

`frontend/src/pages/AppShell.tsx`

```tsx
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/useAuth';

export function AppShell() {
  const navigate = useNavigate();
  const { session, signOut } = useAuth();

  async function handleLogout() {
    await signOut();
    navigate('/login', { replace: true });
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-6 text-slate-100">
      <header className="mx-auto flex max-w-5xl items-center justify-between rounded-2xl border border-slate-800 bg-slate-900/80 px-5 py-4">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-sky-400">Simples Editor</p>
          <p className="mt-1 text-sm text-slate-300">Sessao ativa para {session?.user.email ?? 'usuario autenticado'}</p>
        </div>
        <button
          className="rounded-xl border border-slate-700 px-4 py-2 text-sm text-slate-100 hover:border-slate-500"
          type="button"
          onClick={handleLogout}
        >
          Sair
        </button>
      </header>

      <section className="mx-auto mt-6 max-w-5xl rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <h1 className="text-2xl font-semibold">IDE liberada</h1>
        <p className="mt-3 text-sm leading-6 text-slate-300">
          Esta area confirma o acesso autenticado; os paineis de editor, NASM e terminal entram em
          issues seguintes.
        </p>
      </section>
    </main>
  );
}
```

`frontend/src/App.tsx`

```tsx
import { Navigate, Route, Routes } from 'react-router-dom';
import { ProtectedRoute } from './auth/ProtectedRoute';
import { AuthProvider } from './auth/AuthContext';
import { AppShell } from './pages/AppShell';
import { LoginPage } from './pages/LoginPage';

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<AppShell />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}
```

- [ ] **Step 4: Run the login and router tests again and verify they pass**

Run:

```bash
cd frontend
npm run test -- src/pages/LoginPage.test.tsx src/App.test.tsx
```

Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/pages/LoginPage.tsx frontend/src/pages/AppShell.tsx frontend/src/App.tsx frontend/src/pages/LoginPage.test.tsx frontend/src/App.test.tsx
git commit -m "feat(frontend): add Supabase login flow"
```

### Task 5: Running the full frontend verification

**Files:**
- Review: `frontend/package.json`
- Review: all `frontend/src/**/*.ts` and `frontend/src/**/*.tsx`

- [ ] **Step 1: Run the full frontend test suite**

Run:

```bash
cd frontend
npm run test
```

Expected: all frontend tests pass.

- [ ] **Step 2: Run the production build**

Run:

```bash
cd frontend
npm run build
```

Expected: the app compiles successfully with the login flow, route protection, and Tailwind styles in place.

- [ ] **Step 3: Commit**

```bash
git add frontend
git commit -m "test(frontend): verify login screen flow"
```
