// The period, the channel and the page live in the URL: a reload, a shared link and the back button
// all keep them. These helpers read them and write the link to a change.
import type { Href } from "@nexy/client";

export const PERIODS = ["7", "30", "90"] as const;
export const CHANNELS = ["Online", "Wholesale", "Cafe"] as const;
export const DEFAULT_PERIOD = "30";

export function periodOf(search: URLSearchParams): string {
  const days = search.get("days") ?? "";
  return (PERIODS as readonly string[]).includes(days) ? days : DEFAULT_PERIOD;
}

/** The channel of the URL, or "" for every channel. */
export function channelOf(search: URLSearchParams): string {
  const channel = search.get("channel") ?? "";
  return (CHANNELS as readonly string[]).includes(channel) ? channel : "";
}

/** `pathname` with the query of `search`, changed by `changes`: an empty value drops its key. */
export function linkTo(pathname: string, search: URLSearchParams, changes: Record<string, string> = {}): Href {
  const next = new URLSearchParams(search);
  for (const [key, value] of Object.entries(changes)) {
    if (value) next.set(key, value);
    else next.delete(key);
  }
  const query = next.toString();
  return (query ? `${pathname}?${query}` : pathname) as Href;
}

/** The query a page of the sidebar keeps: the period and the channel, not the page number. */
export function carried(search: URLSearchParams): URLSearchParams {
  const kept = new URLSearchParams();
  for (const key of ["days", "channel"]) {
    const value = search.get(key);
    if (value) kept.set(key, value);
  }
  return kept;
}
