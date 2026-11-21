import { createSignal, onCleanup, onMount } from "solid-js";
import { delete_card, move_card } from "@nexy/actions";

type Board = Awaited<ReturnType<typeof move_card>>;

// The board is server HTML, and every card already moves with its form. This island adds to it:
// cards can be dragged, moved with Alt and an arrow key, and the forms answer without a reload.
// Each change calls the same action as the form, then puts the cards in the order the server
// answered with.
export default function DragAndDrop() {
  const [said, say] = createSignal("");
  const [note, setNote] = createSignal("");
  let dragged: HTMLElement | null = null;

  const board = () => document.querySelector<HTMLElement>("[data-board]")!;
  const cardOf = (id: number) => board().querySelector<HTMLElement>(`[data-card="${id}"]`);
  const titleOf = (card: HTMLElement) => card.querySelector("[data-title]")?.textContent ?? "";

  function show(answer: Board) {
    const kept = new Set<string>();
    for (const column of answer.columns) {
      const list = board().querySelector(`[data-column="${column.key}"]`)!;
      for (const card of column.cards) {
        const element = cardOf(card.id);
        if (!element) return location.reload(); // added somewhere else: the server draws it
        list.append(element);
        element.querySelector<HTMLSelectElement>("select")!.value = column.key;
        kept.add(String(card.id));
      }
      board().querySelector(`[data-count="${column.key}"]`)!.textContent = String(column.cards.length);
    }
    board().querySelectorAll<HTMLElement>("[data-card]").forEach((card) => kept.has(card.dataset.card!) || card.remove());
    setNote(answer.note);
  }

  async function move(card: HTMLElement, column: string, index?: number) {
    const name = board().querySelector(`#column-${column}`)?.firstChild?.textContent?.trim();
    try {
      show(await move_card({ card_id: Number(card.dataset.card), column, index }));
      say(`${titleOf(card)} moved to ${name}.`);
    } catch {
      setNote("The board could not be saved. Check the connection and try again.");
    }
  }

  // Where a card dropped at `y` lands, counted among the cards of the column without the dragged one.
  function indexAt(list: Element, y: number) {
    const cards = [...list.querySelectorAll<HTMLElement>("[data-card]")].filter((card) => card !== dragged);
    const below = cards.findIndex((card) => y < card.getBoundingClientRect().top + card.offsetHeight / 2);
    return below === -1 ? cards.length : below;
  }

  function onDragStart(event: DragEvent) {
    dragged = (event.target as HTMLElement).closest?.("[data-card]") ?? null;
    if (!dragged) return;
    dragged.toggleAttribute("data-dragging", true);
    event.dataTransfer?.setData("text/plain", titleOf(dragged));
  }

  function onDragOver(event: DragEvent) {
    const list = (event.target as HTMLElement).closest?.("[data-column]");
    if (!dragged || !list) return;
    event.preventDefault();
    board().querySelectorAll("[data-over]").forEach((other) => other !== list && other.removeAttribute("data-over"));
    list.toggleAttribute("data-over", true);
  }

  function onDrop(event: DragEvent) {
    const list = (event.target as HTMLElement).closest?.<HTMLElement>("[data-column]");
    if (!dragged || !list) return;
    event.preventDefault();
    const card = dragged;
    const index = indexAt(list, event.clientY);
    const cards = [...list.querySelectorAll("[data-card]")].filter((other) => other !== card);
    list.insertBefore(card, cards[index] ?? null); // at once; the server answer then confirms it
    move(card, list.dataset.column!, index);
  }

  function onDragEnd() {
    dragged?.removeAttribute("data-dragging");
    board().querySelectorAll("[data-over]").forEach((list) => list.removeAttribute("data-over"));
    dragged = null;
  }

  // Alt and an arrow key: up and down in the column, left and right to the next column.
  function onKey(event: KeyboardEvent) {
    const card = (event.target as HTMLElement).closest?.<HTMLElement>("[data-card]");
    if (!event.altKey || !card || event.target !== card) return;
    const keys = [...board().querySelectorAll<HTMLElement>("[data-column]")].map((list) => list.dataset.column!);
    const list = card.parentElement as HTMLElement;
    const at = [...list.children].indexOf(card);
    const step = { ArrowUp: [0, -1], ArrowDown: [0, 1], ArrowLeft: [-1, 0], ArrowRight: [1, 0] }[event.key];
    if (!step) return;
    event.preventDefault();
    const column = keys[keys.indexOf(list.dataset.column!) + step[0]];
    if (!column || at + step[1] < 0) return;
    move(card, column, step[0] ? undefined : at + step[1]).then(() => card.focus());
  }

  async function onSubmit(event: SubmitEvent) {
    const form = event.target as HTMLFormElement;
    const card = form.closest<HTMLElement>("[data-card]");
    if (!card || !(form.matches("[data-move]") || form.matches("[data-delete]"))) return;
    event.preventDefault();
    if (form.matches("[data-move]")) return move(card, new FormData(form).get("column") as string);
    try {
      const title = titleOf(card);
      show(await delete_card({ card_id: Number(card.dataset.card) }));
      say(`${title} deleted.`);
    } catch {
      setNote("The card could not be deleted. Check the connection and try again.");
    }
  }

  onMount(() => {
    const root = board();
    root.querySelectorAll<HTMLElement>("[data-card]").forEach((card) => {
      card.draggable = true;
      card.tabIndex = 0;
      card.classList.add("cursor-grab");
    });
    const listeners = { dragstart: onDragStart, dragover: onDragOver, drop: onDrop, dragend: onDragEnd, keydown: onKey, submit: onSubmit } as const;
    for (const [name, listener] of Object.entries(listeners)) root.addEventListener(name, listener as EventListener);
    onCleanup(() => {
      for (const [name, listener] of Object.entries(listeners)) root.removeEventListener(name, listener as EventListener);
    });
  });

  return (
    <>
      <p role="status" class="sr-only">{said()}</p>
      <p role="alert" class="mt-4 rounded-lg border border-down/40 bg-down/10 px-4 py-3 text-sm empty:hidden">{note()}</p>
    </>
  );
}
