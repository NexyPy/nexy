import LinePattern from "@/components/line-pattern.tsx";
import ThemeToggle from "@/components/theme-toggle.tsx";

const SOURCE = "https://github.com/NexyPy/nexy/tree/main/examples/todos";

export default function Header() {
  return (
    <header className="fixed inset-x-0 top-0 z-20 py-4">
      <nav
        className="relative mx-auto flex w-[72rem] max-w-[calc(100%-2rem)] items-center justify-between border border-paper/10 bg-ink/85 px-5 py-3 text-paper backdrop-blur-[4px]"
        aria-label="Main"
      >
        <LinePattern side="right" />
        <a href="/" className="relative flex items-center gap-3">
          <img src="/nexy.svg" alt="Nexy" className="h-5 invert" />
          <span className="font-mono text-xs uppercase tracking-[0.04em]">Todos</span>
        </a>
        <div className="relative flex items-center gap-2">
          <a href={SOURCE} target="_blank" rel="noopener noreferrer" className="px-3 py-2 font-mono text-xs uppercase tracking-[0.04em] hover:opacity-60">
            Source
          </a>
          <ThemeToggle />
        </div>
      </nav>
    </header>
  );
}
