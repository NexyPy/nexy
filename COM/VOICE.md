# VOICE

How a post from this repository reads. Five decisions, then the parts that are easy to get wrong.

The reader we write for is one person: a TypeScript developer who already runs a Python API, or a
Python developer who already runs a React or Vue front end. They have a `docker-compose.yml` with
two services and a CORS block in it, and they have read enough framework announcements to recognise
one from the first line. Everything below exists to keep that person reading.

## Five decisions

**One person, first person.** A post is signed by whoever did the work, in `je`/`I`, with a name and
nothing else: no role, no title, no emoji after it. `we` is allowed the day a second named person
did the work in the post. Until then it is a lie that a reader cannot check, and readers check.

**A number, or nothing.** Every figure carries a dated file in `COM/proof/`: the machine, the
command, the raw runs, the date. If a number has no proof, it waits for the benchmark, and the post
is written without it. `47 ms` with a file behind it is worth more than `blazing fast` with none,
even when `47 ms` is the smaller number.

**One item, one idea.** Two ideas in one post means the reader keeps neither. The second idea
becomes the second item, and the item that comes first is the one a stranger can act on with one
command.

**Show the work.** A post carries a command, a diff, a terminal, a screenshot of a real file, or it
carries nothing visual at all. Code and typography. No illustration, no abstract shape, no drawing
of a network of dots: those exist because the writer had no artefact to show.

**Admit the limit.** The strongest sentence in a technical post is the one that says what does not
work yet, in the same voice as the rest. `No migration from Next.js yet, the router differs too
much` costs one reader and buys the trust of the other hundred, permanently.

## The four experiences

Every item is met four ways, and all four get written before it ships.

**Reader.** Two lines that stand alone. A fact, a number, a question someone actually asked. Not
"Ever wondered why…", not a teaser for the third line. If line one and line two can be swapped
without loss, both are filler. Plain English, no `delve`, no `seamless`, no `unlock`: the checker
refuses about thirty of those words, and the list in the code is the list.

**Developer.** A command and a reproducible number, under sixty seconds, in the post or in the
first comment. `nx dev`, then the same measurement on their machine. When someone runs it and gets
`2.1 ms` where we got `1.4 ms`, the post worked: they now know what the number depends on.

**Watcher.** Cards are read at 270 px wide, on a phone, sound off, one hand. One idea per card, six
to nine words of headline, type big enough to read without zooming. `--pack` writes the same cards
at feed size so this is checked, not assumed.

**Listener.** Video starts muted, so the first frame has to say what the clip is. A voice, a real
one, no music under it, no text-to-speech, and a `transcript.md` next to the file. Music under
speech is the sound of a clip nobody recorded for a human.

## The open door

We want stars, forks and contributors. We are not going to ask for them in the imperative, because a
post that ends with `drop a star` has taken the reader's time and given back a request.

What we do instead:

- The post gives something first: a number, a command, a template repository, a diff. The thing is
  already useful before anyone clicks anything.
- The door is published, once. `CONTRIBUTING.md` with its rules, the `good first issue` label, the
  hook that refuses an AI co-author trailer, the migration demo. A `link` in the first comment
  points at it. That is the whole invitation.
- `ask` is how the invitation is written in the frontmatter, and it is never `star` or `follow`:
  `run` asks someone to run a command, `report` asks for their number, `contribute` asks for a pull
  request on a named issue, `none` asks nothing. `report` and `contribute` need a proof file: a
  question about a number nobody can reproduce is not a question.
- At most one post in four carries an `ask`, which `voice.density()` enforces over the published
  dates. Past that the reader stops seeing posts and starts seeing a campaign.
- `fork` is never asked. A migration demo is shipped as a template, marked `is_template`, and people
  fork it because it is easier than writing the thing from scratch. Wanting the fork is not a
  reason to ask for it.

## Community, shown not claimed

The repository has one maintainer. `our community` is therefore not a sentence we are allowed to
write, and neither is `a growing community of contributors`, `built by the community`, or a
testimonial from someone who has not merged anything.

What we publish instead, all of it checkable from outside:

- `CONTRIBUTING.md`: one commit one unit, Conventional Commits, a maintainer review before merge,
  no force-push on `main`.
- `.githooks/commit-msg`, which refuses an AI co-author trailer before the commit exists, so the
  contributor graph stays a graph of humans.
- The `good first issue` label, and issues written so that the first comment is a file and a test.
- `CHANGELOG.md`, dated, with the version that is on PyPI.
- `CODE_OF_CONDUCT.md` and `SECURITY.md`, including how to report something privately.
- The open and closed counts, the merge count, and how long an issue usually waits. Those are the
  only numbers about the community we will put in a post.

`our community` becomes available the day three people outside the maintainer have a merged pull
request, and `community-*.md` in `COM/proof/` shows it. Not before.

## The ladder

Three numbers, each one a month of work. They are the only growth targets we have, and they are
small on purpose: a target nobody can hit by accident is a target we can plan against.

| step | PyPI installs / month | what has to be true |
|---|---|---|
| today | 330 | one post a week, one article every fifteen days, the migration demo published |
| 1 000 | three times today | the demo has been forked by people we do not know, and two segment queries bring a docs page in the top ten |
| 5 000 | fifteen times today | someone other than the maintainer answers a question in the discussions, and an integration shows up in a project we have never heard of |

Installs are the reach; they are not the goal. The goal is to be the answer when someone in the
segment asks "React and FastAPI, without the glue": three queries, one of them a comparison, one a
how-to, one a job someone is trying to finish on a Friday. We measure our share of the answer by
where the documentation page sits for those three, and by which `utm_campaign` the visits came from.
GitHub Pages keeps no access log, so every link a post sends is tagged: untagged traffic cannot be
judged, and a channel that cannot be judged cannot be cut.

## Competitors we never name

A post never names another framework. Not Next.js, not Django, not Laravel, not Remix. Three
reasons, in order of weight:

1. A named competitor gets the search, the notification and the reply. We would be renting their
   audience to say something they can answer in one line.
2. A comparison in a feed is read as an attack even when it is sourced. The reader who is happy with
   their tool leaves with a reason to defend it.
3. The comparison already exists where it belongs: `docs/coming-from/` has one page per framework,
   written for the person who typed that framework's name plus `alternative`. It is calm, it links
   to what each tool does better, and it wins the query by answering it.

So a post says what Nexy does, in the words of the thing it replaces: `one origin for your frontend
and your FastAPI API`. The reader supplies the name of what they are leaving; we never do. The
category sentence is the README, verbatim, and nothing else: **The fullstack Python meta-framework.
FastAPI on the server, Vite on the client, one file per page.**

## Words

Banned in a caption, refused by `voice.py`: `delve`, `seamless`, `game-chang`, `cutting-edge`,
`revolutioni`, `unlock`, `unleash`, `elevate`, `empower`, `robust`, `state-of-the-art`, `in today's`,
`dive into`, `deep dive`, `harness`, `transformative`, `supercharge`, `effortless`, `world-class`,
`next-level`, `best-in-class`, `tapestry`, `testament`, `the future of`, `journey`.

Refused as formulas: `this is why`, `it's not just`, `isn't just`, `not only … but also`,
`here's why`, `what if I told you`.

Refused as soliciting: `drop a star`, `star the repo`, `fork us`, `please share`, `don't forget to`,
`if you like this`, `support the project`, `spread the word`, `help us grow`.

Also refused: hashtags (posts without them reach further, and a wall of them reads as a bot), emoji
of any kind, and a first line over 90 characters.

What is left after all that is shorter, plainer and easier to write than the version that had those
words in it.
