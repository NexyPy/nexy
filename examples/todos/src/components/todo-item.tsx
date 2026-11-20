import { useState } from "react";

import Icon from "@/components/icon.tsx";

const PEN = "M4 20h4L19 9l-4-4L4 16zM14 6l4 4";
const BIN = "M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3";

export type Item = { id: number; title: string; done: boolean };

type Props = {
  item: Item;
  onToggle: (id: number) => void;
  onRename: (id: number, title: string) => void;
  onDelete: (id: number) => void;
};

const ICON_BUTTON =
  "grid size-9 place-items-center text-foreground-second transition-colors hover:text-foreground focus-visible:outline-2";

// One row of the list: a checkbox, the title (or a field while it is renamed) and two buttons.
export default function TodoItem({ item, onToggle, onRename, onDelete }: Props) {
  const [editing, setEditing] = useState(false);

  function save(title: string) {
    setEditing(false);
    if (title.trim() && title.trim() !== item.title) onRename(item.id, title);
  }

  return (
    <li className="flex items-center gap-3 border-b border-border px-4 py-2.5 last:border-b-0">
      <input
        type="checkbox"
        checked={item.done}
        onChange={() => onToggle(item.id)}
        aria-label={item.done ? `Mark "${item.title}" as not done` : `Mark "${item.title}" as done`}
        className="size-5 accent-signal"
      />
      {editing ? (
        <input
          autoFocus
          defaultValue={item.title}
          aria-label={`Rename "${item.title}"`}
          maxLength={200}
          onBlur={(event) => save(event.currentTarget.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") save(event.currentTarget.value);
            if (event.key === "Escape") setEditing(false);
          }}
          className="flex-1 border border-border-second bg-background px-2 py-1"
        />
      ) : (
        <span
          onDoubleClick={() => setEditing(true)}
          className={`flex-1 break-words ${item.done ? "text-foreground-second line-through" : ""}`}
        >
          {item.title}
        </span>
      )}
      <button type="button" className={ICON_BUTTON} aria-label={`Rename "${item.title}"`} onClick={() => setEditing(true)}>
        <Icon path={PEN} size={18} />
      </button>
      <button type="button" className={ICON_BUTTON} aria-label={`Delete "${item.title}"`} onClick={() => onDelete(item.id)}>
        <Icon path={BIN} size={18} />
      </button>
    </li>
  );
}
