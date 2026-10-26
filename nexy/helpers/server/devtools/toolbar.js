(() => {
  if (document.getElementById('nexy-devtools')) return
  const page = JSON.parse(document.getElementById('nexy-devtools-data').textContent)
  const css = document.getElementById('nexy-devtools-css').textContent
  const KEY = 'nexy-devtools-hidden'
  const stored = (get) => { try { return get(localStorage) } catch { return null } }

  const h = (tag, props, ...kids) => {
    const el = document.createElement(tag)
    for (const [k, v] of Object.entries(props || {})) {
      if (k === 'class') el.className = v
      else if (k.startsWith('on')) el.addEventListener(k.slice(2), v)
      else el.setAttribute(k, v)
    }
    for (const kid of kids.flat()) {
      if (kid !== null && kid !== undefined) el.append(kid.nodeType ? kid : String(kid))
    }
    return el
  }

  const host = h('div', { id: 'nexy-devtools' })
  const root = host.attachShadow({ mode: 'open' })
  root.append(h('style', {}, css))
  document.body.append(host)

  const clientErrors = []
  let state = null
  let tab = 'page'
  let open = false
  let panel = null

  const nav = performance.getEntriesByType('navigation')[0]
  const ms = (n) => (n === undefined ? '-' : `${Math.round(n)} ms`)
  const row = (name, value) => h('div', { class: 'row' }, h('span', {}, name), h('span', { class: 'mono' }, value))

  const pageTab = () => [
    row('URL', page.path),
    row('Route', page.route || 'no route matched'),
    row('Handler', page.name || '-'),
    row('Status', page.status),
    row('Server time', ms(page.ms)),
    row('Time to first byte', ms(nav && nav.responseStart - nav.requestStart)),
    row('DOM ready', ms(nav && nav.domContentLoadedEventEnd)),
    row('Islands', document.querySelectorAll('[data-nexy-island]').length),
    row('Nexy', page.version),
  ]

  const routesTab = () => {
    if (!state) return [h('div', { class: 'empty' }, 'Loading...')]
    return state.routes.map((r) => {
      const dynamic = r.path.includes('{')
      const label = h('span', { class: 'mono' }, dynamic ? r.path : h('a', { href: r.path }, r.path))
      const tags = r.methods.map((m) => h('span', { class: 'tag' }, m))
      const current = r.path === page.route ? h('span', { class: 'tag current' }, 'current') : null
      return h('div', { class: 'row' }, h('span', {}, tags), label, current)
    })
  }

  const errorsTab = () => {
    const server = state ? state.errors : []
    const all = [...clientErrors, ...server]
    if (!all.length) return [h('div', { class: 'empty' }, 'No error since the server started.')]
    return all.map((e) => h('div', { class: 'err' },
      h('b', {}, e.kind), ': ', e.message, h('div', { class: 'mono' }, e.where || '')))
  }

  const configTab = () => {
    if (!state) return [h('div', { class: 'empty' }, 'Loading...')]
    return Object.entries(state.config).map(([k, v]) => row(k, JSON.stringify(v)))
  }

  const tabs = { page: ['Page', pageTab], routes: ['Routes', routesTab], errors: ['Errors', errorsTab], config: ['Config', configTab] }

  const load = () => fetch('/_nexy/devtools/state').then((r) => r.json()).then((s) => { state = s; render() }).catch(() => {})

  const hide = () => { stored((s) => s.setItem(KEY, '1')); host.remove() }

  const render = () => {
    if (panel) panel.remove()
    panel = null
    const count = clientErrors.length + (state ? state.errors.length : 0)
    bar.querySelector('.dot').className = count ? 'dot bad' : 'dot'
    bar.querySelector('button').setAttribute('aria-pressed', String(open))
    if (!open) return
    const buttons = Object.entries(tabs).map(([id, [label]]) =>
      h('button', { 'aria-selected': String(id === tab), onclick: () => { tab = id; render() } },
        id === 'errors' && count ? `${label} (${count})` : label))
    panel = h('div', { class: 'panel' },
      h('div', { class: 'tabs' }, buttons, h('span', { class: 'spacer' }), h('button', { onclick: hide }, 'Hide')),
      h('div', { class: 'body' }, tabs[tab][1]()))
    root.append(panel)
  }

  const bar = h('div', { class: 'bar' },
    h('button', { 'aria-pressed': 'false', onclick: () => { open = !open; if (open && !state) load(); render() } },
      h('span', { class: 'logo' }, 'N'), 'Nexy', h('span', { class: 'dot' })))
  root.append(bar)

  const overlay = (kind, message, detail) => {
    if (root.querySelector('.overlay')) return
    const close = () => root.querySelector('.overlay').remove()
    root.append(h('div', { class: 'overlay', onclick: (e) => { if (e.target === e.currentTarget) close() } },
      h('div', { class: 'dialog' },
        h('header', {}, h('span', { class: 'pill' }, 'Runtime Error'), h('span', {}, `Nexy ${page.version}`),
          h('span', { class: 'spacer' }), h('button', { onclick: close }, 'Close')),
        h('h2', {}, `${kind}: ${message}`),
        h('div', { class: 'where' }, page.path),
        detail ? h('pre', {}, detail) : null,
        h('footer', {}, 'Shown by nexy dev only. Press Esc to dismiss.'))))
  }

  const report = (kind, message, detail, where) => {
    clientErrors.push({ kind, message, where })
    overlay(kind, message, detail)
    render()
  }

  addEventListener('error', (e) => report(e.error ? e.error.name : 'Error', e.error ? e.error.message : e.message, e.error && e.error.stack, `${e.filename}:${e.lineno}`))
  addEventListener('unhandledrejection', (e) => {
    const r = e.reason
    report(r && r.name ? r.name : 'UnhandledRejection', r && r.message ? r.message : String(r), r && r.stack, '')
  })
  addEventListener('keydown', (e) => {
    if (e.code === 'KeyD' && e.shiftKey && e.altKey) { stored((s) => s.removeItem(KEY)); location.reload() }
    if (e.key === 'Escape') { const o = root.querySelector('.overlay'); if (o) o.remove() }
  })

  if (stored((s) => s.getItem(KEY))) host.remove()
  else render()
})()
