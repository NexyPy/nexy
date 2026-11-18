<script lang="ts">
  // Catch errors during client rendering and show a fallback instead of crashing the page.
  //
  //   <ErrorBoundary>
  //     {#snippet fallback(error, reset)}<p>{error.message}</p>{/snippet}
  //     <Page />
  //   </ErrorBoundary>
  import type { Snippet } from 'svelte'

  type Props = {
    /** Rendered when a descendant throws during client navigation. */
    fallback: Snippet<[Error, () => void]>
    children?: Snippet
  }

  let { fallback, children }: Props = $props()

  const asError = (error: unknown): Error =>
    error instanceof Error ? error : new Error(String(error))
</script>

<svelte:boundary>
  {@render children?.()}
  {#snippet failed(error, reset)}
    {@render fallback(asError(error), reset)}
  {/snippet}
</svelte:boundary>
