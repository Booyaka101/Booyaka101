// Minimal CDP client over the WebSocket that ships with Node 22. No deps.
// Attaches to an already-running Chrome; it never launches or kills one.
const HOSTS = ["127.0.0.1", "[::1]"];

export async function endpoint(port) {
  for (const host of HOSTS) {
    try {
      const r = await fetch(`http://${host}:${port}/json/version`);
      if (r.ok) return `http://${host}:${port}`;
    } catch {}
  }
  throw new Error(`no CDP on port ${port}`);
}

export async function newTab(base, url) {
  const r = await fetch(`${base}/json/new?${encodeURIComponent(url)}`, {
    method: "PUT",
  });
  if (!r.ok) throw new Error(`could not open tab: ${r.status}`);
  return r.json();
}

export async function closeTab(base, id) {
  await fetch(`${base}/json/close/${id}`).catch(() => {});
}

export async function attach(target) {
  const ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((res, rej) => {
    ws.onopen = res;
    ws.onerror = rej;
  });
  let id = 0;
  const pending = new Map();
  const events = new Map();
  ws.onmessage = (e) => {
    const m = JSON.parse(e.data);
    if (m.id && pending.has(m.id)) {
      const { res, rej } = pending.get(m.id);
      pending.delete(m.id);
      m.error ? rej(new Error(m.error.message)) : res(m.result);
    } else if (m.method && events.has(m.method)) {
      events.get(m.method).forEach((fn) => fn(m.params));
    }
  };
  return {
    send: (method, params = {}) =>
      new Promise((res, rej) => {
        const n = ++id;
        pending.set(n, { res, rej });
        ws.send(JSON.stringify({ id: n, method, params }));
      }),
    on(method, fn) {
      if (!events.has(method)) events.set(method, []);
      events.get(method).push(fn);
    },
    close: () => ws.close(),
  };
}

export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export async function evaluate(cdp, expression) {
  const { result, exceptionDetails } = await cdp.send("Runtime.evaluate", {
    expression,
    returnByValue: true,
    awaitPromise: true,
  });
  if (exceptionDetails) throw new Error(exceptionDetails.text);
  return result.value;
}

export async function waitFor(cdp, expression, timeoutMs = 20000) {
  const until = Date.now() + timeoutMs;
  while (Date.now() < until) {
    if (await evaluate(cdp, expression)) return true;
    await sleep(250);
  }
  return false;
}
