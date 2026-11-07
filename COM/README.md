# COM

Everything we say in public, in one folder: the posts, the articles, the numbers behind them, and
the two documents that decide how they read and how they look.

`COM/` is not a site. Nothing here is served, built or deployed. An item is written here, checked
here, then pasted into LinkedIn, Bluesky, Mastodon or Dev.to by hand. The publishing itself stays
manual on purpose: three networks, three sets of tokens, and no repository should hold them.

## One folder, one item

```
COM/posts/2026-11-page-in-1-4-ms/
  post.md          English caption, frontmatter between +++
  post.fr.md       the same item in French
  image.png        the media: image.png, carousel/*.png, or video.mp4 + transcript.md
```

The folder is named `YYYY-MM-<slug>`: the month it is planned for, then the words a reader would
type. `2026-11-page-in-1-4-ms` is a folder we can still find in a year; `post-final-2` is not.

The language is in the file name (`post.md`, `post.fr.md`, `post.pt.md`), never in the folder. A
French caption is an item of its own: it is published on its own day, in its own networks, and it is
marked as sent on its own.

Media lives next to the words and the folder decides the kind, so nobody has to declare it:

| in the folder | kind | what a reader gets |
|---|---|---|
| `image.png` | image | one screenshot or one card, 1200×675 or 1080×1350 |
| `carousel/*.png` | carousel | a document, read one card at a time |
| `video.mp4` + `transcript.md` | video | a silent-first clip, and the text of what is said |
| nothing | text | a caption alone; the checker warns, it does not block |

One kind per folder. Two kinds in one folder is an error, because a post that ships both has never
been published as either.

## The frontmatter

A post or a blog starts with `+++`, then TOML, then `+++`, then the words. The body is the caption
on a network and the text of a blog; there is no second place to write it.

```toml
+++
date = 2026-11-06
platforms = ["linkedin"]        # posts only: linkedin, bluesky, mastodon
link = "https://nexypy.github.io/nexy/docs/"   # the tagged link goes in the first comment
cta = "comment"                 # link | comment | none
ask = "report"                  # none | run | report | contribute — never star, never follow
proof = ["compile-2026-11.md"]  # every number in the body needs one of these
alt = "A terminal: 1.4 ms median over 25 runs."   # one string per image or card
title = "1.4 ms"                # optional on a post, shown above a video
+++
```

A blog adds `description` (160 characters at most), `tags` (one to four), `canonical` and `cover`:

```toml
+++
date = 2026-11-13
title = "Why a route is a file"
description = "One file, one page: what file-based routing buys and what it costs."
tags = ["python", "fastapi", "routing"]
canonical = "https://nexypy.github.io/nexy/docs/views/routes/"
cover = "cover.png"
proof = ["compile-2026-11.md"]
+++
```

`canonical` is not decoration. A blog that repeats a page of the docs without pointing at it makes
two pages compete for the same sentence, and the docs lose.

## The four experiences

Every item has to work four times, because people meet it four ways.

**The reader** reads the first two lines in a feed. Those two lines stand alone: a fact, a number,
or a sentence that makes the third line worth the tap. Plain English, no teaser, no "let that sink
in". If the first line needs the second to make sense, it is not a first line.

**The developer** gets a command and a number they can reproduce in under a minute: `nx dev`, then
the same measurement, on their machine. A claim nobody can check is a marketing sentence, and this
folder does not hold marketing sentences.

**The watcher** sees a card at feed size, on a phone, with the sound off. One idea per card, big
type, and a reason to swipe. The checker assembles the cards at 270 px wide into
`build/com/<slug>-feed.png` for exactly this: if it cannot be read there, it cannot be published.

**The listener** gets the video muted. The first frame says what it is, the transcript says what is
said, and no music plays under a voice. Music under speech is how a clip announces that nobody
recorded it for a human.

## What the checker refuses

`python scripts/publish_social.py --check` stops on the mechanical ones:

- a folder that is not `YYYY-MM-<slug>`, or a language the site does not publish;
- an unknown frontmatter field (a typo in `proof` should not silently drop the proof);
- a caption over the limit of the network it names;
- a card that is not the same size as the others, or not 1:1 or 4:5, or under 400 px wide;
- a number with no dated file in `COM/proof/`;
- a hashtag, an emoji, a hook over 90 characters;
- a phrase from the banned list in `VOICE.md`, a "this is why" formula, a call for engagement
  before the post has given anything;
- a `link` that appears in the caption;
- two `ask` in four posts — one invitation in four at most, or it becomes a campaign;
- a blog without a title, a description, a canonical, one to four tags, or a cover.

It only warns on the ones a machine judges badly: readability above grade 10, two paragraphs of the
same length, a post with no media, a video with no title. A rule that is sometimes wrong is a
nuisance; a rule that blocks on a guess gets switched off within a month.

## The commands

```bash
python scripts/publish_social.py --list                     # every item, its networks, what went out
python scripts/publish_social.py --check                    # the errors and the warnings above
python scripts/publish_social.py --pack                     # every carousel into build/com/
python scripts/publish_social.py --pack 2026-11-six-routes  # one carousel
python scripts/publish_social.py --dry-run --lang fr        # exactly what a human then pastes
```

`--pack` writes `<slug>.pdf` (the document LinkedIn reads) and `<slug>-feed.png` (the same cards at
270 px, the two-second test). Both go to `build/com/`, which is git-ignored: the cards are the
source, the PDF is an artifact. The PDF is assembled from the PNGs without re-encoding them, so
what LinkedIn shows is byte-for-byte the card that was checked.

`--dry-run` prints the caption and its tagged link and stops. It has no token, no network call and
no side effect; publishing is a human pasting into a browser.

## Where the words and the look live

- `VOICE.md` — how a post reads: five decisions, the open door, what we show instead of claiming,
  the ladder from 330 to 5 000 installs a month, and the competitors we never name.
- `BRAND.md` — how it looks: the monogram, the two typefaces, the palette, the card grid, and the
  seven looks we refuse because every generated landing page has them.
- `proof/` — one dated file per number. A claim without one is refused by the checker.
- `posts/`, `blogs/` — the items themselves.

## What never ships

A promise instead of a measurement. A community we claim instead of a community we can show.
A star asked for in the imperative. A number without a date on it. Anything we would have to take
back in a comment under our own post.
