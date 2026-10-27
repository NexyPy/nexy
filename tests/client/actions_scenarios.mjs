// The browser side of @Action (nexy/modules/frontend/client/actions.ts), with fetch replaced.
import { ActionError, createActionState, defineAction } from "../../nexy/modules/frontend/client/actions.ts";

const calls = [];
let reloaded = 0;
let refreshed = 0;
let answer;

globalThis.location = { pathname: "/users", reload: () => reloaded++ };
globalThis.fetch = async (url, init) => {
  calls.push({ url, init });
  return answer();
};

const json = (body, status = 200, headers = {}) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json", ...headers },
  });

async function outcome(promise) {
  try {
    return { value: await promise };
  } catch (error) {
    return { error: { name: error.name, status: error.status, fields: error.fields, message: error.message } };
  }
}

const create = defineAction("/_nx_abc", "src.actions.create");
const out = {};

answer = () => json({ name: "Ada" });
out.result = await create({ name: "Ada" });
out.request = {
  url: calls[0].url,
  method: calls[0].init.method,
  body: calls[0].init.body,
  type: calls[0].init.headers["content-type"],
};
out.metadata = { url: create.url, id: create.id };

answer = () => json({ detail: [{ loc: ["body", "name"], msg: "Field required" }] }, 422);
out.invalid = await outcome(create({}));

answer = () => json({ detail: "no" }, 403);
out.forbidden = await outcome(create({}));

answer = () => new Response("boom", { status: 500 });
out.crash = await outcome(create({}));

answer = () => json("ok", 200, { "x-nexy-revalidate": "*" });
await create({});
out.reloadOnStar = reloaded;

answer = () => json("ok", 200, { "x-nexy-revalidate": "/other" });
await create({});
out.reloadOtherPage = reloaded;

answer = () => json("ok", 200, { "x-nexy-revalidate": "/other,/users" });
await create({});
out.reloadListedPage = reloaded;

globalThis.__nexy_router = { refresh: async () => void refreshed++ };
answer = () => json("ok", 200, { "x-nexy-revalidate": "*" });
await create({});
out.routerRefresh = { refreshed, reloaded };
delete globalThis.__nexy_router;

answer = () => json("ok");
reloaded = 0;
await create({});
out.noHeaderNoReload = reloaded;

// The state of an action
const states = [];
answer = () => json({ id: 1 });
const store = createActionState(create);
store.subscribe(() => states.push(store.getState()));
const data = await store.run({ name: "Ada" });
out.state = { data, states: states.map((s) => ({ pending: s.pending, data: s.data ?? null, error: !!s.error })) };

answer = () => json({ detail: "no" }, 403);
const failing = createActionState(create, { onError: () => (out.onError = true) });
out.failedRun = (await failing.run({})) ?? null;
out.failedState = { pending: failing.getState().pending, error: failing.getState().error?.name };

failing.reset();
out.afterReset = { pending: failing.getState().pending, error: failing.getState().error ?? null };

console.log("@@" + JSON.stringify(out) + "@@");
