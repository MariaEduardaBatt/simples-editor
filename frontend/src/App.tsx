import { Link, Outlet, Route, Routes } from 'react-router-dom'

function Layout() {
  return (
    <div className="min-h-dvh bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
          <div className="font-semibold tracking-tight">Simples Editor</div>

          <nav className="flex items-center gap-4 text-sm text-slate-300">
            <Link className="hover:text-white" to="/">
              Home
            </Link>
            <Link className="hover:text-white" to="/login">
              Login
            </Link>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-8">
        <Outlet />
      </main>

      <footer className="border-t border-slate-800">
        <div className="mx-auto max-w-5xl px-4 py-4 text-xs text-slate-400">
          Frontend scaffold (Issue #8)
        </div>
      </footer>
    </div>
  )
}

function Home() {
  return (
    <section className="space-y-3">
      <h1 className="text-2xl font-semibold">Welcome</h1>
      <p className="text-slate-300">
        This is the baseline frontend shell. Authentication and editor features will be
        added in later tasks.
      </p>
    </section>
  )
}

function Login() {
  return (
    <section className="space-y-3">
      <h1 className="text-2xl font-semibold">Login</h1>
      <p className="text-slate-300">
        Placeholder screen. Supabase auth will be wired up in a later issue.
      </p>
    </section>
  )
}

function NotFound() {
  return (
    <section className="space-y-3">
      <h1 className="text-2xl font-semibold">Not Found</h1>
      <p className="text-slate-300">The page you requested does not exist.</p>
    </section>
  )
}

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="login" element={<Login />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}
