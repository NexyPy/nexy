(function () {
  var root = document.documentElement;
  var KEY = "nexy-theme";
  function stored() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }
  function apply() {
    var saved = stored();
    var dark = saved ? saved === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
    root.classList.toggle("dark", dark);
  }
  function sync() {
    var on = String(root.classList.contains("dark"));
    document.querySelectorAll("[data-theme-toggle]").forEach(function (button) {
      if (button.getAttribute("aria-checked") !== on) button.setAttribute("aria-checked", on);
    });
  }
  apply();
  document.addEventListener("click", function (event) {
    var button = event.target.closest && event.target.closest("[data-theme-toggle]");
    if (!button) return;
    var dark = root.classList.toggle("dark");
    try { localStorage.setItem(KEY, dark ? "dark" : "light"); } catch (e) {}
    sync();
  });
  addEventListener("storage", function (event) {
    if (event.key === KEY) { apply(); sync(); }
  });
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function () {
    if (!stored()) { apply(); sync(); }
  });
  document.addEventListener("DOMContentLoaded", sync);
  new MutationObserver(sync).observe(root, { childList: true, subtree: true });
})();
