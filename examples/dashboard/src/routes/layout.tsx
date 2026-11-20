import type { ReactNode } from "react";
import { AppSidebar } from "@/components/app-sidebar";
import { SiteHeader } from "@/components/site-header";
import ThemeScript from "@/components/theme-script";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import { TooltipProvider } from "@/components/ui/tooltip";

// The document of every page. The sidebar and the header stay; only `children` changes when the
// client router moves to another page.
export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <meta charSet="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <meta name="description" content="The sales of Kiln Coffee: revenue, orders and products." />
        <title>Kiln Coffee dashboard</title>
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
        <ThemeScript />
      </head>
      <body>
        <TooltipProvider>
          <SidebarProvider>
            <AppSidebar />
            <SidebarInset>
              <SiteHeader />
              <main className="flex flex-1 flex-col gap-4 p-4 lg:p-6">{children}</main>
            </SidebarInset>
          </SidebarProvider>
        </TooltipProvider>
      </body>
    </html>
  );
}
