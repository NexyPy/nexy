import { MinusIcon, TrendingDownIcon, TrendingUpIcon } from "lucide-react";
import type { Totals } from "@nexy/actions";
import { Badge } from "@/components/ui/badge";
import { Card, CardAction, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { type Trend, change, count, exact, money } from "@/lib/format";

type Kpi = { label: string; value: (totals: Totals) => number; text: (value: number) => string };

const KPIS: Kpi[] = [
  { label: "Revenue", value: (t) => t.revenue_cents, text: money },
  { label: "Orders", value: (t) => t.orders, text: count },
  { label: "Average order", value: (t) => t.average_cents, text: exact },
  { label: "Units sold", value: (t) => t.units, text: count },
];

const TRENDS: Record<Trend, { icon: typeof MinusIcon; color: string }> = {
  up: { icon: TrendingUpIcon, color: "text-up" },
  down: { icon: TrendingDownIcon, color: "text-down" },
  flat: { icon: MinusIcon, color: "text-muted-foreground" },
};

function Change({ now, before }: { now: number; before: number }) {
  const found = change(now, before);
  if (!found) return null;
  const { icon: Icon, color } = TRENDS[found.trend];
  return (
    <Badge variant="outline" className={color}>
      <Icon />
      {found.text}
    </Badge>
  );
}

export function KpiCards({ totals, before, days }: { totals: Totals; before: Totals; days: number }) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {KPIS.map((kpi) => (
        <Card key={kpi.label} className="@container/card">
          <CardHeader>
            <CardDescription>{kpi.label}</CardDescription>
            <CardTitle className="text-2xl font-semibold tabular-nums">{kpi.text(kpi.value(totals))}</CardTitle>
            <CardAction>
              <Change now={kpi.value(totals)} before={kpi.value(before)} />
            </CardAction>
          </CardHeader>
          <CardFooter className="text-sm text-muted-foreground">
            Against the {days} days before: {kpi.text(kpi.value(before))}
          </CardFooter>
        </Card>
      ))}
    </div>
  );
}
