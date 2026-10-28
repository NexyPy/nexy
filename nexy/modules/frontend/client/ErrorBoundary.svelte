<script lang="ts">
  import type { ErrorBoundaryProps } from './svelte.ts'
  import { useMatch, useBlocker, useTransition } from './svelte.ts'

  let { fallback, children }: ErrorBoundaryProps = $props()
  let error: Error | null = $state(null)

  function reset() {
    error = null
  }

  // Re-throw to Svelte's error boundary if we have one above us.
  $effect(() => {
    if (error) {
      throw error
    }
  })
</script>

{#if error}
  {@render fallback(error, reset)}
{:else}
  {@render children?.()}
{/if}
