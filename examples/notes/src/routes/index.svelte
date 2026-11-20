<script lang="ts">
  // Beside the list on a wide screen, before a note is open. On a phone the list is shown instead.
  import Brand from "@/components/brand.svelte";
  import NewNote from "@/components/new-note.svelte";
</script>

<section class="m-auto max-w-sm px-6 py-16 text-center">
  <Brand size="text-3xl" />
  <h1 class="mt-6 text-2xl">Pick a note, or start one.</h1>
  <p class="mt-2 text-foreground-second">
    Notes are written in Markdown and saved while you type. Pin the ones you come back to.
  </p>
  <div class="mt-6 flex justify-center"><NewNote /></div>
</section>
