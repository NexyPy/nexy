<script lang="ts">
  import Icon from "@/components/icon.svelte";
  import { search, shelf } from "@/lib/notes";

  const GLASS = "M11 4a7 7 0 100 14 7 7 0 000-14zM21 21l-4.3-4.3";
  const WAIT = 250; // the list follows the typing, without asking at every key

  let words = $state($shelf.search);
  let timer: ReturnType<typeof setTimeout> | undefined;

  function typed() {
    clearTimeout(timer);
    timer = setTimeout(() => search(words.trim()), WAIT);
  }
</script>

<label class="relative block">
  <span class="sr-only">Search the notes</span>
  <span class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-foreground-second">
    <Icon path={GLASS} size={16} />
  </span>
  <input
    type="search"
    bind:value={words}
    oninput={typed}
    placeholder="Search"
    autocomplete="off"
    class="min-h-10 w-full border border-border bg-background py-2 pl-9 pr-3 text-sm placeholder:text-foreground-second focus:border-foreground focus:outline-none"
  />
</label>
