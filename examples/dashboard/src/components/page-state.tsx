import { AlertCircleIcon } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

/** What an action that did not answer leaves on the page. */
export function Problem({ message }: { message: string }) {
  if (!message) return null;
  return (
    <p role="alert" className="flex items-center gap-2 rounded-lg border border-destructive/40 px-4 py-3 text-sm text-destructive">
      <AlertCircleIcon className="size-4 shrink-0" />
      The server did not answer: {message}
    </p>
  );
}

/** The shape of a page before its first answer. */
export function Placeholder({ blocks }: { blocks: string[] }) {
  return (
    <div className="flex flex-col gap-4" aria-busy="true" aria-label="Loading">
      {blocks.map((height, index) => (
        <Skeleton key={index} className={`w-full rounded-xl ${height}`} />
      ))}
    </div>
  );
}
