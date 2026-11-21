import { usePathname, useSearchParams } from "@nexy/client";
import { orders } from "@nexy/actions";
import { Filters } from "@/components/filters";
import { Placeholder, Problem } from "@/components/page-state";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { count, day, exact } from "@/lib/format";
import { useLoaded } from "@/lib/load";
import { channelOf, linkTo } from "@/lib/query";
import { cn } from "@/lib/utils";

function Pages({ number, pages }: { number: number; pages: number }) {
  const pathname = usePathname();
  const search = useSearchParams();
  const to = (page: number) => linkTo(pathname, search, { page: page === 1 ? "" : String(page) });

  return (
    <Pagination className="mx-0 w-auto">
      <PaginationContent>
        <PaginationItem>
          <PaginationPrevious
            href={to(number - 1)}
            aria-disabled={number === 1}
            className={cn(number === 1 && "pointer-events-none opacity-50")}
          />
        </PaginationItem>
        <PaginationItem>
          <PaginationNext
            href={to(number + 1)}
            aria-disabled={number === pages}
            className={cn(number === pages && "pointer-events-none opacity-50")}
          />
        </PaginationItem>
      </PaginationContent>
    </Pagination>
  );
}

export default function Orders() {
  const search = useSearchParams();
  const channel = channelOf(search);
  const page = search.get("page") ?? "1";
  const { data, error, stale } = useLoaded(() => orders({ channel, page }), `${channel}/${page}`);

  return (
    <>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-muted-foreground">
          {data ? `${count(data.total)} orders, newest first` : "Loading the orders..."}
        </p>
        <Filters period={false} />
      </div>
      <Problem message={error} />
      {data ? (
        <Card className={cn("py-0 transition-opacity", stale && "opacity-60")}>
          <CardContent className="px-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="pl-4">Day</TableHead>
                  <TableHead>Product</TableHead>
                  <TableHead>Channel</TableHead>
                  <TableHead className="hidden md:table-cell">Region</TableHead>
                  <TableHead className="text-right">Units</TableHead>
                  <TableHead className="pr-4 text-right">Revenue</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.rows.map((order) => (
                  <TableRow key={order.id}>
                    <TableCell className="pl-4 tabular-nums">{day(order.placed_on)}</TableCell>
                    <TableCell className="font-medium">{order.product}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{order.channel}</Badge>
                    </TableCell>
                    <TableCell className="hidden md:table-cell">{order.region}</TableCell>
                    <TableCell className="text-right tabular-nums">{order.units}</TableCell>
                    <TableCell className="pr-4 text-right tabular-nums">{exact(order.revenue_cents)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      ) : (
        !error && <Placeholder blocks={["h-96"]} />
      )}
      {data && (
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="text-sm text-muted-foreground tabular-nums">
            Page {data.number} of {data.pages}
          </p>
          <Pages number={data.number} pages={data.pages} />
        </div>
      )}
    </>
  );
}
