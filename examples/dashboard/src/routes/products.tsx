import { useSearchParams } from "@nexy/client";
import { products } from "@nexy/actions";
import { Filters } from "@/components/filters";
import { Placeholder, Problem } from "@/components/page-state";
import { Card, CardContent } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { count, money, span } from "@/lib/format";
import { useLoaded } from "@/lib/load";
import { channelOf, periodOf } from "@/lib/query";
import { cn } from "@/lib/utils";

export default function Products() {
  const search = useSearchParams();
  const days = periodOf(search);
  const channel = channelOf(search);
  const { data, error, stale } = useLoaded(() => products({ days, channel }), `${days}/${channel}`);
  const total = data?.products.reduce((sum, share) => sum + share.revenue_cents, 0) ?? 0;

  return (
    <>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-muted-foreground">
          {data ? span(data.period.first, data.period.last) : "Loading the products..."}
        </p>
        <Filters />
      </div>
      <Problem message={error} />
      {data ? (
        <Card className={cn("py-0 transition-opacity", stale && "opacity-60")}>
          <CardContent className="px-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="pl-4">Product</TableHead>
                  <TableHead className="text-right">Units</TableHead>
                  <TableHead className="text-right">Revenue</TableHead>
                  <TableHead className="w-1/4 pr-4">Share</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.products.map((share) => {
                  const percent = total ? Math.round((share.revenue_cents / total) * 100) : 0;
                  return (
                    <TableRow key={share.name}>
                      <TableCell className="pl-4 font-medium">{share.name}</TableCell>
                      <TableCell className="text-right tabular-nums">{count(share.units)}</TableCell>
                      <TableCell className="text-right tabular-nums">{money(share.revenue_cents)}</TableCell>
                      <TableCell className="pr-4">
                        <div className="flex items-center gap-2">
                          <div className="h-2 flex-1 overflow-hidden rounded-full bg-muted">
                            <div className="h-full rounded-full bg-chart-1" style={{ width: `${percent}%` }} />
                          </div>
                          <span className="w-9 text-right text-xs text-muted-foreground tabular-nums">{percent}%</span>
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      ) : (
        !error && <Placeholder blocks={["h-96"]} />
      )}
    </>
  );
}
