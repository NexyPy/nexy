import type { Share } from "@nexy/actions";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { money } from "@/lib/format";
import { cn } from "@/lib/utils";

// Every channel, whichever one the filter keeps: the chosen one is drawn, the others are dimmed.
export function ChannelCard({ channels, chosen }: { channels: Share[]; chosen: string }) {
  const total = channels.reduce((sum, share) => sum + share.revenue_cents, 0);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Revenue by channel</CardTitle>
        <CardDescription>Every channel, whatever the filter keeps</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        {channels.map((share) => {
          const percent = total ? Math.round((share.revenue_cents / total) * 100) : 0;
          return (
            <div key={share.name} className={cn("flex flex-col gap-1.5", chosen && chosen !== share.name && "opacity-50")}>
              <div className="flex items-baseline justify-between gap-2 text-sm">
                <span>{share.name}</span>
                <span className="tabular-nums">
                  <span className="font-medium">{money(share.revenue_cents)}</span>
                  <span className="ml-2 text-muted-foreground">{percent}%</span>
                </span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-muted">
                <div className="h-full rounded-full bg-chart-1" style={{ width: `${percent}%` }} />
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
