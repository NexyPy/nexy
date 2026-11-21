import { useEffect, useState } from "preact/hooks";

type Message = { id: number; room: string; author: string; text: string; sent_at: string };

const EVERY = 2000; // how often a visible room asks for new messages, in ms

// The room is server HTML, and its form posts to /send without JavaScript. This island adds to it:
// it sends without a reload, asks for new messages while the tab is visible, and shows times in the
// reader's own time. New messages are made from the page's <template>, filled with textContent.
export default function LiveRoom() {
  const [online, setOnline] = useState(true);

  useEffect(() => {
    const list = document.querySelector<HTMLOListElement>("[data-messages]");
    const form = document.querySelector<HTMLFormElement>("[data-send]");
    const template = document.querySelector<HTMLTemplateElement>("[data-message-template]");
    if (!list || !form || !template) return;
    const room = list.dataset.room!;
    const note = form.querySelector<HTMLElement>("[data-note]")!;
    const text = form.querySelector<HTMLTextAreaElement>("textarea")!;

    const lastId = () => Number(list.lastElementChild?.getAttribute("data-message") ?? 0);
    const localTime = (time: HTMLTimeElement) => {
      time.textContent = new Date(time.dateTime).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    };

    function show(messages: Message[]) {
      const scroller = list!.parentElement!;
      const atEnd = scroller.scrollTop > -40; // column-reverse: 0 is the bottom
      for (const message of messages) {
        if (list!.querySelector(`[data-message="${message.id}"]`)) continue;
        const item = template!.content.firstElementChild!.cloneNode(true) as HTMLLIElement;
        item.dataset.message = String(message.id);
        item.querySelector("[data-initial]")!.textContent = message.author.slice(0, 1).toUpperCase();
        item.querySelector("[data-author]")!.textContent = message.author;
        item.querySelector("[data-text]")!.textContent = message.text;
        const time = item.querySelector<HTMLTimeElement>("[data-time]")!;
        time.dateTime = message.sent_at;
        localTime(time);
        list!.append(item);
      }
      if (atEnd) scroller.scrollTop = 0;
    }

    async function poll() {
      if (document.hidden) return;
      try {
        const answer = await fetch(`/api/messages?room=${room}&after=${lastId()}`);
        show(await answer.json());
        setOnline(true);
      } catch {
        setOnline(false);
      }
    }

    async function send(event: SubmitEvent) {
      event.preventDefault();
      const body = new URLSearchParams(new FormData(form!) as unknown as Record<string, string>);
      body.set("after", String(lastId()));
      try {
        const answer = await fetch("/send", { method: "POST", body, headers: { accept: "application/json" } });
        const { note: said, messages } = await answer.json();
        note.textContent = said;
        show(messages);
        if (!said) text.value = "";
        setOnline(true);
      } catch {
        note.textContent = "The message could not be sent. Check the connection and try again.";
        setOnline(false);
      }
      text.focus();
    }

    // Enter sends, Shift and Enter starts a new line.
    function enter(event: KeyboardEvent) {
      if (event.key !== "Enter" || event.shiftKey || event.isComposing) return;
      event.preventDefault();
      form!.requestSubmit();
    }

    list.querySelectorAll<HTMLTimeElement>("time[data-time]").forEach(localTime);
    form.addEventListener("submit", send);
    text.addEventListener("keydown", enter);
    const timer = setInterval(poll, EVERY);
    document.addEventListener("visibilitychange", poll);
    return () => {
      form.removeEventListener("submit", send);
      text.removeEventListener("keydown", enter);
      clearInterval(timer);
      document.removeEventListener("visibilitychange", poll);
    };
  }, []);

  return (
    <p class="flex shrink-0 items-center gap-2 text-xs text-foreground-second">
      <span aria-hidden="true" class={`size-2 rounded-full ${online ? "bg-live" : "bg-down"}`} />
      {online ? "Live" : "Offline, retrying"}
    </p>
  );
}
