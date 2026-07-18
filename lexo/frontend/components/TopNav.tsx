import Link from "next/link";

export default function TopNav() {
  return (
    <header className="sticky top-0 z-10 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
        <Link href="/dashboard" className="flex items-center gap-2 font-serif text-lg font-medium text-zinc-100">
          <span className="h-1.5 w-1.5 rounded-full bg-indigo-400" />
          Lexo
        </Link>
        <nav className="flex items-center gap-6 text-sm">
          <Link href="/dashboard" className="text-zinc-400 transition hover:text-zinc-100">
            Dashboard
          </Link>
          <Link
            href="/login"
            className="rounded-md border border-zinc-800 px-3 py-1.5 text-zinc-400 transition hover:border-zinc-700 hover:text-zinc-100"
          >
            Log out
          </Link>
        </nav>
      </div>
    </header>
  );
}
