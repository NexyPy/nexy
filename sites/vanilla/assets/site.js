(() => {
  const root = document.body.dataset.root
  const $ = (selector, scope = document) => scope.querySelector(selector)
  const $$ = (selector, scope = document) => [...scope.querySelectorAll(selector)]

  // --- Theme: the choice is kept in this browser -------------------------------------------------
  $('.theme').addEventListener('click', () => {
    const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'
    document.documentElement.dataset.theme = next
    try { localStorage.setItem('nexy-docs-theme', next) } catch {}
  })

  // --- Menu on a narrow screen ---------------------------------------------------------------------
  const menu = $('.menu')
  const scrim = $('.scrim')
  const setMenu = (open) => {
    document.body.classList.toggle('open', open)
    menu.setAttribute('aria-expanded', String(open))
    scrim.hidden = !open
  }
  menu.addEventListener('click', () => setMenu(!document.body.classList.contains('open')))
  scrim.addEventListener('click', () => setMenu(false))
  $('.side').addEventListener('click', (e) => { if (e.target.closest('a')) setMenu(false) })
  const current = $('.side [aria-current]')
  if (current) current.scrollIntoView({ block: 'center' })

  // --- Copy button on code blocks --------------------------------------------------------------
  $$('.doc pre').forEach((block) => {
    const button = Object.assign(document.createElement('button'), { className: 'copy', type: 'button', textContent: 'Copy' })
    button.addEventListener('click', async () => {
      try { await navigator.clipboard.writeText(block.innerText) } catch { return }
      button.textContent = 'Copied'
      setTimeout(() => { button.textContent = 'Copy' }, 1500)
    })
    block.append(button)
  })

  // --- Outline: the heading being read is lit ------------------------------------------------------
  const links = new Map($$('.toc a').map((a) => [a.getAttribute('href').slice(1), a]))
  if (links.size && 'IntersectionObserver' in window) {
    const seen = new Set()
    const light = () => {
      const first = $$('.doc [id]').find((h) => seen.has(h.id) && links.has(h.id))
      links.forEach((a) => a.classList.remove('on'))
      if (first) links.get(first.id).classList.add('on')
    }
    const watch = new IntersectionObserver((entries) => {
      entries.forEach((e) => (e.isIntersecting ? seen.add(e.target.id) : seen.delete(e.target.id)))
      light()
    }, { rootMargin: '-64px 0px -70% 0px' })
    links.forEach((_, id) => { const h = document.getElementById(id); if (h) watch.observe(h) })
  }

  // --- Search: loaded the first time it opens ----------------------------------------------------
  const dialog = $('dialog.search')
  const input = $('input', dialog)
  const list = $('.results', dialog)
  let index = null
  let shown = []
  let active = 0

  const load = async () => {
    if (index) return
    try { index = await (await fetch(document.body.dataset.search)).json() } catch { index = [] }
  }
  const score = (entry, words) => {
    let total = 0
    for (const word of words) {
      const hit = (text, weight) => (text.toLowerCase().includes(word) ? weight : 0)
      const points = hit(entry.title, 10) + hit(entry.headings, 4) + hit(entry.text, 1)
      if (!points) return 0
      total += points
    }
    return total
  }
  // A few words around the first match, so a result says why it was found.
  const snippet = (entry, words) => {
    const text = `${entry.headings} ${entry.text}`
    const at = words.map((w) => text.toLowerCase().indexOf(w)).filter((i) => i >= 0).sort((x, y) => x - y)[0]
    if (at === undefined) return ''
    const from = Math.max(0, at - 40)
    return `${from > 0 ? '...' : ''}${text.slice(from, from + 120)}...`
  }
  // The words found are wrapped in <mark>. Plain string search: no pattern to escape.
  const mark = (text, words) => {
    const fragment = document.createDocumentFragment()
    const lower = text.toLowerCase()
    let at = 0
    while (at < text.length) {
      const hits = words.map((w) => [lower.indexOf(w, at), w.length]).filter(([i]) => i >= 0).sort((a, b) => a[0] - b[0])
      if (!hits.length) break
      const [start, length] = hits[0]
      const found = Object.assign(document.createElement('mark'), { textContent: text.slice(start, start + length) })
      fragment.append(text.slice(at, start), found)
      at = start + length
    }
    fragment.append(text.slice(at))
    return fragment
  }
  const render = () => {
    list.replaceChildren(...(shown.length ? shown.map((e, i) => {
      const li = document.createElement('li')
      const a = Object.assign(document.createElement('a'), { href: `${root}/${e.url}` })
      a.setAttribute('role', 'option')
      a.setAttribute('aria-selected', String(i === active))
      const words = input.value.toLowerCase().split(/\s+/).filter(Boolean)
      const found = Object.assign(document.createElement('span'), { className: 'snippet' })
      found.append(mark(snippet(e, words), words))
      a.append(e.title, Object.assign(document.createElement('small'), { textContent: e.section }), found)
      li.append(a)
      return li
    }) : [Object.assign(document.createElement('li'), { className: 'none', textContent: input.value ? 'No page matches.' : 'Type to search.' })]))
  }
  const search = () => {
    const words = input.value.toLowerCase().split(/\s+/).filter(Boolean)
    shown = words.length
      ? index.map((e) => [score(e, words), e]).filter(([s]) => s).sort((a, b) => b[0] - a[0]).slice(0, 8).map(([, e]) => e)
      : []
    active = 0
    render()
  }
  const open = async () => { await load(); dialog.showModal(); input.value = ''; search(); input.focus() }
  $('.search-open').addEventListener('click', open)
  input.addEventListener('input', search)
  dialog.addEventListener('click', (e) => { if (e.target === dialog) dialog.close() })
  input.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault()
      if (shown.length) active = (active + (e.key === 'ArrowDown' ? 1 : -1) + shown.length) % shown.length
      render()
    } else if (e.key === 'Enter' && shown[active]) {
      e.preventDefault()
      location.href = `${root}/${shown[active].url}`
    }
  })
  addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); open() }
    else if (e.key === '/' && !/INPUT|TEXTAREA/.test(document.activeElement.tagName)) { e.preventDefault(); open() }
  })
})()
