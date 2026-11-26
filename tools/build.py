"""Build every HTML page of Exam Stash from catalog.py and tools/manifest.json.

Run after prepare.py:  python tools/build.py
Writes index.html, 404.html, contact/, sem-N/<subject>/, other-branches/<subject>/, view/<id>/,
sitemap.xml, robots.txt and llms.txt. Static files in assets/ are written by hand.
"""
import datetime, html, json, os, re, shutil, sys

sys.path.insert(0, os.path.dirname(__file__))
from catalog import ITEMS, SECTION, SECTIONS, SUBJECTS, item_id  # noqa: E402
from convert import docx_to_html, xlsx_to_html  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://stash.harver.in"
NAME = "Exam Stash"
V = {"css": 6, "js": 3, "og": 2}          # cache-busting: bump on every change to that file
TODAY = datetime.date.today().isoformat()
YEAR = datetime.date.today().year
# Web3Forms access key for the "Exam Stash" form (public by design; it only lets the form email Harsh).
W3F_KEY = "e7870148-6278-4184-b6fa-318a5d0bdd07"
FB_TOPICS = [("feedback", "General feedback"), ("add", "Send a paper, question bank or notes"),
             ("label", "Wrong or missing label"), ("broken", "A page or file does not open"),
             ("remove", "Ask to remove something"), ("other", "Something else")]
STAR_WORDS = ["Poor", "Fair", "Good", "Very good", "Excellent"]
STAR = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 2.5l2.9 6.1 6.6.8-4.9 4.6 1.3 6.6L12 17.3l-5.9 3.3 '
        '1.3-6.6-4.9-4.6 6.6-.8z"/></svg>')

man = json.load(open(os.path.join(ROOT, "tools", "manifest.json"), encoding="utf-8"))
subj_by = {s["slug"]: s for s in SUBJECTS}
for it in ITEMS:
    it["id"] = item_id(it)
    it["m"] = man[it["id"]]


def esc(s):
    return html.escape(str(s), quote=True)


def size(n):
    return f"{n / 1e6:.1f} MB" if n >= 1e6 else f"{max(1, round(n / 1e3))} KB"


def sec_of(s):
    return SECTION[s["sem"]]


def subj_url(s):
    return f"/{sec_of(s)['slug']}/{s['slug']}/"


def items_of(slug):
    its = [i for i in ITEMS if i["subject"] == slug]
    papers = sorted([i for i in its if i["kind"] == "paper"], key=lambda i: -i["year"])
    return papers, [i for i in its if i["kind"] == "qb"], [i for i in its if i["kind"] == "notes"]


def year_text(it):
    return it.get("yearlabel") or str(it["year"])


def item_title(it):
    if it["kind"] == "paper":
        return f'{year_text(it)} papers' + (f', {it["label"]}' if it.get("label") else "")
    if it["kind"] == "qb":
        return f'question bank, {it["title"]}'
    return it["title"] if not it["title"].startswith("Module") else f'{it["title"]} notes'


def row_label(it):
    if it["kind"] == "paper":
        return f'{year_text(it)}: {", ".join(it["exams"])}' + (f', {it["label"]}' if it.get("label") else "")
    return it["title"]


def row_meta(it):
    m, bits = it["m"], []
    if it["kind"] == "paper":
        bits.append("Batch 2027" if it["own"] else (it["note"] or "Earlier batch"))
    elif it.get("note"):
        bits.append(it["note"])
    if m.get("pages"):
        bits.append(f'{m["pages"]} page{"s" if m["pages"] != 1 else ""}')
    if m["ext"] == "xlsx":
        bits.append("readable page or the Excel file")
    if m["ext"] == "docx":
        bits.append("readable page or the Word file")
    bits.append(size(m["size"]))
    return " · ".join(bits)


def download_name(it):
    s = subj_by[it["subject"]]
    if it["kind"] == "paper":
        base = f'{s["name"]} - {year_text(it)} papers ({", ".join(it["exams"])})' + (f' {it["label"]}' if it.get("label") else "")
    elif it["kind"] == "qb":
        base = f'{s["name"]} - question bank, {it["title"]}'
    else:
        base = f'{s["name"]} - {item_title(it)}'
    base = re.sub(r'[<>:"/\\|?*]', "", base)
    return f'{base}.{it["m"]["ext"]}'


def file_url(it):
    return f'/files/{it["id"]}.{it["m"]["ext"]}'


def short_group(s):
    return "older syllabus" if "older" in s.get("note", "") else "other option"


# ---------------------------------------------------------------- shell
def sidebar(current_slug=None):
    cur_sec = subj_by[current_slug]["sem"] if current_slug else None
    out = []
    for sec in SECTIONS:
        subs = [s for s in SUBJECTS if s["sem"] == sec["key"]]
        lis = []
        for s in subs:
            cur = ' aria-current="page"' if s["slug"] == current_slug else ""
            extra = f' <span class="side-note">{esc(short_group(s))}</span>' if s["group"] != "core" else ""
            lis.append(f'<li><a href="{subj_url(s)}"{cur}>{esc(s["name"])}{extra}</a></li>')
        op = " open" if sec["key"] == cur_sec else ""
        out.append(f'<details class="side-sem {sec["css"]}" data-sec="{sec["slug"]}"{op}>'
                   f'<summary><span>{esc(sec["title"])}</span><span class="count">{len(subs)}</span></summary>'
                   f'<ul>{"".join(lis)}</ul></details>')
    return "".join(out)


def jump_options(current_slug=None):
    out = []
    for sec in SECTIONS:
        opts = "".join(f'<option value="{subj_url(s)}"{" selected" if s["slug"] == current_slug else ""}>{esc(s["name"])}</option>'
                       for s in SUBJECTS if s["sem"] == sec["key"])
        out.append(f'<optgroup label="{esc(sec["title"])}">{opts}</optgroup>')
    first = "" if current_slug else '<option value="" selected>Choose a subject</option>'
    return first + "".join(out)


def page(path, title, desc, main, css=None, current_slug=None, jsonld=None, noindex=False):
    canonical = SITE + path
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    robots = '<meta name="robots" content="noindex">\n' if noindex else ""
    doc = f"""<!doctype html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{robots}<link rel="canonical" href="{canonical}">
<meta name="color-scheme" content="dark light">
<meta name="theme-color" content="#0f1012">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/og-image.jpg?v={V['og']}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<script>try{{var t=localStorage.getItem("es-theme");if(t==="light"||t==="dark")document.documentElement.setAttribute("data-theme",t)}}catch(e){{}}</script>
<link rel="stylesheet" href="/assets/site.css?v={V['css']}">
<script src="/assets/site.js?v={V['js']}" defer></script>
{ld}
</head>
<body class="{css or ''}">
<a class="skip" href="#main">Skip to content</a>
<header class="bar">
  <a class="brand" href="/">{NAME}</a>
  <button class="theme-btn" type="button" data-theme-toggle>Light mode</button>
  <form class="jump" data-jump hidden>
    <label for="jump">Jump to subject</label>
    <div class="jump-row"><select id="jump" name="to">{jump_options(current_slug)}</select><button type="submit">Go</button></div>
  </form>
</header>
<div class="shell">
<aside class="side" aria-label="Semesters and subjects">
  <div class="side-top">
    <a class="brand" href="/">{NAME}</a>
    <p>TCET IT papers, question banks and notes</p>
    <button class="theme-btn" type="button" data-theme-toggle>Light mode</button>
  </div>
  <nav aria-label="Subjects">{sidebar(current_slug)}</nav>
</aside>
<div class="col">
<main id="main" tabindex="-1">
{main}
</main>
<footer class="foot">
  <div class="foot-fb"><div><b>Help improve {NAME}</b><span>Found it useful, spotted a mistake, or have a paper to add? Leave a rating or a message.</span></div>
    <button class="btn" type="button" data-feedback hidden>Send feedback</button></div>
  <p>Shared by Harsh Verma, IT Batch 2027, for study. Not affiliated with TCET or the University of Mumbai. Question papers belong to the college and university; question banks and notes belong to their authors.</p>
  <p class="foot-links"><a href="/privacy/">Privacy and use</a> <span aria-hidden="true">·</span> <a href="https://harver.in">harver.in</a> <span aria-hidden="true">·</span> &copy; {YEAR} {NAME}</p>
  <p data-cookie-row hidden><button class="linklike" type="button" data-cookie-settings>Cookie settings</button></p>
</footer>
</div>
</div>
{feedback_dialog()}
<div class="cookie" data-cookie-banner hidden role="region" aria-label="Cookie preferences">
  <p><b>Cookies.</b> {NAME} can use Google Analytics cookies to see which subjects people open. Accept all to allow them, or Essential only to browse without them. Change this any time under Cookie settings.</p>
  <div class="cookie-btns"><button class="btn-main" type="button" data-cookie-accept>Accept all</button><button class="btn" type="button" data-cookie-essential>Essential only</button></div>
</div>
</body>
</html>
"""
    out = os.path.join(ROOT, path.strip("/"), "index.html") if path.endswith("/") else os.path.join(ROOT, path.strip("/"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8", newline="\n").write(doc)


def feedback_dialog():
    topics = "".join(f'<option value="{k}">{esc(t)}</option>' for k, t in FB_TOPICS)
    stars = "".join(f'<button type="button" role="radio" aria-checked="false" data-star="{n}" aria-label="{n} of 5, {STAR_WORDS[n - 1]}">{STAR}</button>'
                    for n in range(1, 6))
    subjects = "".join(f'<option value="{esc(s["name"])}"></option>' for s in SUBJECTS)
    sems = "".join(f"<option>{esc(sec['title'])}</option>" for sec in SECTIONS)
    return f"""<dialog class="fb" data-fb aria-labelledby="fb-h">
<form class="fb-form" data-fb-form novalidate>
  <div class="fb-top"><h2 id="fb-h">Send feedback</h2><button class="btn fb-x" type="button" data-fb-close>Close</button></div>
  <p class="fb-intro">Ratings, corrections and requests are all welcome, and every message is read. To share a paper, question bank or notes, pick that topic and paste a link.</p>
  <fieldset class="fb-rate"><legend>How useful is {NAME} for you? <span class="opt">(optional)</span></legend>
    <div class="stars" role="radiogroup" aria-label="Rating, 1 to 5">{stars}</div><span class="star-word" data-star-word></span></fieldset>
  <div class="field"><label for="fb-topic">Topic</label><select id="fb-topic" name="topic">{topics}</select></div>
  <div class="fb-add" data-fb-add hidden>
    <div class="field"><label for="fb-subject">Subject</label><input id="fb-subject" name="for_subject" list="fb-subjects" autocomplete="off" aria-describedby="fb-subject-err">
      <datalist id="fb-subjects">{subjects}</datalist><p class="err" id="fb-subject-err" hidden>Name the subject.</p></div>
    <div class="fb-row">
      <div class="field"><label for="fb-sem">Semester</label><select id="fb-sem" name="for_semester"><option>Not sure</option>{sems}</select></div>
      <div class="field"><label for="fb-kind">What it is</label><select id="fb-kind" name="kind"><option>Previous-year paper</option><option>Question bank</option><option>Notes</option><option>Something else</option></select></div>
    </div>
    <div class="field"><label for="fb-link">Link to the file</label><input id="fb-link" name="link" type="url" inputmode="url" placeholder="https://drive.google.com/..." aria-describedby="fb-link-help fb-link-err">
      <p class="help" id="fb-link-help">Upload it to Google Drive (or similar), set sharing to "Anyone with the link", and paste the link. Files cannot be attached here.</p>
      <p class="err" id="fb-link-err" hidden>Paste a link that starts with https://</p></div>
  </div>
  <div class="field"><label for="fb-msg">Message <span class="opt" data-msg-opt>(optional if you leave a rating)</span></label>
    <textarea id="fb-msg" name="message" rows="4" maxlength="2000" aria-describedby="fb-msg-err"></textarea>
    <p class="err" id="fb-msg-err" hidden>Write a few words, or pick a star rating.</p></div>
  <div class="fb-row">
    <div class="field"><label for="fb-name">Your name <span class="opt">(optional)</span></label><input id="fb-name" name="name" autocomplete="name"></div>
    <div class="field"><label for="fb-email">Email <span class="opt">(optional, for a reply)</span></label><input id="fb-email" name="email" type="email" autocomplete="email" aria-describedby="fb-email-err">
      <p class="err" id="fb-email-err" hidden>That email address does not look complete.</p></div>
  </div>
  <div class="hp" aria-hidden="true"><label for="fb-botcheck">Leave this empty</label><input id="fb-botcheck" name="botcheck" tabindex="-1" autocomplete="off"></div>
  <div class="fb-actions"><button class="btn-main" type="submit" data-fb-send>Send feedback</button><p class="form-status" role="status" aria-live="polite" data-fb-status></p></div>
  <p class="fine">Sent to Harsh by email through Web3Forms. See <a href="/privacy/">Privacy and use</a>.</p>
</form>
<div class="fb-done" data-fb-done hidden><h2>Thank you</h2><p>Your message was sent<span data-fb-reply>, and Harsh can reply to the email you gave</span>.</p>
  <button class="btn" type="button" data-fb-close>Close</button></div>
</dialog>"""


# ---------------------------------------------------------------- rows
def file_row(it):
    ext = it["m"]["ext"]
    label = row_label(it)
    ctx = esc(f'{subj_by[it["subject"]]["name"]}, {label}')
    return (f'<li class="file"><span class="ft {ext}">{ext.upper()}</span>'
            f'<div class="fname"><span>{esc(label)}</span><small>{esc(row_meta(it))}</small></div>'
            f'<a class="act" href="/view/{it["id"]}/">Open<span class="vh"> {ctx}</span></a>'
            f'<a class="act" href="{file_url(it)}" download="{esc(download_name(it))}">Download<span class="vh"> {ctx}</span></a></li>')


SYLLABUS_NOTE = ("The syllabus may have changed since Batch 2027 (TCET, University of Mumbai, CBCGS-HME 2023 from Semester III). "
                 "Check your current syllabus before trusting a module list.")


def subject_summary(s):
    p, q, no = items_of(s["slug"])
    bits = []
    if p:
        years = []
        for i in p:
            if year_text(i) not in years:
                years.append(year_text(i))
        bits.append("papers " + ", ".join(years))
    if q:
        bits.append(f'{len(q)} question bank{"s" if len(q) > 1 else ""}')
    if no:
        bits.append(f'{len(no)} notes file{"s" if len(no) > 1 else ""}')
    return bits


# ---------------------------------------------------------------- pages
def build_home():
    secs = []
    for sec in SECTIONS:
        groups = {"core": [], "elective": [], "other": []}
        n_files = 0
        for s in SUBJECTS:
            if s["sem"] != sec["key"]:
                continue
            n_files += sum(len(x) for x in items_of(s["slug"]))
            key = " ".join([s["name"], s.get("aka", ""), s["code"], sec["title"], sec["short"]]).lower()
            note = f' <span class="tag">{esc(s.get("note", ""))}</span>' if s.get("note") else ""
            groups[s["group"]].append(
                f'<li data-key="{esc(key)}"><a href="{subj_url(s)}"><span class="s-name">{esc(s["name"])}</span>'
                f'<span class="s-meta">{esc(s["code"] + " · " if s["code"] else "")}{esc(" · ".join(subject_summary(s)))}{note}</span></a></li>')
        n_subj = sum(len(g) for g in groups.values())
        body = f'<ul class="subjects">{"".join(groups["core"])}</ul>'
        if groups["elective"]:
            body += f'<h3>Other options in this semester</h3><ul class="subjects">{"".join(groups["elective"])}</ul>'
        if groups["other"]:
            body += f'<h3>Older syllabus</h3><ul class="subjects">{"".join(groups["other"])}</ul>'
        note = f'<p class="sec-note">{esc(sec["note"])}.</p>' if sec["note"] else ""
        secs.append(f'<details class="sem-block {sec["css"]}" id="{sec["slug"]}">'
                    f'<summary><h2>{esc(sec["title"])}</h2><span class="sum-meta">{n_subj} subject{"s" if n_subj != 1 else ""}, {n_files} file{"s" if n_files != 1 else ""}</span></summary>'
                    f'<div class="sem-body">{note}{body}</div></details>')
    main = f"""
<h1>{NAME}</h1>
<p class="lead">Previous-year papers, question banks and notes for TCET IT, from first year to semester VII. Open anything here, or download the original file.</p>
<p class="notice">{esc(SYLLABUS_NOTE)} Not an official TCET site.</p>
<div class="search">
  <label for="q">Find a subject</label>
  <input id="q" type="search" placeholder="DBMS, OS, Automata, DevOps" autocomplete="off" data-search>
  <p class="search-status" aria-live="polite" data-search-status>{len(SUBJECTS)} subjects, {len(ITEMS)} files. Pick a semester to open it.</p>
</div>
<p class="search-empty" data-search-empty hidden>No subject matches that. Try a short name such as DBMS, CN or BDA, or clear the box and open a semester.</p>
<div class="sems">
<p class="sem-tools"><button class="linklike" type="button" data-open-all>Open all</button> <button class="linklike" type="button" data-close-all>Close all</button></p>
{"".join(secs)}
</div>
"""
    ld = {"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": SITE + "/",
          "description": "Previous-year papers, question banks and notes for TCET IT students.",
          "author": {"@type": "Person", "name": "Harsh Verma", "url": "https://harver.in"}}
    page("/", f"{NAME}: TCET IT previous-year papers, question banks and notes",
         "Previous-year exam papers (ISE and ESE), question banks and notes for TCET IT, first year to semester VII. View on your phone or download.",
         main, jsonld=ld)


def build_subject(s):
    p, q, no = items_of(s["slug"])
    sec = sec_of(s)
    parts = []
    if p:
        parts.append(f'<section><h2>Previous-year papers</h2><ul class="files">{"".join(file_row(i) for i in p)}</ul></section>')
    if q:
        parts.append(f'<section><h2>Question bank{"s" if len(q) > 1 else ""}</h2><ul class="files">{"".join(file_row(i) for i in q)}</ul></section>')
    if no:
        parts.append(f'<section><h2>Notes</h2><ul class="files">{"".join(file_row(i) for i in no)}</ul></section>')
    sub = " · ".join(x for x in [s["code"], s.get("note", ""), sec["note"]] if x)
    caution = ""
    if sec["key"] == "ob":
        caution = '<p class="notice">These papers are from other branches, not IT. Many Machine Learning questions overlap with the IT subject, so they are worth a look.</p>'
    elif s["group"] == "other":
        caution = '<p class="notice">These papers come from an older syllabus. Many questions still overlap, so they are worth a look.</p>'
    main = f"""
<nav class="crumb" aria-label="Breadcrumb"><a href="/#{sec['slug']}">{esc(sec['title'])}</a></nav>
<h1>{esc(s['name'])}</h1>
{f'<p class="sub">{esc(sub)}</p>' if sub else ''}
{caution}
{"".join(parts)}
<p class="ask">Have a paper, question bank or notes for {esc(s['name'])} that is not here? <button class="linklike" type="button" data-feedback data-topic="add" data-subject="{esc(s['name'])}" data-sem="{esc(sec['title'])}" hidden>Send it to Harsh</button></p>
<p class="fine">{esc(SYLLABUS_NOTE)}</p>
"""
    what = [w for w, l in (("previous-year papers", p), ("question bank", q), ("notes", no)) if l]
    where = "TCET IT " + sec["short"] if sec["key"] != "ob" else "TCET, other branches"
    title = f'{s["name"]} {", ".join(what[:-1]) + " and " + what[-1] if len(what) > 1 else what[0]} ({where}) | {NAME}'
    desc = f'{s["name"]}, {where}: ' + "; ".join(x for x in subject_summary(s)) + ". View or download."
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": NAME, "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": sec["title"], "item": f"{SITE}/#{sec['slug']}"},
        {"@type": "ListItem", "position": 3, "name": s["name"], "item": SITE + subj_url(s)}]}
    page(subj_url(s), title, desc, main, css=sec["css"], current_slug=s["slug"], jsonld=ld)


def build_view(it):
    s = subj_by[it["subject"]]
    sec = sec_of(s)
    m = it["m"]
    ext = m["ext"]
    head = f"""
<nav class="crumb" aria-label="Breadcrumb"><a href="/#{sec['slug']}">{esc(sec['title'])}</a> <span aria-hidden="true">/</span> <a href="{subj_url(s)}">{esc(s['name'])}</a></nav>
<h1>{esc(s['name'])}: {esc(item_title(it))}</h1>
<p class="sub"><span class="ft {ext}">{ext.upper()}</span> {esc(row_meta(it))}{' · ' + esc(', '.join(it['exams'])) if it['kind'] == 'paper' else ''}</p>
<div class="actions">
  <a class="btn-main" href="{file_url(it)}" download="{esc(download_name(it))}">Download {ext.upper()}</a>
  {'<button class="btn" type="button" data-print>Print or save as PDF</button>' if ext in ('xlsx', 'docx') else f'<a class="btn" href="{file_url(it)}">Open the PDF itself</a>'}
  <a class="btn" href="{subj_url(s)}">All files for this subject</a>
</div>
"""
    if ext == "pdf":
        figs = []
        n = m["pages"]
        for i, (w, h) in enumerate(m["img"], start=1):
            lazy = 'fetchpriority="high"' if i == 1 else 'loading="lazy"'
            figs.append(f'<li><figure class="pg"><div class="pg-img" style="aspect-ratio:{w}/{h}">'
                        f'<img src="/pages/{it["id"]}/{i}.webp" width="{w}" height="{h}" {lazy} decoding="async" alt="Page {i} of {n}" data-page>'
                        f'<p class="pg-fail"><span>Page {i} did not load. <a href="{file_url(it)}">Open the PDF</a> instead.</span></p></div>'
                        f'<figcaption>Page {i} of {n}</figcaption></figure></li>')
        body = f'<ol class="pages">{"".join(figs)}</ol>'
    elif ext == "xlsx":
        src = os.path.join(ROOT, "files", f'{it["id"]}.xlsx')
        frag, count, _coloured = xlsx_to_html(src, m.get("figs", []), f'/pages/{it["id"]}/')
        body = (f'<p class="fine">{count} questions, converted from the Excel file so it reads on a phone. '
                'Colours and notes are the ones Harsh kept in the sheet.</p><div class="qb">' + frag + "</div>")
    else:
        src = os.path.join(ROOT, "files", f'{it["id"]}.docx')
        frag, _ = docx_to_html(src, m.get("docimgs", {}), f'/pages/{it["id"]}/')
        body = f'<p class="fine">Converted from the Word file so it reads on a phone. The download is the original.</p><article class="prose">{frag}</article>'
    caution = ""
    if it["kind"] == "paper" and not it["own"] and it["note"]:
        caution = '<p class="notice">From an older syllabus. The questions still overlap a lot.</p>'
    if sec["key"] == "ob":
        caution = '<p class="notice">From another branch, not IT. Many questions overlap with the IT subject.</p>'
    title = f'{s["name"]} {item_title(it)}{" (" + ", ".join(it["exams"]) + ")" if it["kind"] == "paper" else ""} | {NAME}'
    desc = f'{s["name"]}, {sec["title"] if sec["key"] != "ob" else "other branches"}: {item_title(it)}. {row_meta(it)}.'
    page(f'/view/{it["id"]}/', title, desc, head + caution + body, css=sec["css"], current_slug=s["slug"])


def build_privacy():
    updated = datetime.date.today().strftime("%d %B %Y").lstrip("0")
    main = f"""
<h1>Privacy and use</h1>
<p class="lead">Short and plain: what this site is, what it keeps about you (very little), and how the files may be used.</p>
<p class="fine">Last updated {updated}.</p>
<section class="prose">
<h2>Who runs it</h2>
<p>{NAME} is run by Harsh Verma, a TCET IT student (Batch 2027), to share the papers, question banks and notes he collected. It is free, has no ads and is not affiliated with Thakur College of Engineering and Technology or the University of Mumbai.</p>
<h2>What is collected</h2>
<ul>
<li><b>Visit counts.</b> GoatCounter counts page views (which page, the referring site, browser type and country). It sets no cookies and does not identify you.</li>
<li><b>Feedback you send.</b> The feedback form sends what you type, the page you were on and your optional name and email to Harsh's inbox through Web3Forms. Your email is used only to reply to you and is never shared or added to any list.</li>
<li><b>Your theme choice.</b> The light or dark setting is saved in your own browser (local storage) and never leaves your device.</li>
<li>No accounts, no advertising, no tracking cookies.</li>
</ul>
<h2>The files</h2>
<ul>
<li>Question papers belong to TCET and the University of Mumbai. Question banks and notes belong to the faculty or students who wrote them. They are shared here only to help students study.</li>
<li>Use them for your own study. Please do not sell them or present them as official.</li>
<li>Personal details found on scans (such as a student's name or roll number) were covered before publishing, and file properties were removed.</li>
<li>If something here is yours and you want it removed, or you spot personal details we missed, use <button class="linklike" type="button" data-feedback data-topic="remove" hidden>Ask to remove something</button><span class="nojs-only"> the feedback form</span>. It will be taken down.</li>
</ul>
<h2>Accuracy</h2>
<p>{esc(SYLLABUS_NOTE)} Papers and banks are shown as they were given, and answer keys were written by students, so check anything important against your own syllabus and teachers.</p>
<h2>Contact</h2>
<p>Use Send feedback at the bottom of any page.</p>
</section>
"""
    page("/privacy/", f"Privacy and use | {NAME}", "What Exam Stash collects (very little), how the shared papers and notes may be used, and how to ask for removal.", main)


def build_404():
    main = """
<h1>Nothing here</h1>
<p class="lead">This address does not match a page. Files keep the same address once published, so the link may have a typo.</p>
<p><a class="btn-main" href="/">See every semester</a></p>
"""
    page("/404.html", f"Page not found | {NAME}", "This page does not exist on Exam Stash.", main, noindex=True)


def build_meta():
    urls = ["/", "/privacy/"] + [subj_url(s) for s in SUBJECTS] + [f'/view/{i["id"]}/' for i in ITEMS]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join(f"  <url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in urls) + "</urlset>\n"
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8", newline="\n").write(sm)
    open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8", newline="\n").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    lines = [f"# {NAME}", "", "> Previous-year exam papers (ISE and ESE), question banks and notes for TCET IT (University of Mumbai), "
             "first year to semester VII, shared by Harsh Verma from IT Batch 2027. Not an official TCET site. The syllabus may have changed since.", ""]
    for sec in SECTIONS:
        lines.append(f"## {sec['title']}")
        for s in SUBJECTS:
            if s["sem"] == sec["key"]:
                lines.append(f'- [{s["name"]}]({SITE}{subj_url(s)})' + (f': {s["note"]}' if s.get("note") else ""))
        lines.append("")
    open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8", newline="\n").write("\n".join(lines))


def main():
    for d in ("view", "contact", "privacy", *[sec["slug"] for sec in SECTIONS]):
        shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)
    build_home()
    for s in SUBJECTS:
        if not any(i["subject"] == s["slug"] for i in ITEMS):
            raise SystemExit(f"Subject without files: {s['slug']}")
        build_subject(s)
    for it in ITEMS:
        build_view(it)
    build_privacy()
    build_404()
    build_meta()
    print(f"Built home, privacy, {len(SUBJECTS)} subject pages, {len(ITEMS)} file pages.")


if __name__ == "__main__":
    main()
