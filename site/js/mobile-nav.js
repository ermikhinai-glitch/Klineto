(function () {
  function qs(sel, root) {
    return (root || document).querySelector(sel);
  }
  function qsa(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }

  function pathKey() {
    var p = (location.pathname || "/").replace(/\/+$/, "") || "/";
    return p;
  }

  function markActive() {
    var p = pathKey();
    qsa(".m-bottom-nav a, .m-drawer a").forEach(function (a) {
      var href = a.getAttribute("href") || "";
      var active = false;
      if (href === "/" || href === "") {
        active = p === "/";
      } else if (href.indexOf("#") === 0) {
        active = false;
      } else {
        var clean = href.replace(/\/+$/, "");
        active = p === clean || p.indexOf(clean + "/") === 0;
      }
      // Services tab: any hub/service page
      if (a.getAttribute("data-m-nav") === "services") {
        active =
          p.indexOf("/uborka-") === 0 ||
          p.indexOf("/himchistka") === 0 ||
          p.indexOf("/generalnaya") === 0 ||
          p.indexOf("/podderzhivayushchaya") === 0 ||
          p.indexOf("/ezhednevnaya") === 0 ||
          p.indexOf("/regulyarnaya") === 0 ||
          p.indexOf("/uborka-posle") === 0;
      }
      if (a.getAttribute("data-m-nav") === "calc") {
        active = p.indexOf("/kalkulyator") === 0 || location.hash === "#calculator";
      }
      a.classList.toggle("is-active", !!active);
      if (active) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    });
  }

  function openDrawer() {
    var d = qs(".m-drawer");
    var b = qs(".m-drawer-backdrop");
    if (!d || !b) return;
    d.classList.add("is-open");
    b.classList.add("is-open");
    document.documentElement.classList.add("m-drawer-open");
    // Clear any leftover inline overflow from older builds
    document.documentElement.style.overflow = "";
    document.body.style.overflow = "";
  }

  function closeDrawer() {
    var d = qs(".m-drawer");
    var b = qs(".m-drawer-backdrop");
    if (!d || !b) return;
    d.classList.remove("is-open");
    b.classList.remove("is-open");
    document.documentElement.classList.remove("m-drawer-open");
    document.documentElement.style.overflow = "";
    document.body.style.overflow = "";
  }

  document.addEventListener("DOMContentLoaded", function () {
    markActive();
    // Ensure scroll is not stuck locked from a previous session/state
    document.documentElement.classList.remove("m-drawer-open");
    document.documentElement.style.overflow = "";
    document.body.style.overflow = "";
    var btn = qs(".m-menu-btn");
    var close = qs(".m-drawer-close");
    var backdrop = qs(".m-drawer-backdrop");
    if (btn) btn.addEventListener("click", openDrawer);
    if (close) close.addEventListener("click", closeDrawer);
    if (backdrop) backdrop.addEventListener("click", closeDrawer);
    qsa(".m-drawer a").forEach(function (a) {
      a.addEventListener("click", closeDrawer);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeDrawer();
    });
  });
})();
