import { useEffect, useState } from "react";
import {
  add_todo,
  clear_completed,
  delete_todo,
  list_todos,
  rename_todo,
  toggle_todo,
} from "@nexy/actions";

import Container from "@/components/container.tsx";
import TodoItem, { type Item } from "@/components/todo-item.tsx";

type Board = { items: Item[]; note: string };
type Filter = "all" | "active" | "done";

const FILTERS: [Filter, string][] = [
  ["all", "All"],
  ["active", "To do"],
  ["done", "Done"],
];

function shown(items: Item[], filter: Filter): Item[] {
  if (filter === "active") return items.filter((item) => !item.done);
  if (filter === "done") return items.filter((item) => item.done);
  return items;
}

function left(items: Item[]): string {
  const count = items.filter((item) => !item.done).length;
  return count === 1 ? "1 thing left" : `${count} things left`;
}

export default function Todos() {
  const [items, setItems] = useState<Item[]>([]);
  const [filter, setFilter] = useState<Filter>("all");
  const [status, setStatus] = useState("Loading the list...");
  const [loaded, setLoaded] = useState(false);

  // Every action answers with the whole list: the page shows what the database holds.
  async function apply(call: Promise<Board>): Promise<boolean> {
    try {
      const board = await call;
      setItems(board.items);
      setStatus(board.note);
      return !board.note;
    } catch (error) {
      setStatus(`The server did not answer: ${error instanceof Error ? error.message : error}`);
      return false;
    } finally {
      setLoaded(true);
    }
  }

  useEffect(() => {
    apply(list_todos());
  }, []);

  async function add(event: { preventDefault(): void; currentTarget: HTMLFormElement }) {
    event.preventDefault();
    const form = event.currentTarget;
    const title = String(new FormData(form).get("title") ?? "");
    if (await apply(add_todo({ title }))) form.reset();
  }

  // The box changes at once; the answer of the server then replaces the whole list.
  function toggle(todo_id: number) {
    setItems((now) => now.map((item) => (item.id === todo_id ? { ...item, done: !item.done } : item)));
    apply(toggle_todo({ todo_id }));
  }

  const visible = shown(items, filter);
  const doneCount = items.length - items.filter((item) => !item.done).length;

  return (
    <section className="flex flex-1 pb-20 pt-36">
      <Container className="max-w-[40rem]">
        <h1 className="text-5xl leading-[1.05]">Todos</h1>
        <p className="mt-4 text-foreground-second">
          Kept in SQLite by Python. Double-click a title to rename it.
        </p>

        <form onSubmit={add} className="mt-8 flex gap-2">
          <label htmlFor="new-todo" className="sr-only">What needs doing?</label>
          <input
            id="new-todo"
            name="title"
            placeholder="What needs doing?"
            maxLength={200}
            autoComplete="off"
            className="flex-1 border border-border-second bg-background px-3 py-2.5"
          />
          <button type="submit" className="border border-foreground bg-foreground px-5 font-mono text-sm uppercase text-background hover:opacity-85">
            Add
          </button>
        </form>

        <p role="status" aria-live="polite" className="mt-3 min-h-6 text-sm text-foreground-second">
          {status}
        </p>

        <div role="tablist" aria-label="Show" className="mt-4 flex gap-1 font-mono text-xs uppercase">
          {FILTERS.map(([value, label]) => (
            <button
              key={value}
              type="button"
              role="tab"
              aria-selected={filter === value}
              onClick={() => setFilter(value)}
              className="px-3 py-2 aria-selected:bg-foreground aria-selected:text-background"
            >
              {label} ({shown(items, value).length})
            </button>
          ))}
        </div>

        <ul aria-label="Todos" className="mt-2 border border-border">
          {visible.map((item) => (
            <TodoItem
              key={item.id}
              item={item}
              onToggle={toggle}
              onRename={(todo_id, title) => apply(rename_todo({ todo_id, title }))}
              onDelete={(todo_id) => apply(delete_todo({ todo_id }))}
            />
          ))}
          {loaded && visible.length === 0 && (
            <li className="px-4 py-6 text-center text-foreground-second">
              {items.length === 0 ? "Nothing to do yet." : "Nothing here."}
            </li>
          )}
        </ul>

        <div className="mt-3 flex items-center justify-between text-sm text-foreground-second">
          <span>{left(items)}</span>
          {doneCount > 0 && (
            <button type="button" onClick={() => apply(clear_completed())} className="underline underline-offset-4 hover:text-foreground">
              Clear done ({doneCount})
            </button>
          )}
        </div>
      </Container>
    </section>
  );
}
