import { useSearchParams } from "@nexy/client";
import { overview } from "@nexy/actions";
import { BestSellers } from "@/components/best-sellers";
import { ChannelCard } from "@/components/channel-card";
import { Filters } from "@/components/filters";
import { KpiCards } from "@/components/kpi-cards";
import { Placeholder, Problem } from "@/components/page-state";
import { RevenueChart } from "@/components/revenue-chart";
import { span } from "@/lib/format";
import { useLoaded } from "@/lib/load";
import { channelOf, periodOf } from "@/lib/query";
import { cn } from "@/lib/utils";

export default function Overview() {
  const search = useSearchParams();
  const days = periodOf(search);
  const channel = channelOf(search);
  const { data, error, stale } = useLoaded(() => overview({ days, channel }), `${days}/${channel}`);

  return (
    <>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-muted-foreground">
          {data ? span(data.period.first, data.period.last) : "Loading the period..."}
        </p>
        <Filters />
      </div>
      <Problem message={error} />
      {data ? (
        <div className={cn("flex flex-col gap-4 transition-opacity", stale && "opacity-60")}>
          <KpiCards totals={data.totals} before={data.before} days={data.period.days} />
          <RevenueChart daily={data.daily} />
          <div className="grid gap-4 lg:grid-cols-2">
            <ChannelCard channels={data.channels} chosen={data.period.channel} />
            <BestSellers best={data.best} />
          </div>
        </div>
      ) : (
        !error && <Placeholder blocks={["h-32", "h-80", "h-72"]} />
      )}
    </>
  );
}
