<script lang="ts">
  // The root layout writes the whole document: the header, the list of notes, and the page beside
  // it. On a phone the list is the home page and a note takes the whole screen.
  import type { Snippet } from "svelte";
  import { pathname } from "@nexy/client";

  import Header from "@/components/header.svelte";
  import NoteList from "@/components/note-list.svelte";

  let { children }: { children?: Snippet } = $props();

  const home = $derived($pathname === "/");
</script>

<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="Margin, a notebook that saves while you type, in Markdown." />
    <title>Margin</title>
    <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="" />
    <link
      href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500..700&family=Geist:wght@400..600&family=Geist+Mono:wght@400..500&display=swap"
      rel="stylesheet"
    />
    <!-- Applied before the first paint, so a dark page never flashes white. -->
    <style>html{background:#ffffff;color-scheme:light}html.dark{background:#0a0a0a;color-scheme:dark}</style>
    <script>try { var saved = localStorage.getItem("nexy-theme"); var dark = saved ? saved === "dark" : matchMedia("(prefers-color-scheme: dark)").matches; document.documentElement.classList.toggle("dark", dark); } catch (error) {}</script>
  </head>
  <body class="flex h-dvh flex-col">
    <Header />
    <div class="mx-auto my-4 flex min-h-0 w-[72rem] max-w-[calc(100%-2rem)] flex-1 border border-border">
      <aside
        aria-label="Notes"
        class="min-h-0 flex-col border-border md:flex md:w-80 md:shrink-0 md:border-r {home ? 'flex w-full' : 'hidden'}"
      >
        <NoteList />
      </aside>
      <main class="min-h-0 min-w-0 flex-1 flex-col {home ? 'hidden md:flex' : 'flex'}">{@render children?.()}</main>
    </div>
  </body>
</html>
