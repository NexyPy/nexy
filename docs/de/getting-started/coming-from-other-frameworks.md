# Kommt aus einem anderen Rahmen

Nexy ist FastAPI plus dateibasiertes Routing, servergerenderte Seiten und optionale React-, Vue-, Svelte-, Solid- oder Preact-Inseln. Diese Seite stellt dar, was Sie bereits wissen.

## Von FastAPI

| FastAPI | Nexy |
|---|---|
| `@app.get("/users")` in einem Modul, das Sie importieren | `GET`-Funktion in `src/routes/users.py` |
| `app.include_router(router)` | der Dateipfad ist die URL; nichts zu registrieren |
| Pfadparameter `/users/{id}` | `src/routes/users/[id].py` |
| `Depends(...)` | immer noch `Depends(...)`: Handler sind FastAPI Handler |
| Jinja2 `TemplateResponse` | eine `.nexy`-Seite neben dem Endpunkt |
| Laufen mit `uvicorn main:app` | `nx dev`, dann `nx build && nx start` |

Alles unter `src/routes/*.py` ist normal FastAPI: Abhängigkeiten, Pydantic Modelle, Middleware und `/docs` funktionieren weiterhin.

## Von Next.js

| Next.js | Nexy |
|---|---|
| `app/page.tsx` | `src/routes/index.tsx` oder `index.nexy` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug].tsx` |
| `app/layout.tsx` (besitzt `<html>`) | `src/routes/layout.tsx` mit `useCSR = True` (React) oder `src/routes/layout.nexy` im Servermodus |
| verschachtelt `layout.tsx` | verschachtelt `layout.tsx` / `layout.vue` / `layout.svelte` im Client-Modus, verschachtelt `layout.nexy` im Server-Modus |
| `use client` Komponenten auf einer Serverseite | [Inseln](../rendering/islands.md) im Servermodus |
| Routenhandler `route.ts` | `src/routes/api/x.py`, geschrieben in Python |
| `(group)`-Ordner | gleich: `(group)/` |
| Serveraktionen | [`@Action`](../guides/actions.md) Funktionen, die aus einem Formular oder als typisierte Clientfunktionen aufgerufen werden |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

Das Backend ist Python, sodass Ihre API Code mit Ihren Daten und ML-Arbeit teilt. Client-Komponenten hydratisieren als Inseln statt als ganzseitiger React Baum.

## Von Express- oder Node-Backends

| Express | Nexy |
|---|---|
| `app.get("/users/:id", handler)` | `src/routes/users/[id].py` mit `async def GET(id)` |
| `app.use(middleware)` | FastAPI Middleware, registriert von `nexyconfig.py` |
| `res.json(obj)` | Gibt ein Diktat oder ein Pydantic-Modell zurück |
| EJS/Pug-Ansichten | `.nexy` (Jinja2) Seiten |
| `npm run dev` | `nx dev` |

## Auswahl eines Routers

| Benutzen | Wann |
|---|---|
| Dateibasierter Router | aus Dateien zugeordnete Seiten und Endpunkte; die Standardeinstellung |
| Modularer Router | Controller, Module und Abhängigkeitsinjektion im NestJS-Stil |

Beide basieren auf `nx new` und werden durch dieselben End-to-End-Tests abgedeckt. Siehe [Routing](../routing/README.md) und [Modulares Routing](../routing/modular/README.md).

## Wohin als nächstes

- [Schnellstart](quick-start.md): Erstellen Sie ein Projekt und führen Sie es aus
- [Projektstruktur](project-structure.md): Wohin jede Datei gehört
- [Routing](../routing/README.md): Wählen Sie den Router aus
