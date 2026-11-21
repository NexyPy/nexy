<script lang="ts">
  // The page is rendered once at build: a time written there would be wrong for everyone. The city
  // is in the HTML; the time is added once the island runs, then kept up to date.
  const ZONE = "Europe/Lisbon";
  const format = new Intl.DateTimeFormat("en-GB", { hour: "2-digit", minute: "2-digit", timeZone: ZONE });

  let now = $state("");

  $effect(() => {
    const tick = () => (now = format.format(new Date()));
    tick();
    const timer = setInterval(tick, 15_000);
    return () => clearInterval(timer);
  });
</script>

<p class="text-sm text-foreground-second">
  Based in Lisbon, Portugal{#if now}, where it is <time class="tabular-nums text-foreground">{now}</time>{/if}.
</p>
