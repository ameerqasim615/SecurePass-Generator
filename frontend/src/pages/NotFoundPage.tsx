import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-50 px-4 text-center dark:bg-slate-950">
      <p className="text-sm font-semibold text-violet-600 dark:text-violet-400">404</p>
      <h1 className="mt-2 text-3xl font-semibold text-navy-800 dark:text-white">Page not found</h1>
      <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
        The page you are looking for does not exist or has moved.
      </p>
      <Link
        to="/"
        className="mt-6 rounded-md bg-navy-800 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-navy-900"
      >
        Back to home
      </Link>
    </main>
  )
}
