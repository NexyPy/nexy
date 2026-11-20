---
title: A page that needs no JavaScript to be read
date: 2026-11-14
tags: nexy, performance
summary: How the pages of this blog stay readable with scripts turned off, and the one script they keep.
---

Turn JavaScript off and reload this page: the text, the links and the table of contents are all
still here. The pages are `.nexy` files, and Nexy turns each one into HTML on the server.

## The one script

The theme switch in the header is the only part that needs a script: it remembers the choice of
the reader in `localStorage`. A small inline script in the layout applies that choice before the
first paint, so a dark page never flashes white.

## What it costs

Nothing on the client. The server reads the posts once at startup and keeps them in memory, so a
page is a template filled with values already at hand.
