import { usePathname, useRouter, useSearchParams } from "@nexy/client";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { CHANNELS, DEFAULT_PERIOD, PERIODS, channelOf, linkTo, periodOf } from "@/lib/query";

const EVERY = "all";

// A change is a new entry in the history: the back button gives the filters before it.
export function Filters({ period = true }: { period?: boolean }) {
  const search = useSearchParams();
  const pathname = usePathname();
  const router = useRouter();
  const go = (changes: Record<string, string>) =>
    router.push(linkTo(pathname, search, { ...changes, page: "" }), { scroll: false });

  return (
    <div className="flex flex-wrap items-center gap-2">
      {period && (
        <ToggleGroup
          type="single"
          variant="outline"
          value={periodOf(search)}
          onValueChange={(days) => days && go({ days: days === DEFAULT_PERIOD ? "" : days })}
          aria-label="Period"
        >
          {PERIODS.map((days) => (
            <ToggleGroupItem key={days} value={days} className="px-3">
              {days} days
            </ToggleGroupItem>
          ))}
        </ToggleGroup>
      )}
      <Select
        value={channelOf(search) || EVERY}
        onValueChange={(channel) => go({ channel: channel === EVERY ? "" : channel })}
      >
        <SelectTrigger className="w-40" aria-label="Channel">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value={EVERY}>All channels</SelectItem>
          {CHANNELS.map((channel) => (
            <SelectItem key={channel} value={channel}>
              {channel}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
