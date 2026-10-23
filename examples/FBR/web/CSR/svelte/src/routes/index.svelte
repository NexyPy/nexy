<script lang="ts">
  import Card from "@/components/card.svelte";
</script>

<main class="min-h-dvh flex flex-col items-center justify-center gap-10 p-8">
  <header class="max-w-xl text-center">
    <p class="font-mono text-xs uppercase tracking-[0.2em] text-foreground-second">
      Client-side routing
    </p>
    <h1 class="mt-3 text-3xl font-semibold text-foreground">Your Nexy app</h1>
    <p class="mt-3 text-sm text-foreground-second">
      Edit
      <code class="rounded bg-background-second px-1.5 py-0.5 font-mono">src/routes/index.svelte</code>
      to get started.
    </p>
  </header>
  <!-- The demo card is designed for a dark surface. -->
  <div class="dark rounded-3xl bg-background p-4">
    <Card />
  </div>
</main>
