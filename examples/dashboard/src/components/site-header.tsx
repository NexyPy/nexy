import { usePathname } from "@nexy/client";
import { Separator } from "@/components/ui/separator";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { PAGES } from "@/components/app-sidebar";
import ThemeToggle from "@/components/theme-toggle";

export function SiteHeader() {
  const pathname = usePathname();
  const title = PAGES.find((page) => page.href === pathname)?.label ?? "Kiln Coffee";

  return (
    <header className="sticky top-0 z-10 flex h-14 shrink-0 items-center gap-2 border-b bg-background px-4">
      <SidebarTrigger className="-ml-1" />
      <Separator orientation="vertical" className="mx-1 data-vertical:h-4 data-vertical:self-center" />
      <h1 className="text-base font-medium">{title}</h1>
      <div className="ml-auto">
        <ThemeToggle />
      </div>
    </header>
  );
}
