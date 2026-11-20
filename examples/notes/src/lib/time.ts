// When a note changed, in the words a person would use: "just now", "12 min ago", "Yesterday".
const MINUTE = 60_000;
const HOUR = 60 * MINUTE;
const DAY = 24 * HOUR;

export function ago(iso: string, now = Date.now()): string {
  const then = new Date(iso);
  const gone = now - then.getTime();
  if (gone < MINUTE) return "just now";
  if (gone < HOUR) return `${Math.floor(gone / MINUTE)} min ago`;
  if (gone < DAY) return `${Math.floor(gone / HOUR)} h ago`;
  if (gone < 2 * DAY) return "Yesterday";
  const year = then.getFullYear() === new Date(now).getFullYear() ? undefined : "numeric";
  return then.toLocaleDateString("en", { day: "numeric", month: "short", year });
}

export function words(text: string): number {
  return text.split(/\s+/).filter(Boolean).length;
}
