"""Turn Excel question banks and Word notes into readable HTML fragments.

Excel: one list of questions per sheet. Marks and module columns become section dividers,
the other columns (CO, PYQ tags, remarks) sit under each question, cells keep their font and
fill colours (adjusted per theme for contrast), notes kept beside the table go into a
"Notes in the sheet" block, and pictures stay with the question they sit next to.
Word: headings, paragraphs, lists, tables, bold and italics.
"""
import colorsys, html, re, zipfile

EMOJI = re.compile("[\U0001F000-\U0001FAFF\uFE0F\u200D]")
MARKS = re.compile(r"^\(?\s*\d+\s*(m|marks?)\s*\)?\.?$", re.I)
MODULE = re.compile(r"^\s*mod(ule)?\s*[-:]?\s*\d+", re.I)
DARK_BG = (0x16, 0x17, 0x1A)   # list surface in dark mode
LIGHT_BG = (0xFF, 0xFF, 0xFF)


def esc(s):
    # Em dashes from the source files read as commas here (site copy rule: no em dashes).
    s = re.sub(r"\s*—\s*", ", ", s)
    return html.escape(s, quote=True)


# ---------------------------------------------------------------- colours
def _lum(rgb):
    def ch(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def tune(rgb, bg, target=4.8):
    """Move lightness until the colour reads on bg; keep the hue."""
    h, l, s = colorsys.rgb_to_hls(*(c / 255 for c in rgb))
    step = 0.02 if _lum(bg) < 0.5 else -0.02
    for _ in range(60):
        cur = tuple(round(c * 255) for c in colorsys.hls_to_rgb(h, l, s))
        if contrast(cur, bg) >= target:
            return cur
        l = min(1, max(0, l + step))
    return cur


def hexs(rgb):
    return "#%02x%02x%02x" % rgb


def apply_tint(rgb, tint):
    if not tint:
        return rgb
    h, l, s = colorsys.rgb_to_hls(*(c / 255 for c in rgb))
    l = l * (1 + tint) if tint < 0 else l * (1 - tint) + tint
    return tuple(round(c * 255) for c in colorsys.hls_to_rgb(h, l, s))


INDEXED = {2: "FF0000", 3: "00FF00", 4: "0000FF", 5: "FFFF00", 6: "FF00FF", 7: "00FFFF", 10: "FF0000",
           11: "00FF00", 12: "0000FF", 13: "FFFF00", 14: "FF00FF", 15: "00FFFF", 16: "800000", 17: "008000",
           18: "000080", 19: "808000", 20: "800080", 21: "008080", 53: "FF6600", 52: "FF9900", 51: "FFCC00"}


class Palette:
    def __init__(self, z):
        self.theme = []
        try:
            t = z.read("xl/theme/theme1.xml").decode("utf-8")
            scheme = re.search(r"<a:clrScheme[^>]*>(.*?)</a:clrScheme>", t, re.S).group(1)
            order = {}
            for name, body in re.findall(r"<a:(dk1|lt1|dk2|lt2|accent\d|hlink|folHlink)>(.*?)</a:\1>", scheme, re.S):
                m = re.search(r'(?:srgbClr val|lastClr)="([0-9A-Fa-f]{6})"', body)
                order[name] = m.group(1) if m else "000000"
            names = ["lt1", "dk1", "lt2", "dk2"] + [f"accent{i}" for i in range(1, 7)] + ["hlink", "folHlink"]
            self.theme = [order.get(n, "000000") for n in names]
        except Exception:
            pass

    def resolve(self, attrs):
        """attrs: the attribute string of a <color>/<fgColor> element. Returns (r,g,b) or None."""
        if not attrs or 'auto="1"' in attrs:
            return None
        m = re.search(r'rgb="(?:[0-9A-Fa-f]{2})?([0-9A-Fa-f]{6})"', attrs)
        hexv = None
        if m:
            hexv = m.group(1)
        else:
            m = re.search(r'theme="(\d+)"', attrs)
            if m and int(m.group(1)) < len(self.theme):
                hexv = self.theme[int(m.group(1))]
            else:
                m = re.search(r'indexed="(\d+)"', attrs)
                if m:
                    hexv = INDEXED.get(int(m.group(1)))
        if not hexv:
            return None
        rgb = tuple(int(hexv[i:i + 2], 16) for i in (0, 2, 4))
        t = re.search(r'tint="(-?[\d.]+)"', attrs)
        return apply_tint(rgb, float(t.group(1)) if t else 0)


def is_plain_text(rgb):
    return rgb is None or max(rgb) < 70 and max(rgb) - min(rgb) < 30       # black or near-black


def is_plain_fill(rgb):
    return rgb is None or min(rgb) > 235                                     # white


def color_style(rgb):
    d, l = tune(rgb, DARK_BG), tune(rgb, LIGHT_BG)
    return f"--cd:{hexs(d)};--cl:{hexs(l)}"


def fill_style(rgb):
    return f"--fill:rgba({rgb[0]},{rgb[1]},{rgb[2]},.26)"


# ---------------------------------------------------------------- xlsx
def _runs(si_xml, pal):
    """Rich text: list of (text, rgb or None, bold)."""
    runs = re.findall(r"<r>(.*?)</r>", si_xml, re.S)
    if not runs:
        t = "".join(re.findall(r"<t[^>]*>(.*?)</t>", si_xml, re.S))
        return [(html.unescape(t), None, False)]
    out = []
    for r in runs:
        rpr = re.search(r"<rPr>(.*?)</rPr>", r, re.S)
        rgb, bold = None, False
        if rpr:
            c = re.search(r"<color ([^>]*?)/>", rpr.group(1))
            rgb = pal.resolve(c.group(1)) if c else None
            bold = bool(re.search(r'<b(?: val="(?:1|true)")?/>', rpr.group(1)))
        t = "".join(re.findall(r"<t[^>]*>(.*?)</t>", r, re.S))
        out.append((html.unescape(t), rgb, bold))
    return out


def _col(ref):
    n = 0
    for ch in re.match(r"[A-Z]+", ref).group(0):
        n = n * 26 + ord(ch) - 64
    return n


def read_workbook(path):
    z = zipfile.ZipFile(path)
    names = z.namelist()
    pal = Palette(z)
    shared = []
    if "xl/sharedStrings.xml" in names:
        for si in re.findall(r"<si>(.*?)</si>", z.read("xl/sharedStrings.xml").decode("utf-8"), re.S):
            shared.append(_runs(si, pal))
    st = z.read("xl/styles.xml").decode("utf-8")
    fonts = []
    fblock = re.search(r"<fonts[^>]*>(.*?)</fonts>", st, re.S)
    for f in re.findall(r"<font(?:\s[^>]*)?>(.*?)</font>|<font\s*/>", fblock.group(1) if fblock else "", re.S):
        c = re.search(r"<color ([^>]*?)/>", f)
        fonts.append(dict(rgb=pal.resolve(c.group(1)) if c else None,
                          bold=bool(re.search(r'<b(?: val="(?:1|true)")?/>', f)),
                          strike=bool(re.search(r'<strike(?: val="(?:1|true)")?/>', f))))
    fills = []
    flblock = re.search(r"<fills[^>]*>(.*?)</fills>", st, re.S)
    for f in re.findall(r"<fill>(.*?)</fill>", flblock.group(1) if flblock else "", re.S):
        solid = 'patternType="solid"' in f
        c = re.search(r"<fgColor ([^>]*?)/>", f)
        fills.append(pal.resolve(c.group(1)) if (solid and c) else None)
    xfs = []
    xblock = re.search(r"<cellXfs[^>]*>(.*?)</cellXfs>", st, re.S)
    for x in re.findall(r"<xf ([^>]*?)/?>", xblock.group(1) if xblock else ""):
        fi = re.search(r'fontId="(\d+)"', x)
        fl = re.search(r'fillId="(\d+)"', x)
        xfs.append((int(fi.group(1)) if fi else 0, int(fl.group(1)) if fl else 0))
    wb = z.read("xl/workbook.xml").decode("utf-8")
    rels = z.read("xl/_rels/workbook.xml.rels").decode("utf-8")
    relmap = {}
    for m in re.finditer(r"<Relationship ([^>]*)/>", rels):
        a = m.group(1)
        i, t = re.search(r'Id="([^"]+)"', a), re.search(r'Target="([^"]+)"', a)
        if i and t:
            relmap[i.group(1)] = t.group(1)
    sheets = []
    for m in re.finditer(r"<sheet ([^>]*?)/>", wb):
        a = m.group(1)
        name = html.unescape(re.search(r'name="([^"]+)"', a).group(1))
        if re.search(r'state="(hidden|veryHidden)"', a):
            continue
        rid = re.search(r'r:id="([^"]+)"', a).group(1)
        target = relmap[rid].lstrip("/")
        target = target if target.startswith("xl/") else "xl/" + target
        x = z.read(target).decode("utf-8")
        rows = []
        for rm in re.finditer(r'<row [^>]*?r="(\d+)"[^>]*?(?:/>|>(.*?)</row>)', x, re.S):
            rnum, body = int(rm.group(1)), rm.group(2) or ""
            cells = {}
            for cm in re.finditer(r'<c r="([A-Z]+)\d+"([^>]*?)(?:/>|>(.*?)</c>)', body, re.S):
                ref, attrs, inner = cm.groups()
                if not inner:
                    continue
                t = re.search(r't="(\w+)"', attrs)
                s = re.search(r's="(\d+)"', attrs)
                v = re.search(r"<v>(.*?)</v>", inner, re.S)
                if t and t.group(1) == "s" and v:
                    runs = shared[int(v.group(1))]
                elif t and t.group(1) == "inlineStr":
                    runs = _runs(re.search(r"<is>(.*?)</is>", inner, re.S).group(1), pal)
                elif v:
                    val = html.unescape(v.group(1))
                    if re.fullmatch(r"-?\d+\.0+", val):
                        val = val.split(".")[0]
                    runs = [(val, None, False)]
                else:
                    continue
                text = "".join(r[0] for r in runs).strip()
                if not text:
                    continue
                font, fill = (0, 0)
                if s and int(s.group(1)) < len(xfs):
                    font, fill = xfs[int(s.group(1))]
                fo = fonts[font] if font < len(fonts) else dict(rgb=None, bold=False, strike=False)
                cells[_col(ref)] = dict(text=text, runs=runs, rgb=fo["rgb"], bold=fo["bold"], strike=fo["strike"],
                                        fill=fills[fill] if fill < len(fills) else None)
            if cells:
                rows.append((rnum, cells))
        sheets.append((name, rows))
    return sheets


def cell_html(c):
    parts = []
    base = c["rgb"]
    for text, rgb, bold in c["runs"]:
        text = EMOJI.sub("", text)
        if not text:
            continue
        col = rgb if rgb is not None else base
        h = esc(text).replace("\r\n", "\n").replace("\n", "<br>")
        if bold:
            h = f"<b>{h}</b>"
        if not is_plain_text(col):
            h = f'<span class="xc" style="{color_style(col)}">{h}</span>'
        parts.append(h)
    out = "".join(parts).strip()
    if c["strike"]:
        out = f"<s>{out}</s>"
    return out


def cell_classes(c):
    if not is_plain_fill(c["fill"]):
        return ' class="xf" style="%s"' % fill_style(c["fill"])
    return ""


def norm_marks(t):
    m = re.match(r"^\(?\s*(\d+)\s*(m|marks?)\s*\)?\.?$", t.strip(), re.I)
    return f"{m.group(1)} marks" if m else t.strip()


def xlsx_to_html(path, figs=(), img_base=""):
    sheets = [(n, r) for n, r in read_workbook(path) if sum(len(c) for _, c in r) >= 6]
    out, count = [], 0
    colours_used = False
    for sname, rows in sheets:
        cols = {}
        for _, cells in rows:
            for k, c in cells.items():
                cols.setdefault(k, []).append(c["text"])
        if not cols:
            continue
        qcol = max(cols, key=lambda k: sum(len(v) for v in cols[k]))
        numcol = qcol - 1 if (qcol - 1) in cols and sum(bool(re.fullmatch(r"\d+", v.strip())) for v in cols[qcol - 1]) > len(cols[qcol - 1]) * 0.6 else None
        # main block: contiguous columns starting at the first used column
        main, k = set(), min(cols)
        while k in cols or (k + 1) in cols and k < qcol:
            main.add(k)
            k += 1
        marks_cols = {k for k in cols if k != qcol and k != numcol and
                      sum(bool(MARKS.match(v)) for v in cols[k]) >= max(2, 0.7 * len(cols[k]))}
        header_idx = next((i for i, (_, c) in enumerate(rows) if qcol in c and c[qcol]["text"].strip().lower().rstrip(":") in ("questions", "question")), None)
        first_q = next((i for i, (_, c) in enumerate(rows) if numcol and numcol in c and re.fullmatch(r"\d+", c[numcol]["text"].strip())), 0)
        info_end = header_idx if header_idx is not None else first_q
        info, side, items = [], [], []
        used, used_fill = {}, {}
        fig_rows = {}
        for f in figs:
            if f["sheet"] == sname:
                fig_rows.setdefault(f["row"], []).append(f)
        last_marks = None
        for i, (rnum, cells) in enumerate(rows):
            sidecells = {k: c for k, c in cells.items() if k not in main and not MODULE.match(c["text"])}
            if sidecells:
                side.append((rnum, sidecells))
            cells = {k: c for k, c in cells.items() if k in main or MODULE.match(c["text"])}
            if i < info_end:
                if cells:
                    info.append(" ".join(cell_html(cells[k]) for k in sorted(cells)))
                continue
            if i == header_idx:
                continue
            for k in sorted(cells):
                if MODULE.match(cells[k]["text"]) and k != qcol:
                    items.append(("div", f'<h3 class="qb-mod">{cell_html(cells[k])}</h3>', rnum))
            for k in sorted(marks_cols):
                if k in cells and cells[k]["text"].strip() != last_marks:
                    last_marks = cells[k]["text"].strip()
                    items.append(("div", f'<h4 class="qb-marks">{esc(norm_marks(last_marks))}</h4>', rnum))
            q = cells.get(qcol)
            meta = [cell_html(cells[k]) for k in sorted(cells)
                    if k not in (qcol, numcol) and k not in marks_cols and not MODULE.match(cells[k]["text"])]
            num = cells[numcol]["text"].strip() if numcol and numcol in cells else ""
            if q is None:
                if num and rnum in fig_rows:
                    # The question is a picture on the sheet (an equation, a table, a figure).
                    count += 1
                    body = '<p class="qb-meta">' + " · ".join(meta) + "</p>" if meta else ""
                    items.append(("q", (num, body, ""), rnum))
                elif meta:
                    items.append(("div", f'<h4 class="qb-marks">{" ".join(meta)}</h4>', rnum))
                continue
            count += 1
            for _t, rgb, _b in q["runs"]:
                fam = family(rgb if rgb is not None else q["rgb"])
                if fam and not is_plain_text(rgb if rgb is not None else q["rgb"]):
                    used.setdefault(fam, rgb if rgb is not None else q["rgb"])
            if not is_plain_fill(q["fill"]) and family(q["fill"]):
                used_fill.setdefault(family(q["fill"]), q["fill"])
            body = f'<p class="qb-q">{cell_html(q)}</p>'
            if meta:
                body += '<p class="qb-meta">' + " <span aria-hidden=\"true\">·</span> ".join(meta) + "</p>"
            items.append(("q", (num, body, cell_classes(q)), rnum))
        qrows = [r for kind, _, r in items if kind == "q"]

        def nearest_q(row):
            above = [r for r in qrows if r <= row]
            return max(above) if above else (min(qrows) if qrows else row)

        # attach pictures to the nearest question at or above their row
        attach = {}
        for frow, fl in fig_rows.items():
            attach.setdefault(nearest_q(frow), []).extend(fl)
        # Cells typed beside the table: count tables, colour legends, or notes about one question.
        legend, notes, table_rows = [], {}, []
        for rnum, sc in side:
            texts = [c["text"].strip() for c in sc.values()]
            if len(sc) >= 2 and all(len(t) <= 14 for t in texts):
                table_rows.append((rnum, sc))
                continue
            for k in sorted(sc):
                c = sc[k]
                if LEGEND.search(c["text"]):
                    legend.append(c)
                else:
                    notes.setdefault(nearest_q(rnum), []).append(cell_html(c))
        colours_used = colours_used or bool(used or used_fill)
        if len(sheets) > 1:
            out.append(f'<h2 class="qb-sheet">{esc(sname.strip())}</h2>')
        if info:
            out.append('<div class="qb-info">' + "".join(f"<p>{x}</p>" for x in info) + "</div>")
        out.append(colour_key(legend, used, used_fill))
        out.append('<ol class="qb-list">')
        for kind, val, rnum in items:
            if kind == "div":
                out.append(f'</ol>{val}<ol class="qb-list">')
                continue
            num, body, cls = val
            for n in notes.get(rnum, []):
                body += f'<p class="qb-note"><span>Note from Harsh:</span> {n}</p>'
            figs_html = ""
            for f in attach.get(rnum, []):
                figs_html += (f'<img class="qb-fig" src="{img_base}{f["file"]}" width="{f["w"]}" height="{f["h"]}" '
                              f'loading="lazy" alt="Picture from the sheet for question {esc(num) or "above"}">')
            out.append(f'<li{cls}><span class="qb-n">{esc(num)}</span><div>{body}{figs_html}</div></li>')
        out.append("</ol>")
        if table_rows:
            ncols = sorted({k for _, c in table_rows for k in c})
            trs = "".join("<tr>" + "".join(f"<td{cell_classes(c[k]) if k in c else ''}>{cell_html(c[k]) if k in c else ''}</td>" for k in ncols) + "</tr>"
                          for _, c in table_rows)
            out.append('<details class="qb-side"><summary>Counts kept beside the questions in this sheet</summary>'
                       f'<div class="table-wrap"><table>{trs}</table></div></details>')
    html_out = "\n".join(out).replace('<ol class="qb-list"></ol>', "")
    return html_out, count, colours_used


LEGEND = re.compile(r"(?i)\b(means?|is the repetition|stands for|indicates?)\b")
COLOUR_WORDS = {"blue": "blue", "red": "red", "green": "green", "yellow": "yellow", "orange": "orange",
                "purple": "purple", "violet": "purple", "pink": "red"}
STANDARD = {"blue": (0, 112, 192), "red": (255, 0, 0), "green": (0, 176, 80), "yellow": (255, 255, 0),
            "orange": (255, 192, 0), "purple": (112, 48, 160)}
USUAL = {"blue": "Asked in a previous-year paper (PYQ)", "red": "Repeated in this question bank",
         "green": "The repeated copy of a red question"}


def family(rgb):
    if rgb is None:
        return None
    h, l, s = colorsys.rgb_to_hls(*(c / 255 for c in rgb))
    if s < 0.25 or l > 0.93 or l < 0.08:
        return None
    deg = h * 360
    if deg < 15 or deg >= 330:
        return "red"
    if deg < 42:
        return "orange"
    if deg < 70:
        return "yellow"
    if deg < 170:
        return "green"
    if deg < 260:
        return "blue"
    return "purple"


def swatch(rgb, fill=False):
    style = fill_style(rgb).replace(".26)", ".55)") if fill else color_style(rgb)
    return f'<span class="sw{" fill" if fill else ""}" style="{style}" aria-hidden="true"></span>'


def colour_key(legend, used, used_fill):
    """The sheet's own legend if it has one, otherwise Harsh's usual colour pattern."""
    if legend:
        lis = []
        for c in legend:
            word = next((COLOUR_WORDS[w] for w in re.findall(r"[a-z]+", c["text"].lower()) if w in COLOUR_WORDS), None)
            sw = swatch(used.get(word) or STANDARD[word]) if word else ""
            lis.append(f"<li>{sw}{cell_html(c)}</li>")
        return ('<div class="qb-key"><p class="qb-key-h">Colour key, as written in this sheet</p>'
                f'<ul>{"".join(lis)}</ul></div>')
    if not (used or used_fill):
        return ""
    lis = []
    for fam in ("blue", "red", "green"):
        if fam in used:
            lis.append(f"<li>{swatch(used[fam])}{fam.capitalize()}: {esc(USUAL[fam])}</li>")
    others = [f for f in used if f not in USUAL]
    for fam in others:
        lis.append(f"<li>{swatch(used[fam])}{fam.capitalize()} text: Harsh's own mark</li>")
    for fam, rgb in used_fill.items():
        lis.append(f"<li>{swatch(rgb, fill=True)}{fam.capitalize()} highlight: Harsh's own mark</li>")
    return ('<div class="qb-key"><p class="qb-key-h">Colour key, Harsh\'s usual pattern</p>'
            f'<ul>{"".join(lis)}</ul></div>')


# ---------------------------------------------------------------- docx
def _num_formats(z):
    fmts = {}
    if "word/numbering.xml" not in z.namelist():
        return fmts
    x = z.read("word/numbering.xml").decode("utf-8")
    abstract = {}
    for aid, body in re.findall(r'<w:abstractNum [^>]*w:abstractNumId="(\d+)"[^>]*>(.*?)</w:abstractNum>', x, re.S):
        lv = {}
        for ilvl, lb in re.findall(r'<w:lvl [^>]*w:ilvl="(\d+)"[^>]*>(.*?)</w:lvl>', body, re.S):
            f = re.search(r'<w:numFmt w:val="([^"]+)"', lb)
            lv[int(ilvl)] = f.group(1) if f else "bullet"
        abstract[aid] = lv
    for nid, aid in re.findall(r'<w:num w:numId="(\d+)"[^>]*>.*?<w:abstractNumId w:val="(\d+)"', x, re.S):
        fmts[nid] = abstract.get(aid, {})
    return fmts


def _para_runs(p):
    out = []
    for r in re.findall(r"<w:r(?:\s[^>]*)?>(.*?)</w:r>", p, re.S):
        rpr = re.search(r"<w:rPr>(.*?)</w:rPr>", r, re.S)
        rp = rpr.group(1) if rpr else ""
        bold = bool(re.search(r'<w:b(?: w:val="(?:1|true|on)")?/>', rp))
        ital = bool(re.search(r'<w:i(?: w:val="(?:1|true|on)")?/>', rp))
        body = re.sub(r"<w:rPr>.*?</w:rPr>", "", r, flags=re.S)
        for rid in re.findall(r'<a:blip [^>]*r:embed="([^"]+)"|<v:imagedata [^>]*r:id="([^"]+)"', body):
            rid = rid[0] or rid[1]
            if rid in _DOC_IMGS:
                out.append(("\x00IMG:" + rid, False, False))
        text = ""
        for m in re.finditer(r"<w:t(?:\s[^>]*)?>(.*?)</w:t>|<w:(br|cr)\b[^>]*/>|<w:tab/>", body, re.S):
            if m.group(1) is not None:
                text += html.unescape(m.group(1))
            elif m.group(2):
                text += "\n"
            else:
                text += " "
        text = EMOJI.sub("", text)
        if text:
            out.append((text, bold, ital))
    return out


_DOC_IMGS, _DOC_IMG_BASE = {}, ""


def _runs_html(runs):
    h = ""
    for text, bold, ital in runs:
        if text.startswith("\x00IMG:"):
            im = _DOC_IMGS[text[5:]]
            h += (f'<img class="doc-fig" src="{_DOC_IMG_BASE}{im["file"]}" width="{im["w"]}" height="{im["h"]}" '
                  f'loading="lazy" alt="Picture from the document">')
            continue
        t = esc(text).replace("\n", "<br>")
        if bold:
            t = f"<b>{t}</b>"
        if ital:
            t = f"<i>{t}</i>"
        h += t
    return h.strip()


def docx_to_html(path, imgs=None, img_base=""):
    """imgs: {relationship id: {file, w, h}} from prepare.py, for pictures in the document."""
    global _DOC_IMGS, _DOC_IMG_BASE
    _DOC_IMGS, _DOC_IMG_BASE = imgs or {}, img_base
    z = zipfile.ZipFile(path)
    fmts = _num_formats(z)
    x = z.read("word/document.xml").decode("utf-8")
    body = re.search(r"<w:body>(.*)</w:body>", x, re.S).group(1)
    # Google Docs exports put horizontal rules inside a paragraph; split the paragraph there.
    body = re.sub(r'<w:r\b(?:(?!</w:r>).)*?o:hr="t"(?:(?!</w:r>).)*?</w:r>',
                  "</w:p><w:p><w:r><w:t>__HR__</w:t></w:r></w:p><w:p>", body, flags=re.S)
    out, list_stack = [], []
    headings = 0

    def close_lists(level=-1):
        while len(list_stack) > level + 1:
            out.append(f"</li></{list_stack.pop()}>")

    for m in re.finditer(r"<w:tbl>.*?</w:tbl>|<w:p(?:\s[^>]*)?>.*?</w:p>|<w:p(?:\s[^>]*)?/>", body, re.S):
        block = m.group(0)
        if block.startswith("<w:tbl>"):
            close_lists()
            rows = []
            for tr in re.findall(r"<w:tr(?:\s[^>]*)?>(.*?)</w:tr>", block, re.S):
                cells = []
                for tc in re.findall(r"<w:tc>(.*?)</w:tc>", tr, re.S):
                    paras = [_runs_html(_para_runs(p)) for p in re.findall(r"<w:p(?:\s[^>]*)?>(.*?)</w:p>", tc, re.S)]
                    cells.append("<br>".join(p for p in paras if p))
                rows.append(cells)
            if rows:
                head = rows[0]
                trs = "<tr>" + "".join(f"<th>{c}</th>" for c in head) + "</tr>"
                trs += "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows[1:])
                out.append(f'<div class="table-wrap"><table>{trs}</table></div>')
            continue
        style = re.search(r'<w:pStyle w:val="([^"]+)"', block)
        style = style.group(1) if style else ""
        runs = _para_runs(block)
        text = _runs_html(runs)
        if not text:
            continue
        plain = "".join(r[0] for r in runs).strip()
        if plain == "__HR__":
            close_lists()
            out.append("<hr>")
            continue
        num = re.search(r'<w:numPr>.*?<w:ilvl w:val="(\d+)"/>.*?<w:numId w:val="(\d+)"/>', block, re.S) or \
            re.search(r'<w:numPr>.*?<w:numId w:val="(\d+)"/>', block, re.S)
        hl = re.match(r"(?i)heading\s*(\d)", style) or re.match(r"(?i)^title$", style)
        all_bold = runs and all(r[1] for r in runs if r[0].strip())
        if hl or (all_bold and len(plain) < 90 and not num):
            close_lists()
            level = int(hl.group(1)) if hl and hl.groups() and hl.group(1) else (1 if hl else 3)
            tag = f"h{min(5, level + 1)}"
            headings += 1
            out.append(f"<{tag}>{_runs_html([(t, False, i) for t, b, i in runs])}</{tag}>")
            continue
        if num and fmts:
            if num.lastindex == 2:
                ilvl, nid = int(num.group(1)), num.group(2)
            else:
                ilvl, nid = 0, num.group(1)
            fmt = fmts.get(nid, {}).get(ilvl, "bullet")
            tag = "ul" if fmt in ("bullet", "none") else "ol"
            if len(list_stack) > ilvl + 1:
                close_lists(ilvl)
                out.append("</li><li>" + text)
            elif len(list_stack) == ilvl + 1:
                if list_stack[-1] != tag:
                    close_lists(ilvl - 1)
                    list_stack.append(tag)
                    out.append(f"<{tag}><li>{text}")
                else:
                    out.append(f"</li><li>{text}")
            else:
                while len(list_stack) < ilvl + 1:
                    list_stack.append(tag)
                    out.append(f"<{tag}><li>" + (text if len(list_stack) == ilvl + 1 else ""))
            continue
        close_lists()
        out.append(f"<p>{text}</p>")
    close_lists()
    # A rule nested deeper (inside a link or field) stays in its paragraph: show it as a blank line.
    return re.sub(r"(?:<br>)*__HR__(?:<br>)*", "<br><br>", "\n".join(out)), headings
