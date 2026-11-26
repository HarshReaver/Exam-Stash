// Exam Stash: theme switch, open/close sections, subject jump, search, page-image errors,
// print, feedback dialog, analytics.
(function () {
  "use strict";
  var LIVE = location.hostname === "stash.harver.in";
  var GOATCOUNTER = "https://examstash.goatcounter.com/count"; // site code "examstash" in Harsh's GoatCounter account
  var GA_ID = "";                // Google Analytics 4 web stream for stash.harver.in. Empty = no cookies, no banner.
  var CONSENT_KEY = "es-cookies";

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
      store("es-theme", next);
      paintThemeButtons();
    });
  });
  paintThemeButtons();

  // Home sections: a link like /#sem-5 opens that semester and scrolls to it.
  var blocks = all("details.sem-block");
  function openFromHash() {
    var id = decodeURIComponent(location.hash.slice(1));
    var target = id && document.getElementById(id);
    if (target && target.tagName === "DETAILS") {
      target.open = true;
      target.scrollIntoView({ block: "start" });
      target.querySelector("summary").focus({ preventScroll: true });
    }
  }
  if (blocks.length) {
    openFromHash();
    window.addEventListener("hashchange", openFromHash);
    var openAll = document.querySelector("[data-open-all]"), closeAll = document.querySelector("[data-close-all]");
    if (openAll) openAll.addEventListener("click", function () { blocks.forEach(function (d) { d.open = true; }); });
    if (closeAll) closeAll.addEventListener("click", function () { blocks.forEach(function (d) { d.open = false; }); });
  }

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

  // Subject search on the home page: opens the semesters that have matches, restores them when cleared.
  var q = document.querySelector("[data-search]");
  if (q) {
    var items = all("li[data-key]");
    var status = document.querySelector("[data-search-status]");
    var empty = document.querySelector("[data-search-empty]");
    var initial = status.textContent;
    var before = null;
    q.addEventListener("input", function () {
      var words = q.value.toLowerCase().split(/\s+/).filter(Boolean);
      if (words.length && before === null) before = blocks.map(function (d) { return d.open; });
      var shown = 0;
      items.forEach(function (li) {
        var key = li.getAttribute("data-key");
        var ok = words.every(function (w) { return key.indexOf(w) !== -1; });
        li.hidden = !ok;
        if (ok) shown++;
      });
      blocks.forEach(function (sec, i) {
        var any = !!sec.querySelector("li[data-key]:not([hidden])");
        sec.hidden = !any;
        all("h3", sec).forEach(function (h) {
          var list = h.nextElementSibling;
          h.hidden = !!list && !list.querySelector("li:not([hidden])");
        });
        if (words.length) sec.open = any;
        else if (before) sec.open = before[i];
      });
      if (!words.length) before = null;
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

  // Feedback dialog (Web3Forms emails it to Harsh). Opened by any [data-feedback] button.
  var W3F_KEY = "e7870148-6278-4184-b6fa-318a5d0bdd07";
  var dlg = document.querySelector("[data-fb]");
  if (dlg && typeof dlg.showModal === "function") {
    all("[data-feedback]").forEach(function (b) { b.hidden = false; });
    all(".nojs-only").forEach(function (e) { e.hidden = true; });
    var ff = dlg.querySelector("[data-fb-form]"), done = dlg.querySelector("[data-fb-done]");
    var stars = all("[data-star]", dlg), word = dlg.querySelector("[data-star-word]"), rating = 0;
    var WORDS = ["", "Poor", "Fair", "Good", "Very good", "Excellent"];
    var topic = ff.elements.topic, addBox = dlg.querySelector("[data-fb-add]"), msgOpt = dlg.querySelector("[data-msg-opt]");
    var fbStatus = dlg.querySelector("[data-fb-status]"), sendBtn = dlg.querySelector("[data-fb-send]"), opener = null;
    var paint = function (n) {
      stars.forEach(function (b) { b.classList.toggle("on", +b.dataset.star <= n); });
      word.textContent = n ? WORDS[n] : "";
    };
    var setRating = function (n) {
      rating = n;
      stars.forEach(function (b) {
        var k = +b.dataset.star;
        b.setAttribute("aria-checked", String(k === n));
        b.tabIndex = (n ? k === n : k === 1) ? 0 : -1;
      });
      paint(n);
    };
    stars.forEach(function (b) {
      b.addEventListener("click", function () { setRating(+b.dataset.star === rating ? 0 : +b.dataset.star); });
      b.addEventListener("mouseenter", function () { paint(+b.dataset.star); });
      b.addEventListener("keydown", function (e) {
        var k = +b.dataset.star, next = 0;
        if (e.key === "ArrowRight" || e.key === "ArrowUp") next = Math.min(5, k + 1);
        if (e.key === "ArrowLeft" || e.key === "ArrowDown") next = Math.max(1, k - 1);
        if (next) { e.preventDefault(); setRating(next); stars[next - 1].focus(); }
      });
    });
    dlg.querySelector(".stars").addEventListener("mouseleave", function () { paint(rating); });
    var syncTopic = function () {
      var t = topic.value;
      addBox.hidden = t !== "add";
      msgOpt.textContent = t === "add" ? "(optional)" : t === "feedback" ? "(optional if you leave a rating)" : "(required)";
    };
    topic.addEventListener("change", syncTopic);
    var setError = function (field, bad) {
      field.setAttribute("aria-invalid", bad ? "true" : "false");
      document.getElementById(field.getAttribute("aria-describedby").split(" ").pop()).hidden = !bad;
    };
    var say = function (text, cls) { fbStatus.textContent = text; fbStatus.className = "form-status" + (cls ? " " + cls : ""); };
    var reset = function () {
      ff.reset(); setRating(0); say("");
      all("[aria-invalid]", ff).forEach(function (f) { f.setAttribute("aria-invalid", "false"); });
      all(".err", ff).forEach(function (p) { p.hidden = true; });
      ff.hidden = false; done.hidden = true; syncTopic();
    };
    document.addEventListener("click", function (e) {
      var b = e.target.closest("[data-feedback]");
      if (b) {
        opener = b; reset();
        if (b.dataset.topic) { topic.value = b.dataset.topic; syncTopic(); }
        if (b.dataset.subject) ff.elements.for_subject.value = b.dataset.subject;
        if (b.dataset.sem) ff.elements.for_semester.value = b.dataset.sem;
        dlg.showModal();
        (b.dataset.topic === "add" ? ff.elements.link : b.dataset.topic ? ff.elements.message : stars[0]).focus();
        return;
      }
      if (e.target.closest("[data-fb-close]")) dlg.close();
    });
    dlg.addEventListener("click", function (e) { if (e.target === dlg) dlg.close(); }); // click on the backdrop
    dlg.addEventListener("close", function () { if (opener) opener.focus(); });
    ff.addEventListener("submit", function (e) {
      e.preventDefault();
      if (ff.elements.botcheck.value) return; // a bot filled the hidden field
      var t = topic.value, label = topic.options[topic.selectedIndex].text;
      var msg = ff.elements.message.value.trim(), mail = ff.elements.email.value.trim();
      var subj = ff.elements.for_subject.value.trim(), link = ff.elements.link.value.trim();
      var bad = [];
      var check = function (field, isBad) { setError(field, isBad); if (isBad) bad.push(field); };
      if (t === "add") {
        check(ff.elements.for_subject, !subj);
        check(ff.elements.link, !/^https?:\/\/\S+\.\S+/.test(link));
        check(ff.elements.message, false);
      } else {
        check(ff.elements.message, t === "feedback" ? !rating && msg.length < 2 : msg.length < 5);
      }
      check(ff.elements.email, mail !== "" && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(mail));
      if (bad.length) { bad[0].focus(); say("Fix the highlighted field.", "bad"); return; }
      var data = {
        access_key: W3F_KEY, from_name: "Exam Stash",
        subject: "Exam Stash: new message, " + label + (rating ? ", " + rating + "/5" : ""),
        topic: label,
        rating: rating ? new Array(rating + 1).join("★") + new Array(6 - rating).join("☆") + " " + rating + "/5 (" + WORDS[rating] + ")" : "Not given",
        message: msg || "(no message)",
        page: document.title + " · " + location.href
      };
      if (t === "add") {
        data.for_subject = subj; data.for_semester = ff.elements.for_semester.value;
        data.kind = ff.elements.kind.value; data.link = link;
      }
      if (ff.elements.name.value.trim()) data.name = ff.elements.name.value.trim();
      if (mail) data.email = mail;
      sendBtn.disabled = true; sendBtn.textContent = "Sending..."; say("");
      fetch("https://api.web3forms.com/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(data)
      }).then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return r.ok && j.success; }); })
        .then(function (ok) {
          if (ok) {
            dlg.querySelector("[data-fb-reply]").hidden = !mail;
            ff.hidden = true; done.hidden = false; done.querySelector("button").focus();
          } else say("It did not send. Try again in a minute.", "bad");
        })
        .catch(function () { say("It did not send (no connection?). Try again in a minute.", "bad"); })
        .then(function () { sendBtn.disabled = false; sendBtn.textContent = "Send feedback"; });
    });
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
