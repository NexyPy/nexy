import { Link, useSearchParams } from "@nexy/client";
import type { Share } from "@nexy/actions";
import { Button } from "@/components/ui/button";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { count, money } from "@/lib/format";
import { carried, linkTo } from "@/lib/query";

export function BestSellers({ best }: { best: Share[] }) {
  const all = linkTo("/products", carried(useSearchParams()));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Best sellers</CardTitle>
        <CardDescription>The five products that brought in the most</CardDescription>
        <CardAction>
          <Button variant="outline" size="sm" asChild>
            <Link href={all}>All products</Link>
          </Button>
        </CardAction>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Product</TableHead>
              <TableHead className="text-right">Units</TableHead>
              <TableHead className="text-right">Revenue</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {best.map((share) => (
              <TableRow key={share.name}>
                <TableCell className="font-medium">{share.name}</TableCell>
                <TableCell className="text-right tabular-nums">{count(share.units)}</TableCell>
                <TableCell className="text-right tabular-nums">{money(share.revenue_cents)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
