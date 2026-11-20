import type { ReactNode } from "react";
import Header from "@/components/header.tsx";
import Footer from "@/components/footer.tsx";
import ThemeScript from "@/components/theme-script.tsx";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <meta charSet="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <meta name="description" content="A todo list kept in SQLite by Python, with a React page: a Nexy example." />
        <title>Todos</title>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500..700&family=Geist:wght@400..600&family=Geist+Mono:wght@400..500&display=swap"
          rel="stylesheet"
        />
        <ThemeScript />
      </head>
      <body className="flex min-h-dvh flex-col">
        <Header />
        <main className="flex flex-1 flex-col">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
