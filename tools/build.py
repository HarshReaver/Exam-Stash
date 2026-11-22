"""Build every HTML page of Night Before from catalog.py and tools/manifest.json.

Run after prepare.py:  python tools/build.py
Writes index.html, 404.html, sem-N/<subject>/index.html, view/<id>/index.html,
sitemap.xml, robots.txt and llms.txt. Static files in assets/ are written by hand.
"""
import datetime, html, json, os, re, shutil, sys

sys.path.insert(0, os.path.dirname(__file__))
from catalog import ITEMS, SEMESTERS, SUBJECTS, item_id  # noqa: E402
from convert import docx_to_html, xlsx_to_html  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://pyq.harver.in"
NAME = "Night Before"
V = {"css": 4, "js": 1, "og": 1}          # cache-busting: bump on every change to that file
TODAY = datetime.date.today().isoformat()

man = json.load(open(os.path.join(ROOT, "tools", "manifest.json"), encoding="utf-8"))
subj_by = {s["slug"]: s for s in SUBJECTS}
for it in ITEMS:
    it["id"] = item_id(it)
    it["m"] = man[it["id"]]


def esc(s):
    return html.escape(str(s), quote=True)


def size(n):
    return f"{n / 1e6:.1f} MB" if n >= 1e6 else f"{max(1, round(n / 1e3))} KB"


def subj_url(s):
    return f"/sem-{s['sem']}/{s['slug']}/"


def items_of(slug):
    its = [i for i in ITEMS if i["subject"] == slug]
    papers = sorted([i for i in its if i["kind"] == "paper"], key=lambda i: -i["year"])
    return papers, [i for i in its if i["kind"] == "qb"], [i for i in its if i["kind"] == "notes"]


def item_title(it, with_subject=False):
    s = subj_by[it["subject"]]
    if it["kind"] == "paper":
        t = f'{it["year"]} papers'
    elif it["kind"] == "qb":
        t = f'question bank, {it["title"]}'
    else:
        t = it["title"] if not it["title"].startswith("Module") else f'{it["title"]} notes'
    return f'{s["name"]}: {t}' if with_subject else t


def row_label(it):
    if it["kind"] == "paper":
        return f'{it["year"]}: {", ".join(it["exams"])}'
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
        base = f'{s["name"]} - {it["year"]} papers ({", ".join(it["exams"])})'
    elif it["kind"] == "qb":
        base = f'{s["name"]} - question bank, {it["title"]}'
    else:
        base = f'{s["name"]} - {item_title(it)}'
    base = re.sub(r'[<>:"/\\|?*]', "", base)
    return f'{base}.{it["m"]["ext"]}'


def file_url(it):
    return f'/files/{it["id"]}.{it["m"]["ext"]}'


# ---------------------------------------------------------------- shell
def sidebar(current_slug=None):
    out = []
    for n, roman in SEMESTERS.items():
        subs = [s for s in SUBJECTS if s["sem"] == n]
        lis = []
        for s in subs:
            cur = ' aria-current="page"' if s["slug"] == current_slug else ""
            extra = f' <span class="side-note">{esc(short_group(s))}</span>' if s["group"] != "core" else ""
            lis.append(f'<li><a href="{subj_url(s)}"{cur}>{esc(s["name"])}{extra}</a></li>')
        out.append(f'<div class="side-sem s{n}"><h2><a href="/#sem-{n}">Semester {roman}</a></h2><ul>{"".join(lis)}</ul></div>')
    return "".join(out)


def short_group(s):
    return "older syllabus" if "older" in s.get("note", "") else ("other branch" if s["group"] == "other" else "other option")


def jump_options(current_slug=None):
    out = []
    for n, roman in SEMESTERS.items():
        opts = "".join(f'<option value="{subj_url(s)}"{" selected" if s["slug"] == current_slug else ""}>{esc(s["name"])}</option>'
                       for s in SUBJECTS if s["sem"] == n)
        out.append(f'<optgroup label="Semester {roman}">{opts}</optgroup>')
    first = "" if current_slug else '<option value="" selected>Choose a subject</option>'
    return first + "".join(out)


def page(path, title, desc, main, sem=None, current_slug=None, jsonld=None, extra_head=""):
    canonical = SITE + path
    semcls = f" s{sem}" if sem else ""
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    doc = f"""<!doctype html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
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
<script>try{{var t=localStorage.getItem("nb-theme");if(t==="light"||t==="dark")document.documentElement.setAttribute("data-theme",t)}}catch(e){{}}</script>
<link rel="stylesheet" href="/assets/site.css?v={V['css']}">
<script src="/assets/site.js?v={V['js']}" defer></script>
{extra_head}{ld}
</head>
<body class="{semcls.strip()}">
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
  <p>Shared by Harsh, IT Batch 2027, so juniors have last year's papers the night before. Not an official TCET site. <a href="https://harver.in">harver.in</a></p>
  <p data-contact hidden>Wrong label, broken page or a paper to add? <a href="#" data-email>Email Harsh</a>.</p>
  <p data-cookie-row hidden><button class="linklike" type="button" data-cookie-settings>Cookie settings</button></p>
</footer>
</div>
</div>
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


# ---------------------------------------------------------------- rows
def file_row(it):
    ext = it["m"]["ext"]
    label = row_label(it)
    ctx = esc(f'{subj_by[it["subject"]]["name"]}, {label}')
    return (f'<li class="file"><span class="ft {ext}">{ext.upper()}</span>'
            f'<div class="fname"><span>{esc(label)}</span><small>{esc(row_meta(it))}</small></div>'
            f'<a class="act" href="/view/{it["id"]}/">Open<span class="vh"> {ctx}</span></a>'
            f'<a class="act" href="{file_url(it)}" download="{esc(download_name(it))}">Download<span class="vh"> {ctx}</span></a></li>')


SYLLABUS_NOTE = ("The syllabus may have changed since Batch 2027 (TCET, University of Mumbai, CBCGS-HME 2023). "
                 "Check your current syllabus before trusting a module list.")


# ---------------------------------------------------------------- pages
def build_home():
    secs = []
    total_files = len(ITEMS)
    for n, roman in SEMESTERS.items():
        groups = {"core": [], "elective": [], "other": []}
        for s in SUBJECTS:
            if s["sem"] != n:
                continue
            p, q, no = items_of(s["slug"])
            bits = []
            if p:
                bits.append("papers " + ", ".join(str(i["year"]) for i in p))
            if q:
                bits.append(f'{len(q)} question bank{"s" if len(q) > 1 else ""}')
            if no:
                bits.append(f'{len(no)} notes file{"s" if len(no) > 1 else ""}')
            key = " ".join([s["name"], s.get("aka", ""), s["code"], f"sem {n} semester {roman}"]).lower()
            note = f' <span class="tag">{esc(s.get("note", ""))}</span>' if s.get("note") else ""
            groups[s["group"]].append(
                f'<li data-key="{esc(key)}"><a href="{subj_url(s)}"><span class="s-name">{esc(s["name"])}</span>'
                f'<span class="s-meta">{esc(s["code"] + " · " if s["code"] else "")}{esc(" · ".join(bits))}{note}</span></a></li>')
        body = f'<ul class="subjects">{"".join(groups["core"])}</ul>'
        if groups["elective"]:
            body += f'<h3>Other options in this semester</h3><ul class="subjects">{"".join(groups["elective"])}</ul>'
        if groups["other"]:
            body += f'<h3>Other branches and the older syllabus</h3><ul class="subjects">{"".join(groups["other"])}</ul>'
        secs.append(f'<section class="sem-block s{n}" id="sem-{n}" aria-labelledby="h-sem-{n}"><h2 id="h-sem-{n}">Semester {roman}</h2>{body}</section>')
    main = f"""
<h1>{NAME}</h1>
<p class="lead">Previous-year papers, question banks and notes for TCET IT, from semester III to VII. Open anything here, or download the original file.</p>
<p class="notice">{esc(SYLLABUS_NOTE)} Not an official TCET site.</p>
<div class="search">
  <label for="q">Find a subject</label>
  <input id="q" type="search" placeholder="DBMS, OS, Automata, DevOps" autocomplete="off" data-search>
  <p class="search-status" aria-live="polite" data-search-status>{len(SUBJECTS)} subjects, {total_files} files.</p>
</div>
<p class="search-empty" data-search-empty hidden>No subject matches that. Try a short name such as DBMS, CN or BDA, or clear the box to see every semester.</p>
{"".join(secs)}
"""
    ld = {"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": SITE + "/",
          "description": "Previous-year papers, question banks and notes for TCET IT students.",
          "author": {"@type": "Person", "name": "Harsh Verma", "url": "https://harver.in"}}
    page("/", f"{NAME}: TCET IT previous-year papers, question banks and notes",
         "Previous-year exam papers (ISE and ESE), question banks and notes for TCET IT, semesters III to VII. View on your phone or download.",
         main, jsonld=ld)


def build_subject(s):
    p, q, no = items_of(s["slug"])
    roman = SEMESTERS[s["sem"]]
    parts = []
    if p:
        parts.append(f'<section><h2>Previous-year papers</h2><ul class="files">{"".join(file_row(i) for i in p)}</ul></section>')
    if q:
        parts.append(f'<section><h2>Question bank{"s" if len(q) > 1 else ""}</h2><ul class="files">{"".join(file_row(i) for i in q)}</ul></section>')
    if no:
        parts.append(f'<section><h2>Notes</h2><ul class="files">{"".join(file_row(i) for i in no)}</ul></section>')
    sub = " · ".join(x for x in [s["code"], s.get("note", "")] if x)
    caution = ""
    if s["group"] == "other":
        caution = '<p class="notice">These papers come from another branch or an older syllabus. Many questions still overlap, so they are worth a look.</p>'
    main = f"""
<nav class="crumb" aria-label="Breadcrumb"><a href="/#sem-{s['sem']}">Semester {roman}</a></nav>
<h1>{esc(s['name'])}</h1>
{f'<p class="sub">{esc(sub)}</p>' if sub else ''}
{caution}
{"".join(parts)}
<p class="fine">{esc(SYLLABUS_NOTE)}</p>
"""
    what = [w for w, l in (("previous-year papers", p), ("question bank", q), ("notes", no)) if l]
    title = f'{s["name"]} {", ".join(what[:-1]) + " and " + what[-1] if len(what) > 1 else what[0]} (TCET IT Sem {roman}) | {NAME}'
    years = ", ".join(str(i["year"]) for i in p)
    desc = f'{s["name"]} for TCET IT semester {roman}: ' + "; ".join(
        x for x in [f"papers from {years} (ISE and ESE)" if p else "", f"{len(q)} question bank{'s' if len(q) > 1 else ''}" if q else "",
                    f"{len(no)} notes file{'s' if len(no) > 1 else ''}" if no else ""] if x) + ". View or download."
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": NAME, "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": f"Semester {roman}", "item": f"{SITE}/#sem-{s['sem']}"},
        {"@type": "ListItem", "position": 3, "name": s["name"], "item": SITE + subj_url(s)}]}
    page(subj_url(s), title, desc, main, sem=s["sem"], current_slug=s["slug"], jsonld=ld)


def build_view(it):
    s = subj_by[it["subject"]]
    m = it["m"]
    roman = SEMESTERS[s["sem"]]
    ext = m["ext"]
    head = f"""
<nav class="crumb" aria-label="Breadcrumb"><a href="/#sem-{s['sem']}">Semester {roman}</a> <span aria-hidden="true">/</span> <a href="{subj_url(s)}">{esc(s['name'])}</a></nav>
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
        frag, count, coloured = xlsx_to_html(src, m.get("figs", []), f'/pages/{it["id"]}/')
        legend = ""
        if coloured:
            legend = ('<p class="fine">Colours and highlights are the ones in the original sheet.'
                      + (' The sheet\'s own notes on them are under "Notes kept beside the questions".' if "qb-side" in frag else "")
                      + "</p>")
        body = f'<p class="fine">{count} questions, converted from the Excel file so it reads on a phone.</p>{legend}<div class="qb">{frag}</div>'
    else:
        src = os.path.join(ROOT, "files", f'{it["id"]}.docx')
        frag, _ = docx_to_html(src)
        body = f'<p class="fine">Converted from the Word file so it reads on a phone. The download is the original.</p><article class="prose">{frag}</article>'
    caution = '<p class="notice">From another branch or an older syllabus. The questions still overlap a lot.</p>' if it["kind"] == "paper" and not it["own"] and it["note"] else ""
    title = f'{s["name"]} {item_title(it)}{" (" + ", ".join(it["exams"]) + ")" if it["kind"] == "paper" else ""} | {NAME}'
    desc = f'{s["name"]}, TCET IT semester {roman}: {item_title(it)}. {row_meta(it)}.'
    page(f'/view/{it["id"]}/', title, desc, head + caution + body, sem=s["sem"], current_slug=s["slug"])


def build_404():
    main = """
<h1>Nothing here</h1>
<p class="lead">This address does not match a page. Files keep the same address once published, so the link may have a typo.</p>
<p><a class="btn-main" href="/">See every semester</a></p>
"""
    page("/404.html", f"Page not found | {NAME}", "This page does not exist on Night Before.", main)


def build_meta():
    urls = ["/"] + [subj_url(s) for s in SUBJECTS] + [f'/view/{i["id"]}/' for i in ITEMS]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join(f"  <url><loc>{SITE}{u}</loc><lastmod>{TODAY}</lastmod></url>\n" for u in urls) + "</urlset>\n"
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8", newline="\n").write(sm)
    open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8", newline="\n").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    lines = [f"# {NAME}", "", "> Previous-year exam papers (ISE and ESE), question banks and notes for TCET IT (University of Mumbai), "
             "semesters III to VII, shared by Harsh Verma from IT Batch 2027. Not an official TCET site. The syllabus may have changed since.", ""]
    for n, roman in SEMESTERS.items():
        lines.append(f"## Semester {roman}")
        for s in SUBJECTS:
            if s["sem"] == n:
                lines.append(f'- [{s["name"]}]({SITE}{subj_url(s)})' + (f': {s["note"]}' if s.get("note") else ""))
        lines.append("")
    open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8", newline="\n").write("\n".join(lines))


def main():
    for d in ("view", *[f"sem-{n}" for n in SEMESTERS]):
        shutil.rmtree(os.path.join(ROOT, d), ignore_errors=True)
    build_home()
    for s in SUBJECTS:
        if any(i["subject"] == s["slug"] for i in ITEMS):
            build_subject(s)
        else:
            raise SystemExit(f"Subject without files: {s['slug']}")
    for it in ITEMS:
        build_view(it)
    build_404()
    build_meta()
    print(f"Built home, {len(SUBJECTS)} subject pages, {len(ITEMS)} file pages.")


if __name__ == "__main__":
    main()
