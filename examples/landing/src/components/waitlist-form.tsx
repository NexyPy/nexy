import { useState } from "preact/hooks";
import { join_waitlist } from "@nexy/actions";

type Status = "idle" | "sending" | "joined" | "refused";

// A real form: without JavaScript the browser posts it to /waitlist (src/routes/waitlist.py) and
// comes back with the outcome in the address. With JavaScript, this island sends it through the
// `join_waitlist` action and answers in place.
export default function WaitlistForm() {
  const [status, setStatus] = useState<Status>("idle");
  const [message, setMessage] = useState("");

  async function submit(event: SubmitEvent) {
    event.preventDefault();
    const email = String(new FormData(event.currentTarget as HTMLFormElement).get("email") ?? "");
    setStatus("sending");
    try {
      const answer = await join_waitlist({ email });
      setStatus(answer.joined ? "joined" : "refused");
      setMessage(answer.message);
    } catch {
      setStatus("refused");
      setMessage("The server did not answer. Try again in a moment.");
    }
  }

  if (status === "joined") {
    return (
      <p role="status" class="flex min-h-12 items-center gap-3 rounded-xl border border-signal/40 bg-signal-soft px-4 text-sm font-medium">
        <svg viewBox="0 0 24 24" class="size-5 flex-none stroke-signal" fill="none" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M20 6L9 17l-5-5" />
        </svg>
        {message}
      </p>
    );
  }

  return (
    <form method="post" action="/waitlist" onSubmit={submit} class="w-full max-w-md">
      <div class="flex flex-col gap-2 sm:flex-row">
        <label for="email" class="sr-only">Your work email</label>
        <input
          id="email"
          name="email"
          type="email"
          required
          maxLength={254}
          autoComplete="email"
          placeholder="you@company.com"
          aria-describedby="waitlist-note"
          class="h-12 min-w-0 rounded-xl sm:flex-1 border border-border-second bg-background px-4 text-base placeholder:text-foreground-second focus:border-foreground focus:outline-none"
        />
        <button
          type="submit"
          disabled={status === "sending"}
          class="h-12 rounded-xl bg-foreground px-5 text-sm font-medium text-background transition-opacity hover:opacity-85 disabled:cursor-progress disabled:opacity-60"
        >
          {status === "sending" ? "Joining..." : "Join the waitlist"}
        </button>
      </div>
      <p id="waitlist-note" aria-live="polite" class={`mt-3 text-sm ${status === "refused" ? "text-down" : "text-foreground-second"}`}>
        {message || "Free while Beacon is in beta. One email when it opens, nothing else."}
      </p>
    </form>
  );
}
