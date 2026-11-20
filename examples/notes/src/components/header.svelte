<script lang="ts">
  import Link from "@nexy/Link.svelte";

  import LinePattern from "@/components/line-pattern.svelte";
  import Brand from "@/components/brand.svelte";
  import NewNote from "@/components/new-note.svelte";
  import ThemeToggle from "@/components/theme-toggle.svelte";
</script>

<header class="shrink-0 pt-4 [view-transition-name:nx-header]">
  <nav
    class="relative mx-auto flex w-[72rem] max-w-[calc(100%-2rem)] items-center justify-between border border-paper/10 bg-ink px-5 py-3 text-paper shadow-[0_10px_30px_-12px_rgb(0_0_0/0.4)]"
    aria-label="Main"
  >
    <LinePattern side="right" />
    <Link href="/" aria-label="Margin, all notes" class="relative">
      <Brand />
    </Link>
    <div class="relative flex items-center gap-3">
      <ThemeToggle />
      <NewNote tone="on-ink" />
    </div>
  </nav>
</header>
