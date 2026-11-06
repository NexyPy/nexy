// The framework-free state behind useFetch (nexy/modules/frontend/client/fetch.ts), fetch replaced.
import { createFetchState, refreshAll } from "../../nexy/modules/frontend/client/fetch.ts";

const calls = [];
let answer;
globalThis.fetch = async (url, init) => {
  calls.push({ url, init });
  return answer(url);
};
const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });
const snapshot = (store) => {
  const { data, error, pending } = store.getState();
  return { data: data ?? null, pending, error: error ? { name: error.name, status: error.status, message: error.message } : null };
};
const out = {};

const users = createFetchState("/api/users");
out.before = snapshot(users);

answer = () => json([{ id: 1 }]);
let notified = 0;
const stop = users.subscribe(() => notified++);
await users.start();
out.loaded = snapshot(users);
out.request = { url: calls[0].url, accept: calls[0].init.headers.accept, credentials: calls[0].init.credentials };
out.notified = notified;

const again = createFetchState("/api/users");
await again.start();
out.sharedWithoutRefetch = { calls: calls.length, data: again.getState().data };

let release;
answer = () => new Promise((resolve) => (release = () => resolve(json([{ id: 1 }, { id: 2 }]))));
const first = users.refresh();
out.whileRefreshing = snapshot(users);
const second = again.refresh();
release();
await Promise.all([first, second]);
out.deduplicated = { calls: calls.length, data: users.getState().data };

answer = () => json({ detail: "No such post" }, 404);
const missing = createFetchState("/api/posts/9");
await missing.start();
out.notFound = snapshot(missing);

answer = () => new Response("boom", { status: 500 });
const broken = createFetchState("/api/broken");
await broken.start();
out.crash = snapshot(broken);

answer = (url) => json({ url });
const before = calls.length;
await refreshAll();
out.refreshAll = calls.slice(before).map((call) => call.url).sort();

stop();
console.log("@@" + JSON.stringify(out) + "@@");
