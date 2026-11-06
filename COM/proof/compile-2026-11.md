# A page compiles in about 1.6 ms

The claim, as it goes out: **an 87-line route with three component imports and a 380-iteration
loop compiles in 1.6 ms (median of 25 runs, Ryzen 5 4500U).**

## The machine

- AMD Ryzen 5 4500U, 6 cores, 6 GB RAM, Linux 7.0.0-42-generic.
- Python 3.13.15, nexy 2.2.2 (the release on PyPI on 2026-11-05).
- The laptop was otherwise idle: no build, no test suite, no second dev server. An editor and a
  browser were open, as they always are.

## The command

From a clean clone, in the example that has no frontend framework at all:

```bash
cd examples/FBR/web/basics/none
uv run python - <<'PY'
import statistics, time
from nexy.modules.compiler import Compiler

Compiler().compile("src/routes/index.nexy", "/tmp/page.html")  # warm-up
runs = []
for _ in range(25):
    start = time.perf_counter()
    Compiler().compile("src/routes/index.nexy", "/tmp/page.html")
    runs.append((time.perf_counter() - start) * 1000)
print(", ".join(f"{run:.2f}" for run in runs))
print(f"median {statistics.median(runs):.2f} ms, min {min(runs):.2f}, max {max(runs):.2f}")
PY
```

The warm-up run is not measured: it pays for imports, the config load and the Jinja environment.
What is measured is the work the dev server repeats when a file changes: parse the file, run its
frontmatter, render it, write the HTML.

## The raw runs, 2026-11-06

Run B, the command above, against nexy 2.2.2 installed from PyPI:

```
1.67, 1.51, 1.64, 1.65, 1.64, 1.68, 1.54, 1.58, 1.60, 1.77, 1.67, 1.58, 1.54, 1.51,
1.45, 1.48, 1.59, 1.57, 1.51, 1.51, 1.63, 1.76, 1.71, 1.69, 1.66
median 1.60 ms, min 1.45, max 1.77
```

Run C, same command, five minutes later:

```
1.99, 1.86, 2.18, 1.71, 1.91, 1.66, 1.49, 1.51, 1.60, 1.55, 1.56, 1.58, 1.62, 1.63,
1.60, 1.61, 1.62, 1.71, 1.63, 1.66, 1.94, 2.16, 1.88, 1.98, 2.34
median 1.66 ms, min 1.49, max 2.34
```

Run A, the same page compiled from the repository checkout instead of PyPI, with the same Python:

```
1.81, 1.34, 1.28, 1.30, 1.30, 1.61, 1.40, 1.30, 1.29, 1.30, 1.71, 1.33, 1.32, 1.32,
1.28, 1.66, 1.33, 1.30, 1.33, 1.38, 4.21, 1.32, 1.32, 1.63, 1.37
median 1.33 ms, min 1.28, max 4.21
```

## What this does not prove

- **It is not HMR.** This is the compile step alone. A browser reload also pays for the websocket
  message, Vite's module graph and the browser's own re-render, and none of that is in these
  numbers. The HMR figure will be published when it has been measured end to end, in a browser,
  with a timestamp.
- **It is one page, one machine.** A bigger page with more logic takes longer; a slower laptop
  takes longer. The spread between the three runs above (1.33 ms to 1.66 ms median) is the same
  command on the same hardware, so ±0.3 ms is noise, not a result.
- **Run A has an outlier at 4.21 ms.** One run in 25, on a laptop with a browser open. It is left in
  because removing it would make the table prettier and the number less true.
- **No memory figure.** Peak RSS during a compile was not measured, so no memory claim will be made
  from this file.
