// The revenue, or the orders, of each day of the window, drawn in SVG. It reads /api/revenue in the
// browser, so the numbers above it come with the page and the chart follows a moment later.
import { useEffect, useRef, useState, type KeyboardEvent, type PointerEvent } from "react";
import { useFetch } from "@nexy/client";

type Point = { day: string; revenue_cents: number; orders: number };
type Series = { days: number; channel: string; series: Point[] };
type Measure = "revenue" | "orders";

const HEIGHT = 240;
const PAD = { top: 12, right: 8, bottom: 26, left: 52 };
const PLOT_H = HEIGHT - PAD.top - PAD.bottom;

/** The width the chart is given, in CSS pixels: the SVG is drawn at that size, so its text stays readable. */
function useWidth() {
  const box = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(720);
  useEffect(() => {
    if (!box.current) return;
    const watch = new ResizeObserver(([entry]) => setWidth(Math.max(Math.round(entry.contentRect.width), 240)));
    watch.observe(box.current);
    return () => watch.disconnect();
  }, []);
  return [box, width] as const;
}

const value = (point: Point, measure: Measure) =>
  measure === "revenue" ? point.revenue_cents / 100 : point.orders;

const shown = (amount: number, measure: Measure) =>
  measure === "revenue"
    ? amount.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 })
    : amount.toLocaleString("en-US");

const label = (day: string) =>
  new Date(`${day}T00:00:00`).toLocaleDateString("en-US", { month: "short", day: "numeric" });

/** A round top for the axis, at or above the largest value, that four lines divide into whole numbers. */
function ceiling(largest: number): number {
  if (largest <= 4) return 4;
  const power = 10 ** Math.floor(Math.log10(largest));
  const tops = [1, 2, 4, 6, 8, 10].map((step) => step * power).filter((top) => top % 4 === 0);
  return tops.find((top) => top >= largest) ?? 12 * power;
}

function Toggle({ measure, onChange }: { measure: Measure; onChange: (next: Measure) => void }) {
  const options: [Measure, string][] = [["revenue", "Revenue"], ["orders", "Orders"]];
  return (
    <div role="radiogroup" aria-label="Measure" className="flex rounded-lg border border-border p-0.5">
      {options.map(([name, text]) => (
        <button
          key={name}
          type="button"
          role="radio"
          aria-checked={measure === name}
          onClick={() => onChange(name)}
          className="min-h-8 rounded-md px-3 text-sm text-foreground-second aria-checked:bg-foreground aria-checked:text-background"
        >
          {text}
        </button>
      ))}
    </div>
  );
}

function Plot({ points, measure }: { points: Point[]; measure: Measure }) {
  const [active, setActive] = useState<number | null>(null);
  const [box, WIDTH] = useWidth();
  const PLOT_W = WIDTH - PAD.left - PAD.right;
  const top = ceiling(Math.max(...points.map((point) => value(point, measure))));
  const x = (index: number) => PAD.left + (points.length > 1 ? (index / (points.length - 1)) * PLOT_W : PLOT_W / 2);
  const y = (amount: number) => PAD.top + PLOT_H - (amount / top) * PLOT_H;
  const line = points.map((point, index) => `${index ? "L" : "M"}${x(index)},${y(value(point, measure))}`).join("");
  const area = `${line}L${x(points.length - 1)},${PAD.top + PLOT_H}L${x(0)},${PAD.top + PLOT_H}Z`;
  const ticks = [0, 0.25, 0.5, 0.75, 1].map((part) => part * top);
  const marks = WIDTH < 420 ? [0, points.length - 1] : [0, Math.floor((points.length - 1) / 2), points.length - 1];
  const anchors = marks.length === 2 ? ["start", "end"] : ["start", "middle", "end"];

  function follow(event: PointerEvent<SVGSVGElement>) {
    const box = event.currentTarget.getBoundingClientRect();
    const at = ((event.clientX - box.left) / box.width) * WIDTH;
    const index = Math.round(((at - PAD.left) / PLOT_W) * (points.length - 1));
    setActive(Math.min(Math.max(index, 0), points.length - 1));
  }

  function step(event: KeyboardEvent<SVGSVGElement>) {
    const moves: Record<string, number> = { ArrowLeft: -1, ArrowRight: 1 };
    if (!(event.key in moves)) return;
    event.preventDefault();
    const from = active ?? points.length - 1;
    setActive(Math.min(Math.max(from + moves[event.key], 0), points.length - 1));
  }

  const point = active === null ? null : points[active];
  return (
    <div ref={box} className="relative">
      <svg
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        width={WIDTH}
        height={HEIGHT}
        className="block max-w-full touch-pan-y select-none outline-none focus-visible:ring-2 focus-visible:ring-foreground/40"
        role="img"
        tabIndex={0}
        aria-label={`${measure === "revenue" ? "Revenue" : "Orders"} per day. Use the left and right arrows to read each day.`}
        onPointerMove={follow}
        onPointerLeave={() => setActive(null)}
        onKeyDown={step}
        onBlur={() => setActive(null)}
      >
        {ticks.map((tick) => (
          <g key={tick}>
            <line x1={PAD.left} x2={WIDTH - PAD.right} y1={y(tick)} y2={y(tick)} className="stroke-border" />
            <text x={PAD.left - 8} y={y(tick)} dy="0.32em" textAnchor="end" className="fill-foreground-second text-[11px] tabular-nums">
              {shown(tick, measure)}
            </text>
          </g>
        ))}
        {marks.map((index, place) => (
          <text key={place} x={x(index)} y={HEIGHT - 6} textAnchor={anchors[place]} className="fill-foreground-second text-[11px]">
            {label(points[index].day)}
          </text>
        ))}
        <path d={area} className="fill-chart/15" />
        <path d={line} fill="none" strokeWidth={2} strokeLinejoin="round" className="stroke-chart" />
        {point && active !== null && (
          <g>
            <line x1={x(active)} x2={x(active)} y1={PAD.top} y2={PAD.top + PLOT_H} className="stroke-foreground-second" strokeDasharray="3 3" />
            <circle cx={x(active)} cy={y(value(point, measure))} r={4.5} className="fill-chart stroke-background-second" strokeWidth={2} />
          </g>
        )}
      </svg>
      <p aria-live="polite" className="mt-2 min-h-5 text-sm text-foreground-second">
        {point ? (
          <>
            <span className="text-foreground">{label(point.day)}</span>: {shown(point.revenue_cents / 100, "revenue")} from{" "}
            {point.orders.toLocaleString("en-US")} orders
          </>
        ) : (
          "Point at the chart, or focus it and use the arrows, to read a day."
        )}
      </p>
    </div>
  );
}

export function RevenueChart({ days, channel }: { days: string; channel: string }) {
  const query = new URLSearchParams(channel ? { days, channel } : { days });
  const { data, error, pending, refresh } = useFetch<Series>(`/api/revenue/?${query}`);
  const [measure, setMeasure] = useState<Measure>("revenue");
  const points = data?.series ?? [];
  const best = points.reduce<Point | null>((top, point) => (!top || value(point, measure) > value(top, measure) ? point : top), null);
  const empty = !best || value(best, measure) === 0;

  return (
    <figure>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <figcaption>
          <h2 id="chart-title" className="font-display text-lg font-semibold">
            {measure === "revenue" ? "Revenue" : "Orders"} per day
          </h2>
          <p className="text-sm text-foreground-second">
            {best && !empty ? `Best day: ${label(best.day)}, ${shown(value(best, measure), measure)}` : `The last ${days} days${channel ? `, ${channel}` : ""}`}
          </p>
        </figcaption>
        <Toggle measure={measure} onChange={setMeasure} />
      </div>
      <div className="mt-4">
        {error ? (
          <div className="grid h-60 place-items-center text-center text-sm">
            <p>
              The chart did not load.{" "}
              <button type="button" onClick={() => refresh()} className="min-h-10 underline underline-offset-4">Try again</button>
            </p>
          </div>
        ) : pending && !data ? (
          <div className="h-60 animate-pulse rounded-lg bg-border/60" aria-label="Loading the chart" />
        ) : empty ? (
          <p className="grid h-60 place-items-center text-sm text-foreground-second">No sale in these days.</p>
        ) : (
          <Plot points={points} measure={measure} />
        )}
      </div>
    </figure>
  );
}
