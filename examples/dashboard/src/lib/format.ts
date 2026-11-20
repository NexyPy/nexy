// How the dashboard writes its numbers. The server sends cents and ISO days; the page formats them.
const WHOLE = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
const CENTS = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });
const COUNT = new Intl.NumberFormat("en-US");
// A day arrives as "2026-11-15": read in UTC, so it never moves with the time zone of the browser.
const DAY = new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric", timeZone: "UTC" });

/** Whole dollars, for totals: $70,228. */
export const money = (cents: number) => WHOLE.format(cents / 100);

/** Dollars and cents, for one order or an average: $91.32. */
export const exact = (cents: number) => CENTS.format(cents / 100);

export const count = (value: number) => COUNT.format(value);

export const day = (iso: string) => DAY.format(new Date(`${iso}T00:00:00Z`));

/** "Oct 17 to Nov 15, 2026". */
export const span = (first: string, last: string) => `${day(first)} to ${day(last)}, ${last.slice(0, 4)}`;

export type Trend = "up" | "down" | "flat";

/** The change against the period before, or null when there was nothing before to compare with. */
export function change(now: number, before: number): { text: string; trend: Trend } | null {
  if (!before) return null;
  const text = (((now - before) / before) * 100).toFixed(1);
  if (Number(text) === 0) return { text: "0.0%", trend: "flat" };
  return Number(text) > 0 ? { text: `+${text}%`, trend: "up" } : { text: `${text}%`, trend: "down" };
}
