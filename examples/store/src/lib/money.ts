// Prices travel as cents, the way the database keeps them. Only the page turns them into dollars.
const DOLLARS = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });
const DAY = new Intl.DateTimeFormat("en-US", { dateStyle: "medium" });

export function money(cents: number): string {
  return DOLLARS.format(cents / 100);
}

export function day(iso: string): string {
  return DAY.format(new Date(iso));
}

// What the shelves say about a product, in the words a shop uses.
export function availability(stock: number): string {
  if (stock === 0) return "Sold out";
  if (stock <= 5) return `Only ${stock} left`;
  return "In stock";
}
