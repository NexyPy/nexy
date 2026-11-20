<script lang="ts">
  import { add_to_cart } from "@nexy/actions";

  let { slug, name }: { slug: string; name: string } = $props();

  let quantity = $state(1);
  let pending = $state(false);
  let message = $state("");

  async function add() {
    pending = true;
    message = "";
    try {
      const { count } = await add_to_cart({ slug, quantity });
      window.dispatchEvent(new CustomEvent("cart:count", { detail: count }));
      message = `Added ${quantity} to your cart.`;
    } catch {
      message = "Could not add it. Try again.";
    } finally {
      pending = false;
    }
  }

  const step = "grid size-11 place-items-center text-lg hover:bg-background-second disabled:opacity-40";
</script>

<div class="flex flex-col gap-3">
  <div class="flex flex-wrap items-center gap-3">
    <div class="flex items-center border border-border-second" role="group" aria-label="Quantity">
      <button type="button" class={step} aria-label="One less" disabled={quantity <= 1} onclick={() => (quantity -= 1)}>-</button>
      <output class="w-10 text-center tabular-nums" aria-live="polite">{quantity}</output>
      <button type="button" class={step} aria-label="One more" disabled={quantity >= 10} onclick={() => (quantity += 1)}>+</button>
    </div>
    <button
      type="button"
      class="min-h-11 flex-1 bg-foreground px-6 font-medium text-background transition-opacity hover:opacity-85 disabled:opacity-60 sm:flex-none"
      disabled={pending}
      onclick={add}
    >
      {pending ? "Adding" : "Add to cart"}
    </button>
  </div>
  <p role="status" class="min-h-6 text-sm text-foreground-second">
    {#if message}{message} <a href="/cart" class="text-foreground underline underline-offset-4">View cart</a>{/if}
  </p>
</div>
