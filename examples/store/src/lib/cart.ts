// The cart of this browser, shared by the header and the pages: a link changes the page, never the
// cart. The server holds the cart; this is only the last answer it gave.
//
// It is written in the browser only, from onMounted or a click. The server renders the first page
// for every visitor in one process, so state written there would be shared between them.
import { reactive } from "vue";
import { add_to_cart, cart, remove_from_cart, set_quantity } from "@nexy/actions";
import type { Cart } from "@nexy/actions";

const EMPTY: Cart = { lines: [], count: 0, subtotal_cents: 0, shipping_cents: 0, total_cents: 0, note: "" };
const SILENT = "The shop did not answer. Check your connection and try again.";

export const basket = reactive({
  cart: EMPTY,
  loaded: false,
  busy: "", // the product whose change is on its way to the server
  problem: "",
});

async function keep(slug: string, call: () => Promise<Cart>): Promise<void> {
  basket.busy = slug;
  try {
    basket.cart = await call();
    basket.problem = "";
  } catch {
    basket.problem = SILENT;
  } finally {
    basket.busy = "";
    basket.loaded = true;
  }
}

export const load = () => keep("", () => cart());
export const add = (slug: string, quantity = 1) => keep(slug, () => add_to_cart({ slug, quantity }));
export const change = (slug: string, quantity: number) => keep(slug, () => set_quantity({ slug, quantity }));
export const remove = (slug: string) => keep(slug, () => remove_from_cart({ slug }));
