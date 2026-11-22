// Night Before: theme switch, subject jump, search, page-image errors, print, contact, analytics.
(function () {
  "use strict";
  var LIVE = location.hostname === "pyq.harver.in";
  var GOATCOUNTER = "https://nightbefore.goatcounter.com/count"; // site code "nightbefore" in Harsh's GoatCounter account
  var GA_ID = "";                // Google Analytics 4 web stream for pyq.harver.in. Empty = no cookies, no banner.
  var CONSENT_KEY = "nb-cookies";

  function all(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function store(key, val) {
    try { if (val === undefined) return localStorage.getItem(key); localStorage.setItem(key, val); } catch (e) { return null; }
  }

  // Theme: dark by default, the choice is remembered on this device.
  var root = document.documentElement;
  function paintThemeButtons() {
    var dark = root.getAttribute("data-theme") !== "light";
    all("[data-theme-toggle]").forEach(function (b) {
      b.textContent = dark ? "Light mode" : "Dark mode";
      b.setAttribute("aria-label", dark ? "Switch to light mode" : "Switch to dark mode");
    });
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", dark ? "#0f1012" : "#f6f6f3");
  }
  all("[data-theme-toggle]").forEach(function (b) {
    b.addEventListener("click", function () {
      var next = root.getAttribute("data-theme") === "light" ? "dark" : "light";
      root.setAttribute("data-theme", next);
      store("nb-theme", next);
      paintThemeButtons();
    });
  });
  paintThemeButtons();

  // Jump to subject (phones). Needs JavaScript, so it stays hidden without it.
  var jump = document.querySelector("[data-jump]");
  if (jump) {
    var sel = jump.querySelector("select");
    jump.hidden = false;
    jump.addEventListener("submit", function (e) {
      e.preventDefault();
      if (sel.value) location.href = sel.value;
    });
    sel.addEventListener("change", function () {
      if (sel.value && window.matchMedia && matchMedia("(pointer: coarse)").matches) location.href = sel.value;
    });
  }

  // Keep the current subject visible in the sidebar.
  var side = document.querySelector(".side");
  var cur = side && side.querySelector('a[aria-current="page"]');
  if (cur && side.scrollHeight > side.clientHeight) {
    side.scrollTop = Math.max(0, cur.offsetTop - side.clientHeight / 3);
  }

  // Subject search on the home page.
  var q = document.querySelector("[data-search]");
  if (q) {
    var items = all("li[data-key]");
    var status = document.querySelector("[data-search-status]");
    var empty = document.querySelector("[data-search-empty]");
    var initial = status.textContent;
    q.addEventListener("input", function () {
      var words = q.value.toLowerCase().split(/\s+/).filter(Boolean);
      var shown = 0;
      items.forEach(function (li) {
        var key = li.getAttribute("data-key");
        var ok = words.every(function (w) { return key.indexOf(w) !== -1; });
        li.hidden = !ok;
        if (ok) shown++;
      });
      all(".sem-block").forEach(function (sec) {
        sec.hidden = !sec.querySelector("li[data-key]:not([hidden])");
        all("h3", sec).forEach(function (h) {
          var list = h.nextElementSibling;
          h.hidden = !!list && !list.querySelector("li:not([hidden])");
        });
      });
      empty.hidden = shown !== 0;
      status.textContent = words.length ? (shown ? shown + " of " + items.length + " subjects match." : "No match.") : initial;
    });
  }

  // Page images: show a clear message if one fails to load.
  all("img[data-page]").forEach(function (img) {
    function fail() { img.closest(".pg").classList.add("failed"); }
    if (img.complete && img.naturalWidth === 0 && img.getAttribute("src")) fail();
    img.addEventListener("error", fail);
  });

  // Print or save as PDF (converted question banks and notes).
  all("[data-print]").forEach(function (b) { b.addEventListener("click", function () { window.print(); }); });

  // Contact link, assembled here so the address is not plain text in the HTML.
  var mail = document.querySelector("[data-email]");
  if (mail) {
    mail.href = "mailto:" + ["harshkrish2323", "gmail.com"].join("@") + "?subject=" + encodeURIComponent("Night Before");
    document.querySelector("[data-contact]").hidden = false;
  }

  // Visitor counts: GoatCounter (no cookies) on the live site only.
  if (LIVE) {
    var gc = document.createElement("script");
    gc.async = true;
    gc.src = "https://gc.zgo.at/count.js";
    gc.setAttribute("data-goatcounter", GOATCOUNTER);
    document.head.appendChild(gc);
  }

  // Google Analytics 4 only after "Accept all", and only once a stream ID is set above.
  var banner = document.querySelector("[data-cookie-banner]");
  if (GA_ID && banner) {
    var row = document.querySelector("[data-cookie-row]");
    row.hidden = false;
    var loadGA = function () {
      if (!LIVE || window.gtag) return;
      var s = document.createElement("script");
      s.async = true;
      s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA_ID;
      document.head.appendChild(s);
      window.dataLayer = window.dataLayer || [];
      window.gtag = function () { window.dataLayer.push(arguments); };
      window.gtag("js", new Date());
      window.gtag("config", GA_ID);
    };
    var choose = function (val) {
      store(CONSENT_KEY, val);
      banner.hidden = true;
      if (val === "all") loadGA();
      else if (window.gtag) location.reload();
    };
    var saved = store(CONSENT_KEY);
    if (saved === "all") loadGA();
    else if (saved !== "essential") banner.hidden = false;
    banner.querySelector("[data-cookie-accept]").addEventListener("click", function () { choose("all"); });
    banner.querySelector("[data-cookie-essential]").addEventListener("click", function () { choose("essential"); });
    document.querySelector("[data-cookie-settings]").addEventListener("click", function () {
      banner.hidden = false;
      banner.querySelector("[data-cookie-accept]").focus();
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !banner.hidden && store(CONSENT_KEY)) banner.hidden = true; });
  }
})();
