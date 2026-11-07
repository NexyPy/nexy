# proof/

One file per number we put in public. The checker refuses a caption that contains a digit without a
dated file here, and refuses a `proof` entry that does not exist.

The reason is narrow and practical: a number we cannot reproduce in a year is a number we will have
to take back in a comment, and taking a number back costs more than not having published it.

## The shape of a file

`<topic>-YYYY-MM.md`, where the month is the month of the measurement, not the month of the post. A
number measured in October can appear in a November post as long as the file says October.

Five sections, in this order:

1. **The claim**, in one sentence, as it will appear in public.
2. **The machine**: CPU, core count, RAM, OS, Python or Node version, and whether anything else was
   running.
3. **The command**, copy-pasteable, from a clean clone. No private script, no "internal benchmark".
4. **The raw runs**, not just the median: every measurement, or a link to the JSON that holds them.
   A median with no spread hides the one run that took 40 times longer.
5. **What this does not prove**. The limits, in our own words, before a reader finds them.

## Files here today

| file | the number it backs |
|---|---|
| `compile-2026-11.md` | a page compiles in 1.4 ms (median, 25 runs, Ryzen 5 4500U) |
| `metrics-2026-11.md` | the snapshot: stars, forks, issues, PyPI installs |
| `community-2026-11.md` | what can be shown about the community today, and what cannot |

A proof file is never edited after the fact. A new measurement is a new file, and the old one stays:
`compile-2026-12.md` next to `compile-2026-11.md` is how a number improves without the history being
rewritten.
