// The list of notes, shared by the sidebar and the editor: the editor saves a note, the sidebar
// shows its new title and excerpt. The server holds the notes; this is only the last answer it gave.
//
// It is written in the browser only, from onMount or an event. The server renders the first
// document for every visitor in one process, so state written there would be shared between them.
import { writable } from "svelte/store";
import { create_note, notes } from "@nexy/actions";
import type { Summary } from "@nexy/actions";

export const shelf = writable({
  items: [] as Summary[],
  search: "",
  loaded: false,
  problem: "",
});

const SILENT = "The notes did not load. Check that the server still runs, then try again.";
let asked = 0;

/** Ask for the list again. An answer that comes back after a newer question is dropped. */
export async function refresh(): Promise<void> {
  const question = ++asked;
  let search = "";
  shelf.update((state) => ((search = state.search), state));
  try {
    const items = await notes({ search });
    if (question === asked) shelf.update((state) => ({ ...state, items, loaded: true, problem: "" }));
  } catch {
    if (question === asked) shelf.update((state) => ({ ...state, loaded: true, problem: SILENT }));
  }
}

export function search(words: string): void {
  shelf.update((state) => ({ ...state, search: words }));
  void refresh();
}

/** A new empty note; its id, for the address to open. */
export async function start(): Promise<number> {
  const note = await create_note();
  void refresh();
  return note.id;
}
