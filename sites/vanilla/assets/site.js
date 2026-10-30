(() => {
  const root = document.body.dataset.root
  const $ = (selector, scope = document) => scope.querySelector(selector)
  const $$ = (selector, scope = document) => [...scope.querySelectorAll(selector)]

  // --- Theme: the choice is kept in this browser -------------------------------------------------
  // The toggle is optional: a page without one still runs the rest of the script.
  // The change is instant: a cross-fade would stack two snapshots of the page on the click.
  const themeSwitch = $('[data-theme-toggle]')
  const still = matchMedia('(prefers-reduced-motion: reduce)').matches
  if (themeSwitch) {
    const showTheme = (name) => themeSwitch.setAttribute('aria-checked', String(name === 'dark'))
    showTheme(document.documentElement.dataset.theme)
    themeSwitch.addEventListener('click', () => {
      const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'
      document.documentElement.dataset.theme = next
      showTheme(next)
      try { localStorage.setItem('nexy-docs-theme', next) } catch {}
    })
  }

  // --- Copy the page as Markdown, to paste into an editor or an AI assistant -------------------------
  // A confirmation with a check mark that draws itself, then the label comes back.
  const CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12 5 5L20 6"/></svg>'
  const done = (button, text, label) => {
    button.classList.add('done')
    button.innerHTML = `${CHECK}${text}`
    setTimeout(() => { button.classList.remove('done'); button.textContent = label }, 1800)
  }
  const copyPage = $('.copy-page')
  if (copyPage) copyPage.addEventListener('click', async () => {
    const label = copyPage.textContent
    try {
      const text = await (await fetch(copyPage.dataset.markdown)).text()
      await navigator.clipboard.writeText(text)
      done(copyPage, 'Copied', label)
    } catch {
      copyPage.textContent = 'Copy failed'
      setTimeout(() => { copyPage.textContent = label }, 1800)
    }
  })

  // --- Menu on a narrow screen ---------------------------------------------------------------------
  // The drawer takes the page with it: the panel behind stops taking tab stops, and closing it
  // puts the focus back on the button that opened it.
  const menu = $('.menu')
  const scrim = $('.scrim')
  const setMenu = (open, restore) => {
    document.body.classList.toggle('open', open)
    menu.setAttribute('aria-expanded', String(open))
    const behind = $('.panel')
    if (behind) behind.inert = open
    if (restore) menu.focus()
  }
  menu.addEventListener('click', () => setMenu(!document.body.classList.contains('open')))
  scrim.addEventListener('click', () => setMenu(false, true))
  $('.side').addEventListener('click', (e) => { if (e.target.closest('a')) setMenu(false) })

  // --- The grid behind the panel follows the pointer by a few pixels -----------------------------
  if (!still && matchMedia('(hover: hover)').matches) {
    let frame = 0
    addEventListener('pointermove', (e) => {
      if (frame) return
      frame = requestAnimationFrame(() => {
        frame = 0
        document.body.style.setProperty('--mx', (e.clientX / innerWidth - 0.5).toFixed(3))
        document.body.style.setProperty('--my', (e.clientY / innerHeight - 0.5).toFixed(3))
      })
    }, { passive: true })
  }

  // --- Reading progress: the panel scrolls on a wide screen, the window on a narrow one ---------
  const panel = $('.panel')
  const progress = $('.progress')
  const scroller = () => (matchMedia('(min-width: 901px)').matches && panel ? panel : document.scrollingElement)
  const paint = () => {
    const box = scroller()
    const max = box.scrollHeight - box.clientHeight
    progress.style.transform = `scaleX(${max > 0 ? Math.min(box.scrollTop / max, 1) : 0})`
  }
  // A scroll does not bubble, so one listener in the capture phase hears the panel and the window.
  addEventListener('scroll', paint, { passive: true, capture: true })
  addEventListener('resize', paint)
  paint()

  // --- Menu: the section of the current page is open, one at a time; bring the page into view ----
  const current = $('.side [aria-current="page"]')
  if (current) current.scrollIntoView({ block: 'center' })

  // --- The menu folds away on a wide screen, and the choice is kept ----------------------------
  const html = document.documentElement
  const fold = (closed) => {
    if (closed) html.dataset.side = 'closed'
    else delete html.dataset.side
    $$('.bar-open').forEach((button) => button.setAttribute('aria-expanded', String(!closed)))
    try { localStorage.setItem('nexy-docs-side', closed ? 'closed' : 'open') } catch {}
  }
  $$('.side-toggle').forEach((button) => button.addEventListener('click', () => fold(!html.dataset.side)))

  // --- The area selector closes on a click elsewhere and on Escape ---------------------------------
  const area = $('.area-select')
  if (area) {
    addEventListener('click', (e) => { if (!area.contains(e.target)) area.open = false })
    addEventListener('keydown', (e) => { if (e.key === 'Escape') area.open = false })
  }

  // --- The filter of the menu: a word keeps the pages that match ---------------------------------
  // The groups come back as they were served when the word is cleared.
  const filter = $('.side-filter input')
  const empty = $('.side-empty')
  if (filter) {
    const groups = $$('.side details.group')
    const settled = groups.map((group) => group.open)
    filter.addEventListener('input', () => {
      const word = filter.value.trim().toLowerCase()
      let found = 0
      groups.forEach((group, index) => {
        let hits = 0
        $$('li', group).forEach((item) => {
          const keep = !word || item.textContent.toLowerCase().includes(word)
          item.hidden = !keep
          if (keep) hits += 1
        })
        group.hidden = Boolean(word) && hits === 0
        group.open = word ? hits > 0 : settled[index]
        found += hits
      })
      if (empty) empty.hidden = found > 0
    })
  }

  // --- Copy button on code blocks --------------------------------------------------------------
  // A shell command with no file name gets a "Terminal" bar, like a named file.
  const SHELLS = ['bash', 'sh', 'shell', 'console', 'powershell']
  $$('.doc pre').forEach((block) => {
    if (block.closest('figure') || !SHELLS.includes(block.getAttribute('lang'))) return
    const figure = document.createElement('figure')
    figure.className = 'terminal'
    figure.innerHTML = '<figcaption>Terminal</figcaption>'
    block.replaceWith(figure)
    figure.append(block)
  })

  $$('.doc pre').forEach((block) => {
    if (block.getAttribute('lang') === 'diagram') return
    const bar = block.closest('figure')?.querySelector('figcaption')
    const button = Object.assign(document.createElement('button'), { className: 'copy', type: 'button', textContent: 'Copy' })
    button.addEventListener('click', async () => {
      try { await navigator.clipboard.writeText(block.innerText) } catch { return }
      done(button, 'Copied', 'Copy')
    })
    ;(bar ?? block).append(button)
  })

  // --- Outline: the last heading read crosses the line under the top bar --------------------------
  const links = new Map($$('.toc a').map((a) => [a.getAttribute('href').slice(1), a]))
  const targets = $$('.doc [id]').filter((h) => links.has(h.id))
  const light = () => {
    let active = null
    for (const heading of targets) {
      if (heading.getBoundingClientRect().top > 120) break
      active = heading
    }
    links.forEach((a, id) => a.classList.toggle('on', Boolean(active) && id === active.id))
  }
  if (targets.length) {
    addEventListener('scroll', light, { passive: true, capture: true })
    addEventListener('resize', light)
    light()
  }

  // --- Search: loaded the first time it opens ----------------------------------------------------
  // The badge tells the truth on the keyboard in front of the reader.
  const badge = $('.search-open kbd')
  if (badge && /Mac|iPhone|iPad|iPod/.test(navigator.userAgent)) badge.textContent = '⌘ K'
  const dialog = $('dialog.search')
  const input = $('input', dialog)
  const list = $('.results', dialog)
  let index = null
  let shownResults = []
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
    list.replaceChildren(...(shownResults.length ? shownResults.map((e, i) => {
      const li = document.createElement('li')
      li.style.setProperty('--i', i)
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
    shownResults = words.length
      ? index.map((e) => [score(e, words), e]).filter(([s]) => s).sort((a, b) => b[0] - a[0]).slice(0, 8).map(([, e]) => e)
      : []
    active = 0
    render()
  }
  const showSearch = async () => {
    await load()
    dialog.dataset.fresh = ''
    dialog.showModal()
    input.value = ''
    search()
    input.focus()
    setTimeout(() => { delete dialog.dataset.fresh }, 500)
  }
  $$('.search-open').forEach((button) => button.addEventListener('click', showSearch))
  input.addEventListener('input', search)
  dialog.addEventListener('click', (e) => { if (e.target === dialog) dialog.close() })
  input.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault()
      if (shownResults.length) active = (active + (e.key === 'ArrowDown' ? 1 : -1) + shownResults.length) % shownResults.length
      render()
    } else if (e.key === 'Enter' && shownResults[active]) {
      e.preventDefault()
      location.href = `${root}/${shownResults[active].url}`
    }
  })
  addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); showSearch() }
    else if (e.key === '/' && !/INPUT|TEXTAREA/.test(document.activeElement.tagName)) { e.preventDefault(); showSearch() }
    else if (e.key === 'Escape' && document.body.classList.contains('open')) setMenu(false, true)
  })
})()
