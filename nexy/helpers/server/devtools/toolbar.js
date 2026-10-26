(() => {
  if (document.getElementById('nexy-devtools')) return
  const page = JSON.parse(document.getElementById('nexy-devtools-data').textContent)
  const css = document.getElementById('nexy-devtools-css').textContent

  // --- Preferences, kept in this browser -------------------------------------------------------
  const STORE = 'nexy-devtools'
  const CORNERS = ['top-left', 'top-right', 'bottom-left', 'bottom-right']
  const DEFAULTS = { position: 'bottom-left', theme: 'system', zoom: 1, hidden: false }
  const read = () => { try { return JSON.parse(localStorage.getItem(STORE)) || {} } catch { return {} } }
  const prefs = { ...DEFAULTS, ...read() }
  if (!CORNERS.includes(prefs.position)) prefs.position = DEFAULTS.position
  const save = () => { try { localStorage.setItem(STORE, JSON.stringify(prefs)) } catch {} }

  // --- Small helpers ---------------------------------------------------------------------------
  const h = (tag, props, ...kids) => {
    const el = document.createElement(tag)
    for (const [k, v] of Object.entries(props || {})) {
      if (k === 'class') el.className = v
      else if (k.startsWith('on')) el.addEventListener(k.slice(2), v)
      else if (v !== null && v !== undefined) el.setAttribute(k, v)
    }
    for (const kid of kids.flat()) {
      if (kid !== null && kid !== undefined && kid !== false) el.append(kid.nodeType ? kid : String(kid))
    }
    return el
  }
  const ms = (n) => (n === undefined || Number.isNaN(n) ? '-' : n < 1 ? '<1 ms' : `${Math.round(n)} ms`)
  const row = (name, value) => h('div', { class: 'row' }, h('span', {}, name), h('span', {}, value))
  const editor = (file, label) => (file ? h('a', { href: `vscode://file/${file}` }, label || 'Open in editor') : null)

  // --- The page's own numbers ------------------------------------------------------------------
  const nav = performance.getEntriesByType('navigation')[0]
  const vitals = {}
  const GRADES = { fcp: [1800, 3000], lcp: [2500, 4000], cls: [0.1, 0.25], ttfb: [800, 1800] }
  const grade = (name, value) => {
    const [good, poor] = GRADES[name]
    return value <= good ? 'good' : value <= poor ? 'ok' : 'poor'
  }
  const observe = (type, onEntry) => {
    try {
      new PerformanceObserver((list) => { list.getEntries().forEach(onEntry); schedule() }).observe({ type, buffered: true })
    } catch {}
  }
  observe('paint', (e) => { if (e.name === 'first-contentful-paint') vitals.fcp = e.startTime })
  observe('largest-contentful-paint', (e) => { vitals.lcp = e.startTime })
  observe('layout-shift', (e) => { if (!e.hadRecentInput) vitals.cls = (vitals.cls || 0) + e.value })
  if (nav) vitals.ttfb = nav.responseStart - nav.requestStart

  // --- State -----------------------------------------------------------------------------------
  const clientErrors = []
  let state = null
  let tab = 'page'
  let open = false
  let query = ''
  let queued = false

  const host = h('div', { id: 'nexy-devtools' })
  const shadow = host.attachShadow({ mode: 'open' })
  shadow.append(h('style', {}, css))
  document.body.append(host)

  const root = h('div', { class: 'root', 'data-pos': prefs.position, 'data-theme': 'dark' })
  const pill = h('button', { class: 'pill', 'aria-haspopup': 'dialog', 'aria-expanded': 'false', title: 'Nexy dev tools. Drag to move.' })
  root.append(pill)
  shadow.append(root)

  const errorList = () => [...clientErrors, ...(state ? state.errors : [])]
  const schedule = () => { if (!queued) { queued = true; requestAnimationFrame(() => { queued = false; render() }) } }

  // --- Panels ----------------------------------------------------------------------------------
  const vital = (name, label, value, format) =>
    row(label, value === undefined ? '-' : h('span', { class: 'vital', 'data-grade': grade(name, value) }, format(value)))

  const pageTab = () => [
    h('div', { class: 'h' }, 'This page'),
    row('URL', h('code', {}, page.path)),
    row('Route', h('code', {}, page.route || 'no route matched')),
    row('Handler', page.name || '-'),
    row('Source', page.source ? [h('code', {}, page.source), ' ', editor(page.file)] : '-'),
    row('Status', page.status),
    h('div', { class: 'h' }, 'Timings'),
    row('Server', ms(page.ms)),
    vital('ttfb', 'First byte', vitals.ttfb, ms),
    vital('fcp', 'First paint', vitals.fcp, ms),
    vital('lcp', 'Main content', vitals.lcp, ms),
    vital('cls', 'Layout shift', vitals.cls || 0, (v) => v.toFixed(3)),
    row('DOM ready', ms(nav && nav.domContentLoadedEventEnd)),
    row('Interactive parts', document.querySelectorAll('[data-nexy-island]').length),
  ]

  const routesTab = () => {
    if (!state) return [h('div', { class: 'empty' }, 'Loading...')]
    const needle = query.trim().toLowerCase()
    const shown = state.routes.filter((r) => !needle || r.path.toLowerCase().includes(needle))
    const rows = shown.map((r) => {
      const dynamic = r.path.includes('{')
      return h('div', { class: 'row' },
        h('span', {}, r.methods.map((m) => h('span', { class: 'tag' }, m))),
        h('span', {},
          dynamic || !r.methods.includes('GET') ? h('code', {}, r.path) : h('a', { href: r.path }, r.path),
          r.path === page.route ? h('span', { class: 'tag current' }, 'current') : null,
          r.source ? [' ', editor(r.file, 'edit')] : null))
    })
    const search = h('input', {
      class: 'search', type: 'search', placeholder: 'Filter routes', value: query, 'aria-label': 'Filter routes',
      oninput: (e) => { query = e.target.value; render(true) },
    })
    return [search, rows.length ? rows : h('div', { class: 'empty' }, 'No route matches.')]
  }

  const errorsTab = () => {
    const all = errorList()
    if (!all.length) return [h('div', { class: 'empty' }, 'No error since the server started.')]
    return all.map((e) => h('div', { class: 'err' },
      h('b', {}, e.kind), ': ', e.message, h('div', { class: 'mono muted' }, e.where || '')))
  }

  const choice = (label, current, value, apply) =>
    h('button', { 'aria-pressed': String(current === value), onclick: () => { apply(value); save(); applyPrefs(); render() } }, label)

  const settingsTab = () => [
    h('div', { class: 'h' }, 'Theme'),
    h('div', { class: 'choices' },
      [['Match page', 'system'], ['Dark', 'dark'], ['Light', 'light']].map(([label, v]) => choice(label, prefs.theme, v, (x) => { prefs.theme = x }))),
    h('div', { class: 'h' }, 'Position'),
    h('div', { class: 'choices grid4' },
      CORNERS.map((c) => choice(c.replace('-', ' '), prefs.position, c, (x) => { prefs.position = x }))),
    h('div', { class: 'h' }, 'Size'),
    h('div', { class: 'choices' },
      [['Small', 0.9], ['Default', 1], ['Large', 1.15]].map(([label, v]) => choice(label, prefs.zoom, v, (x) => { prefs.zoom = x }))),
    h('div', { class: 'actions' },
      h('button', { onclick: () => { prefs.hidden = true; save(); applyPrefs() } }, 'Hide for now'),
      h('button', { onclick: () => { Object.assign(prefs, DEFAULTS); save(); applyPrefs(); render() } }, 'Reset')),
    h('div', { class: 'empty' }, 'Shift + Alt + D shows or hides the toolbar. Drag the button to move it.'),
  ]

  const TABS = { page: ['Page', pageTab], routes: ['Routes', routesTab], errors: ['Errors', errorsTab], settings: ['Settings', settingsTab] }
  let panel = null

  function render(keepFocus) {
    const count = errorList().length
    pill.replaceChildren(
      h('span', { class: 'logo' }, 'N'),
      h('span', { class: 'route' }, page.route || page.path),
      h('span', { class: 'ms' }, ms(page.ms)),
      count ? h('span', { class: 'count' }, count) : h('span', { class: 'dot' }))
    pill.setAttribute('aria-expanded', String(open))
    const focused = keepFocus && shadow.activeElement && shadow.activeElement.className
    if (panel) panel.remove()
    panel = null
    if (!open) return
    const tabs = Object.entries(TABS).map(([id, [label]]) =>
      h('button', { role: 'tab', 'aria-selected': String(id === tab), onclick: () => { tab = id; render() } },
        label, id === 'errors' && count ? h('span', { class: 'n' }, count) : null))
    panel = h('div', { class: 'panel', role: 'dialog', 'aria-label': 'Nexy dev tools' },
      h('div', { class: 'head' }, h('span', { class: 'title' }, 'Nexy'), h('span', { class: 'version' }, `v${page.version}`),
        h('span', { class: 'spacer' }), h('button', { class: 'close', 'aria-label': 'Close', onclick: () => toggle(false) }, 'Close')),
      h('div', { class: 'tabs', role: 'tablist' }, tabs),
      h('div', { class: 'body' }, TABS[tab][1]()))
    root.append(panel)
    if (focused) { const again = panel.querySelector(`.${focused}`); if (again) { again.focus(); again.setSelectionRange?.(query.length, query.length) } }
  }

  // "system" follows the page: its dark class, else its colour scheme, else the system's.
  function pageIsDark() {
    const page = document.documentElement
    if (page.classList.contains('dark')) return true
    if (page.classList.contains('light')) return false
    const scheme = getComputedStyle(page).colorScheme
    if (scheme === 'dark' || scheme === 'light') return scheme === 'dark'
    return matchMedia('(prefers-color-scheme: dark)').matches
  }

  function applyPrefs() {
    root.dataset.pos = prefs.position
    root.dataset.theme = prefs.theme === 'system' ? (pageIsDark() ? 'dark' : 'light') : prefs.theme
    root.style.setProperty('--zoom', String(prefs.zoom))
    host.style.display = prefs.hidden ? 'none' : ''
  }

  const load = () => fetch('/_nexy/devtools/state').then((r) => r.json()).then((s) => { state = s; render() }).catch(() => {})
  function toggle(next) {
    open = next === undefined ? !open : next
    if (open && !state) load()
    render()
  }

  // --- Moving the button: drag it, it snaps to the nearest corner ---------------------------------
  let drag = null
  let wasDragged = false
  const snap = () => {
    const box = root.getBoundingClientRect()
    const corner = `${box.top + box.height / 2 < innerHeight / 2 ? 'top' : 'bottom'}-${box.left + box.width / 2 < innerWidth / 2 ? 'left' : 'right'}`
    root.classList.remove('dragging')
    for (const side of ['left', 'top', 'right', 'bottom']) root.style[side] = ''
    root.dataset.pos = corner
    const rest = root.getBoundingClientRect()
    const z = prefs.zoom
    root.style.transition = 'none'
    root.style.transform = `translate(${(box.left - rest.left) / z}px, ${(box.top - rest.top) / z}px)`
    root.getBoundingClientRect()
    root.style.transition = 'transform 0.28s cubic-bezier(0.3, 0.7, 0.2, 1)'
    root.style.transform = ''
    setTimeout(() => { root.style.transition = '' }, 320)
    prefs.position = corner
    save()
  }
  pill.addEventListener('pointerdown', (e) => {
    if (e.button !== 0) return
    pill.setPointerCapture(e.pointerId)
    const box = root.getBoundingClientRect()
    drag = { x: e.clientX, y: e.clientY, left: box.left, top: box.top, moved: false }
  })
  pill.addEventListener('pointermove', (e) => {
    if (!drag) return
    const dx = e.clientX - drag.x
    const dy = e.clientY - drag.y
    if (!drag.moved && Math.hypot(dx, dy) < 5) return
    if (!drag.moved) { drag.moved = true; root.classList.add('dragging') }
    const z = prefs.zoom
    root.style.left = `${(drag.left + dx) / z}px`
    root.style.top = `${(drag.top + dy) / z}px`
    root.style.right = 'auto'
    root.style.bottom = 'auto'
  })
  pill.addEventListener('pointerup', () => {
    const was = drag
    drag = null
    if (!was || !was.moved) return
    wasDragged = true
    setTimeout(() => { wasDragged = false }, 0)
    snap()
  })
  pill.addEventListener('click', () => { if (!wasDragged) toggle() })

  // --- An error raised in the browser opens a dialog over the page --------------------------------
  const overlay = (index) => {
    const old = shadow.querySelector('.overlay')
    if (old) old.remove()
    const all = errorList()
    const e = all[index]
    if (!e) return
    const close = () => { const o = shadow.querySelector('.overlay'); if (o) o.remove() }
    const step = (by) => overlay((index + by + all.length) % all.length)
    shadow.append(h('div', { class: 'overlay', onclick: (ev) => { if (ev.target === ev.currentTarget) close() } },
      h('div', { class: 'dialog', role: 'dialog', 'aria-label': 'Error' },
        h('header', {},
          h('span', { class: 'pill2' }, 'Runtime Error'), h('span', {}, `Nexy ${page.version}`),
          h('span', { class: 'spacer' }),
          all.length > 1 ? [h('button', { 'aria-label': 'Previous error', onclick: () => step(-1) }, '<'),
            h('span', {}, `${index + 1} of ${all.length}`), h('button', { 'aria-label': 'Next error', onclick: () => step(1) }, '>')] : null,
          h('button', { onclick: close }, 'Close')),
        h('h2', {}, `${e.kind}: ${e.message}`),
        h('div', { class: 'where' }, e.where || page.path),
        e.stack ? h('pre', {}, e.stack) : null,
        h('footer', {}, 'Shown by nexy dev only. Press Esc to dismiss.'))))
  }
  const report = (kind, message, stack, where) => {
    clientErrors.push({ kind, message, stack, where })
    overlay(clientErrors.length - 1)
    render()
  }
  addEventListener('error', (e) => report(e.error ? e.error.name : 'Error', e.error ? e.error.message : e.message, e.error && e.error.stack, `${e.filename}:${e.lineno}`))
  addEventListener('unhandledrejection', (e) => {
    const r = e.reason
    report(r && r.name ? r.name : 'UnhandledRejection', r && r.message ? r.message : String(r), r && r.stack, '')
  })

  addEventListener('keydown', (e) => {
    if (e.code === 'KeyD' && e.shiftKey && e.altKey) { prefs.hidden = !prefs.hidden; save(); applyPrefs() }
    if (e.key === 'Escape') {
      const o = shadow.querySelector('.overlay')
      if (o) o.remove()
      else if (open) toggle(false)
    }
  })

  new MutationObserver(() => applyPrefs()).observe(document.documentElement, { attributes: true, attributeFilter: ['class', 'style'] })
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applyPrefs)
  applyPrefs()
  render()
})()
