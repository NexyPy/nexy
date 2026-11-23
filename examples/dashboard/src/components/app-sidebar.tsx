import { ChartAreaIcon, CoffeeIcon, CodeIcon, PackageIcon, ReceiptIcon } from "lucide-react";
import { Link, usePathname, useSearchParams } from "@nexy/client";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";
import { carried, linkTo } from "@/lib/query";

export const PAGES = [
  { href: "/", label: "Overview", icon: ChartAreaIcon },
  { href: "/orders", label: "Orders", icon: ReceiptIcon },
  { href: "/products", label: "Products", icon: PackageIcon },
] as const;

// Every link is a client navigation: the router of Nexy renders the next page in the browser,
// and the period and channel chosen on one page follow to the next.
export function AppSidebar() {
  const pathname = usePathname();
  const kept = carried(useSearchParams());
  const { setOpenMobile } = useSidebar();
  const close = () => setOpenMobile(false);

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <Link href={linkTo("/", kept)} onClick={close}>
                <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
                  <CoffeeIcon className="size-4" />
                </span>
                <span className="flex flex-col leading-tight">
                  <span className="font-semibold">Kiln Coffee</span>
                  <span className="text-xs text-muted-foreground">Sales dashboard</span>
                </span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {PAGES.map((page) => (
                <SidebarMenuItem key={page.href}>
                  <SidebarMenuButton asChild isActive={pathname === page.href} tooltip={page.label}>
                    <Link href={linkTo(page.href, kept)} onClick={close}>
                      <page.icon />
                      <span>{page.label}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton asChild tooltip="The code">
              <a href="https://github.com/NexyPy/nexy/tree/main/examples/dashboard" target="_blank" rel="noopener noreferrer">
                <CodeIcon />
                <span>The code</span>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  );
}
