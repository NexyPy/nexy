import { useEffect, useState } from "react";

type Loaded<T> = { key: string; data: T | null; error: string };

const reason = (error: unknown) => (error instanceof Error ? error.message : String(error));

/** Load what `key` names, again each time it changes. The last answer stays on the page while the
 *  next one comes (`stale`), so a filter dims the numbers instead of blanking them. */
export function useLoaded<T>(load: () => Promise<T>, key: string) {
  const [state, setState] = useState<Loaded<T>>({ key: "", data: null, error: "" });

  useEffect(() => {
    let current = true;
    load().then(
      (data) => current && setState({ key, data, error: "" }),
      (error: unknown) => current && setState((last) => ({ ...last, key, error: reason(error) })),
    );
    return () => {
      current = false;
    };
    // `key` names everything `load` reads.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  return { data: state.data, error: state.error, stale: state.key !== key };
}
