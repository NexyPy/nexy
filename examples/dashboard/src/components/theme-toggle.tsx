import { MoonIcon, SunIcon } from "lucide-react";
import { Button } from "@/components/ui/button";

const STORAGE_KEY = "nexy-theme";

// <ThemeScript /> sets the `dark` class before the first paint; this button only flips it. The
// icons follow the class through `dark:`, so the server and the browser render the same markup.
export default function ThemeToggle() {
  function toggle() {
    const dark = document.documentElement.classList.toggle("dark");
    try {
      localStorage.setItem(STORAGE_KEY, dark ? "dark" : "light");
    } catch {
      // The choice only lasts for this visit when storage is blocked.
    }
  }

  return (
    <Button variant="ghost" size="icon" aria-label="Switch between light and dark" onClick={toggle}>
      <SunIcon className="dark:hidden" />
      <MoonIcon className="hidden dark:block" />
    </Button>
  );
}
