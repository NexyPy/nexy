import { useState } from "react";
import { Area, AreaChart, CartesianGrid, XAxis, YAxis } from "recharts";
import type { Day } from "@nexy/actions";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { type ChartConfig, ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { count, day, money } from "@/lib/format";

type Measure = "revenue" | "orders";

const MEASURES: Record<Measure, { title: string; of: (d: Day) => number; text: (value: number) => string }> = {
  revenue: { title: "Revenue", of: (d) => d.revenue_cents / 100, text: (dollars) => money(dollars * 100) },
  orders: { title: "Orders", of: (d) => d.orders, text: count },
};

function best(daily: Day[], measure: Measure): string {
  const { of, text } = MEASURES[measure];
  const top = daily.reduce((found, d) => (of(d) > of(found) ? d : found), daily[0]);
  return top ? `Best day: ${day(top.day)}, ${text(of(top))}` : "";
}

export function RevenueChart({ daily }: { daily: Day[] }) {
  const [measure, setMeasure] = useState<Measure>("revenue");
  const { title, of, text } = MEASURES[measure];
  const config = { value: { label: title, color: "var(--chart-1)" } } satisfies ChartConfig;
  const rows = daily.map((d) => ({ day: d.day, value: of(d) }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title} per day</CardTitle>
        <CardDescription>{best(daily, measure)}</CardDescription>
        <CardAction>
          <ToggleGroup
            type="single"
            variant="outline"
            size="sm"
            value={measure}
            onValueChange={(next) => next && setMeasure(next as Measure)}
            aria-label="Measure"
          >
            <ToggleGroupItem value="revenue" className="px-3">Revenue</ToggleGroupItem>
            <ToggleGroupItem value="orders" className="px-3">Orders</ToggleGroupItem>
          </ToggleGroup>
        </CardAction>
      </CardHeader>
      <CardContent className="px-2 sm:px-6">
        <ChartContainer config={config} className="aspect-auto h-64 w-full">
          <AreaChart accessibilityLayer data={rows} margin={{ left: 4, right: 12 }}>
            <defs>
              <linearGradient id="fill-value" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--color-value)" stopOpacity={0.5} />
                <stop offset="95%" stopColor="var(--color-value)" stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <CartesianGrid vertical={false} />
            <XAxis dataKey="day" tickLine={false} axisLine={false} tickMargin={8} minTickGap={32} tickFormatter={day} />
            <YAxis tickLine={false} axisLine={false} width={64} tickFormatter={(value: number) => text(value)} />
            <ChartTooltip
              cursor={false}
              content={
                <ChartTooltipContent
                  indicator="dot"
                  labelFormatter={(value) => day(String(value))}
                  formatter={(value) => (
                    <div className="flex w-full justify-between gap-4">
                      <span className="text-muted-foreground">{title}</span>
                      <span className="font-mono font-medium tabular-nums">{text(Number(value))}</span>
                    </div>
                  )}
                />
              }
            />
            <Area dataKey="value" type="monotone" fill="url(#fill-value)" stroke="var(--color-value)" strokeWidth={2} />
          </AreaChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
