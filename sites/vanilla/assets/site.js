(() => {
  const root = document.body.dataset.root
  const $ = (selector, scope = document) => scope.querySelector(selector)
  const $$ = (selector, scope = document) => [...scope.querySelectorAll(selector)]

  // --- Motion: initialized in template ---------------------------------------------------

  // --- Theme: the choice is kept in this browser -------------------------------------------------
  // The toggle is optional: a page without one still runs the rest of the script.
  const themeSwitch = $('[data-theme-toggle]')
  const still = matchMedia('(prefers-reduced-motion: reduce)').matches
  if (themeSwitch) {
    const showTheme = (name) => themeSwitch.setAttribute('aria-checked', String(name === 'dark'))
    showTheme(document.documentElement.dataset.theme)
    themeSwitch.addEventListener('click', () => {
      const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'
      const apply = () => { document.documentElement.dataset.theme = next; showTheme(next) }
      if (document.startViewTransition && !still) {
        const box = themeSwitch.getBoundingClientRect()
        const root = document.documentElement
        root.style.setProperty('--tx', `${box.left + box.width / 2}px`)
        root.style.setProperty('--ty', `${box.top + box.height / 2}px`)
        root.classList.add('theme-wipe')
        document.startViewTransition(apply).finished.finally(() => root.classList.remove('theme-wipe'))
      } else apply()
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

  // --- Reading progress ring for the TOC -----------------------------------------------
  const initProgressRing = () => {
    const article = document.querySelector('article')
    const ring = document.querySelector('.progress-ring-circle')
    if (!article || !ring) return
    
    const updateRing = () => {
      const scrollTop = article.scrollTop
      const scrollHeight = article.scrollHeight - article.clientHeight
      const progress = scrollHeight > 0 ? scrollTop / scrollHeight : 0
      const radius = 18
      const circumference = 2 * Math.PI * radius
      const offset = circumference * (1 - progress)
      ring.style.strokeDashoffset = offset.toString()
    }
    
    article.addEventListener('scroll', updateRing)
    addEventListener('resize', updateRing)
    updateRing()
  }
  
  // Initialize reading progress ring after DOM is ready
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    initProgressRing()
  } else {
    document.addEventListener('DOMContentLoaded', initProgressRing)
  }

  // --- Page transitions with Motion --------------------------------------------------
  // Motion loaded via CDN in template: motion@12 or GSAP via loadMotion().
  // A third-party library (motion or GSAP) is used for fluid page transitions
  // and sidebar expand/collapse animations, so the reader is not disturbed
  // by ugly jolts or screen shaking between pages.
  const initPageTransitions = async () => {
    if (!window.loadMotion) {
      console.log('Motion not loaded, using CSS transitions only')
      return
    }
    await window.loadMotion()
    if (!window.Motion && !window.GSAP) {
      console.log('Motion not loaded, using CSS transitions only')
      return
    }
    
    // Iris wipe transition (Motion)
    if (window.Motion) {
      document.addEventListener('astro:page-load', () => {
        const { animate } = window.Motion
        const overlay = document.createElement('div')
        overlay.style.position = 'fixed'
        overlay.style.top = '0'
        overlay.style.left = '0'
        overlay.style.width = '100%'
        overlay.style.height = '100%'
        overlay.style.backgroundColor = 'var(--bg)'
        overlay.style.zIndex = '9999'
        overlay.style.clipPath = 'circle(0% at var(--tx, 50%) var(--ty, 50%))'
        document.body.appendChild(overlay)
         
        const centerX = window.innerWidth / 2
        const centerY = window.innerHeight / 2
         
        animate(overlay, {
          clipPath: 'circle(150% at var(--tx, 50%) var(--ty, 50%) )'
        }, {
          duration: 0.6,
          easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
        })
         
        setTimeout(() => {
          document.body.removeChild(overlay)
          delete document.body.dataset.theme
        }, 700)
      })
    }
     
    // GSAP fallback: smooth page transitions
    if (window.GSAP) {
      const { gsap } = window.GSAP
      document.addEventListener('astro:page-load', () => {
        gsap.to('body', {
          duration: 0.3,
          ease: 'power2.inOut',
          opacity: 0.9,
          onComplete: () => gsap.set('body', { opacity: 1 })
        })
      })
    }
  }
  
  // --- Sidebar group animations ------------------------------------------------------
  // Smooth expand/collapse of sidebar section groups (Motion or GSAP)
  const initSidebarGroups = () => {
    const groups = $$('.side details.group')
    groups.forEach((group) => {
      group.addEventListener('toggle', () => {
        if (window.Motion && group.open) {
          const { animate } = window.Motion
          const content = group.querySelector('ul')
          if (content) {
            animate(content, { height: content.scrollHeight }, {
              duration: 0.3,
              easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
              fill: 'forwards'
            })
          }
        } else if (window.GSAP) {
          const { gsap } = window.GSAP
          const content = group.querySelector('ul')
          if (content) {
            gsap.to(content, {
              duration: 0.3,
              height: group.open ? content.scrollHeight : 0,
              ease: 'power2.inOut'
            })
          }
        }
      })
    })
  }
  
  initSidebarGroups()

  // --- TOC rail spring animation ------------------------------------------------------
  const initTOCRail = () => {
    const links = $$('.toc a')
    if (!links.length) return
    
    links.forEach((link) => {
      link.addEventListener('click', (e) => {
        e.preventDefault()
        const target = document.getElementById(link.getAttribute('href').slice(1))
        if (!target) return
        
        const start = window.pageYOffset
        const end = target.getBoundingClientRect().top + window.pageYOffset
        const distance = end - start
        const duration = 800
        let startTime = null
        
        const ease = (t) => 0.5 - Math.cos(t * Math.PI) / 2
        
        const animate = (currentTime) => {
          if (!startTime) startTime = currentTime
          const elapsed = currentTime - startTime
          const progress = Math.min(elapsed / duration, 1)
          const easeProgress = ease(progress)
          window.scrollTo(0, start + distance * easeProgress)
          
          if (progress < 1) {
            requestAnimationFrame(animate)
          } else {
            link.classList.add('on')
          }
        }
        
        requestAnimationFrame(animate)
      })
    })
  }
  
  initTOCRail()

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
