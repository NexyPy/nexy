<script lang="ts">
  // The gallery is server HTML: links to the full pictures, which work without JavaScript. This
  // island only opens those links in a dialog, with the arrow keys to move between them.
  let dialog: HTMLDialogElement;
  let links: HTMLAnchorElement[] = [];
  let index = $state(0);
  let src = $state("");
  let caption = $state("");
  let total = $state(0);

  function show(position: number) {
    index = (position + links.length) % links.length;
    src = links[index].href;
    caption = links[index].dataset.caption ?? "";
  }

  $effect(() => {
    links = [...document.querySelectorAll<HTMLAnchorElement>("a[data-lightbox]")];
    total = links.length;
    const open = (event: MouseEvent) => {
      const link = (event.target as Element).closest<HTMLAnchorElement>("a[data-lightbox]");
      if (!link || event.metaKey || event.ctrlKey || event.shiftKey) return;
      event.preventDefault();
      show(links.indexOf(link));
      dialog.showModal();
    };
    document.addEventListener("click", open);
    return () => document.removeEventListener("click", open);
  });

  function move(event: KeyboardEvent) {
    if (event.key === "ArrowRight") show(index + 1);
    if (event.key === "ArrowLeft") show(index - 1);
  }
</script>

<dialog
  bind:this={dialog}
  onkeydown={move}
  onclick={(event) => event.target === dialog && dialog.close()}
  aria-label="Picture"
  class="m-auto w-[min(72rem,calc(100vw-2rem))] max-w-none bg-transparent p-0 text-white backdrop:bg-black/85"
>
  {#if src}
    <figure>
      <img {src} alt={caption} class="max-h-[78vh] w-full rounded-xl object-contain" />
      <figcaption class="mt-4 flex items-start justify-between gap-6 text-sm">
        <span>{caption}</span>
        <span class="shrink-0 tabular-nums text-white/70">{index + 1} of {total}</span>
      </figcaption>
    </figure>
  {/if}
  <div class="mt-4 flex justify-end gap-2">
    <button type="button" onclick={() => show(index - 1)} class="h-11 rounded-full border border-white/30 px-5 text-sm hover:border-white">Previous</button>
    <button type="button" onclick={() => show(index + 1)} class="h-11 rounded-full border border-white/30 px-5 text-sm hover:border-white">Next</button>
    <button type="button" onclick={() => dialog.close()} class="h-11 rounded-full bg-white px-5 text-sm font-medium text-black">Close</button>
  </div>
</dialog>
