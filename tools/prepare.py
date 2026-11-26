"""Make the public copies of every file in catalog.py.

- Whole PDFs: copied with document properties removed (author, title, XMP). Text layers stay.
- Paper sets from the combined PDFs: pages re-rendered at 150 dpi into a new PDF, with the
  cover boxes from catalog.NAME_BOXES painted into the pixels (nothing hidden underneath).
- Excel and Word files: copied with author, last editor and company cleared.
- Page images (WebP) for the on-site viewer, and Excel drawings for the readable pages.

Run from anywhere: python tools/prepare.py   (add --force to redo everything)
Writes files/, pages/ and tools/manifest.json. Sources are only read.
"""
import glob, hashlib, io, json, os, re, sys, zipfile

import pymupdf
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
from catalog import ITEMS, item_id  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = os.path.join(ROOT, "files")
PAGES = os.path.join(ROOT, "pages")
MANIFEST = os.path.join(ROOT, "tools", "manifest.json")
VIEW_WIDTH = 1100      # px, page images for the viewer
VIEW_QUALITY = 58
SPLIT_DPI = 150        # re-rendered paper sets
SPLIT_QUALITY = 68


def resolve(src):
    hits = glob.glob(src)
    if len(hits) != 1:
        raise SystemExit(f"Source not found or ambiguous: {src} -> {hits}")
    return hits[0]


def spec_hash(it, src):
    st = os.stat(src)
    key = json.dumps([it.get("pages"), it.get("redact"), st.st_size, int(st.st_mtime), VIEW_WIDTH, VIEW_QUALITY, 3],
                     sort_keys=True, default=str)
    return hashlib.sha1(key.encode()).hexdigest()[:12]


def scrub_pdf(src, out):
    doc = pymupdf.open(src)
    # Keep the invisible OCR text and links; drop properties, XMP, thumbnails, attachments, scripts.
    doc.scrub(hidden_text=False, remove_links=False, clean_pages=False, redactions=False, reset_fields=False)
    doc.set_metadata({})
    doc.del_xml_metadata()
    doc.save(out, garbage=4, deflate=True)
    doc.close()


def split_pdf(src, pages, redact, out):
    srcdoc = pymupdf.open(src)
    new = pymupdf.open()
    for n in pages:
        pg = srcdoc[n - 1]
        pix = pg.get_pixmap(dpi=SPLIT_DPI)
        im = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
        boxes = redact.get(n) or redact.get(str(n)) or []
        if boxes:
            dr = ImageDraw.Draw(im)
            W, H = im.size
            for x0, y0, x1, y1 in boxes:
                dr.rectangle([int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H)], fill=(238, 238, 234))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=SPLIT_QUALITY, optimize=True)
        p = new.new_page(width=pg.rect.width, height=pg.rect.height)
        p.insert_image(p.rect, stream=buf.getvalue())
    new.set_metadata({})
    new.save(out, garbage=4, deflate=True)
    new.close()
    srcdoc.close()


def page_images(pdf_path, outdir):
    os.makedirs(outdir, exist_ok=True)
    for f in os.listdir(outdir):
        os.remove(os.path.join(outdir, f))
    doc = pymupdf.open(pdf_path)
    dims = []
    for i, pg in enumerate(doc):
        zoom = VIEW_WIDTH / pg.rect.width
        pix = pg.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
        im = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
        im.save(os.path.join(outdir, f"{i + 1}.webp"), "WEBP", quality=VIEW_QUALITY, method=4)
        dims.append([im.width, im.height])
    doc.close()
    return dims


CORE_FIELDS = ("dc:creator", "cp:lastModifiedBy", "dc:title", "dc:subject", "cp:keywords", "dc:description", "cp:lastPrinted")
APP_FIELDS = ("Company", "Manager")


def scrub_office(src, out):
    zin = zipfile.ZipFile(src)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename == "docProps/custom.xml":
                continue
            if info.filename == "docProps/core.xml":
                text = data.decode("utf-8")
                for tag in CORE_FIELDS:
                    text = re.sub(rf"<{tag}(\s[^>]*)?>.*?</{tag}>", f"<{tag}></{tag}>", text, flags=re.S)
                data = text.encode("utf-8")
            elif info.filename == "docProps/app.xml":
                text = data.decode("utf-8")
                for tag in APP_FIELDS:
                    text = re.sub(rf"<{tag}>.*?</{tag}>", f"<{tag}></{tag}>", text, flags=re.S)
                data = text.encode("utf-8")
            elif info.filename == "[Content_Types].xml":
                data = re.sub(rb'<Override PartName="/docProps/custom.xml"[^>]*/>', b"", data)
            elif info.filename == "_rels/.rels":
                data = re.sub(rb'<Relationship [^>]*Target="docProps/custom.xml"[^>]*/>', b"", data)
            zout.writestr(info, data)


def docx_images(src, outdir):
    """Pictures placed in a Word document, keyed by their relationship id."""
    z = zipfile.ZipFile(src)
    names = z.namelist()
    if "word/_rels/document.xml.rels" not in names:
        return {}
    rels = dict(re.findall(r'Id="([^"]+)"[^>]*Target="(media/[^"]+)"', z.read("word/_rels/document.xml.rels").decode("utf-8")))
    rels.update({b: a for a, b in re.findall(r'Target="(media/[^"]+)"[^>]*Id="([^"]+)"', z.read("word/_rels/document.xml.rels").decode("utf-8"))})
    doc = z.read("word/document.xml").decode("utf-8")
    used = set(re.findall(r'r:embed="([^"]+)"', doc)) | set(re.findall(r'<v:imagedata [^>]*r:id="([^"]+)"', doc))
    out = {}
    for rid in sorted(used):
        if rid not in rels or "word/" + rels[rid] not in names:
            continue
        try:
            im = Image.open(io.BytesIO(z.read("word/" + rels[rid]))).convert("RGB")
        except Exception:
            continue  # not a picture Pillow can read (for example an embedded EMF)
        if im.width > 1000:
            im = im.resize((1000, int(im.height * 1000 / im.width)))
        os.makedirs(outdir, exist_ok=True)
        name = f"doc-{len(out) + 1}.webp"
        im.save(os.path.join(outdir, name), "WEBP", quality=80)
        out[rid] = dict(file=name, w=im.width, h=im.height)
    return out


def xlsx_drawings(src, outdir):
    """Extract images placed on sheets, with the cell they are anchored to."""
    z = zipfile.ZipFile(src)
    names = z.namelist()
    wb = z.read("xl/workbook.xml").decode("utf-8")
    rels = z.read("xl/_rels/workbook.xml.rels").decode("utf-8")
    relmap = {m.group(1): m.group(2) for m in re.finditer(r'<Relationship [^>]*Id="([^"]+)"[^>]*Target="([^"]+)"', rels)}
    relmap.update({m.group(2): m.group(1) for m in re.finditer(r'<Relationship [^>]*Target="([^"]+)"[^>]*Id="([^"]+)"', rels)})
    figs = []
    for sheet_name, rid in re.findall(r'<sheet [^>]*name="([^"]+)"[^>]*r:id="([^"]+)"', wb):
        target = relmap[rid].lstrip("/")
        target = target if target.startswith("xl/") else "xl/" + target
        srels = target.replace("worksheets/", "worksheets/_rels/") + ".rels"
        if srels not in names:
            continue
        for dtarget in re.findall(r'Target="([^"]*drawings/drawing\d+\.xml)"', z.read(srels).decode("utf-8")):
            dpath = os.path.normpath(os.path.join(os.path.dirname(target), dtarget)).replace("\\", "/")
            dxml = z.read(dpath).decode("utf-8")
            drels_path = dpath.replace("drawings/", "drawings/_rels/") + ".rels"
            drels = dict(re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"', z.read(drels_path).decode("utf-8"))) if drels_path in names else {}
            for anchor in re.findall(r"<xdr:(?:twoCellAnchor|oneCellAnchor)[^>]*>(.*?)</xdr:(?:twoCellAnchor|oneCellAnchor)>", dxml, re.S):
                m = re.search(r"<xdr:from><xdr:col>(\d+)</xdr:col>.*?<xdr:row>(\d+)</xdr:row>", anchor, re.S)
                e = re.search(r'r:embed="([^"]+)"', anchor)
                if not (m and e and e.group(1) in drels):
                    continue
                media = os.path.normpath(os.path.join(os.path.dirname(dpath), drels[e.group(1)])).replace("\\", "/")
                im = Image.open(io.BytesIO(z.read(media))).convert("RGB")
                if im.width > 1000:
                    im = im.resize((1000, int(im.height * 1000 / im.width)))
                os.makedirs(outdir, exist_ok=True)
                name = f"fig-{len(figs) + 1}.webp"
                im.save(os.path.join(outdir, name), "WEBP", quality=80)
                figs.append(dict(sheet=sheet_name, row=int(m.group(2)) + 1, col=int(m.group(1)) + 1,
                                 file=name, w=im.width, h=im.height))
    return figs


def main():
    force = "--force" in sys.argv
    os.makedirs(FILES, exist_ok=True)
    os.makedirs(PAGES, exist_ok=True)
    manifest = {}
    if os.path.exists(MANIFEST) and not force:
        manifest = json.load(open(MANIFEST, encoding="utf-8"))
    keep = set()
    for it in ITEMS:
        iid = item_id(it)
        if iid in keep:
            raise SystemExit(f"Duplicate id {iid}")
        keep.add(iid)
        src = resolve(it["src"])
        ext = os.path.splitext(src)[1].lower().lstrip(".")
        out = os.path.join(FILES, f"{iid}.{ext}")
        h = spec_hash(it, src)
        old = manifest.get(iid)
        if old and old.get("hash") == h and os.path.exists(out):
            continue
        entry = dict(hash=h, ext=ext, source=os.path.basename(src))
        if ext == "pdf":
            if it.get("pages"):
                split_pdf(src, it["pages"], it.get("redact", {}), out)
            else:
                scrub_pdf(src, out)
            entry["img"] = page_images(out, os.path.join(PAGES, iid))
            entry["pages"] = len(entry["img"])
        elif ext in ("xlsx", "docx"):
            scrub_office(src, out)
            if ext == "xlsx":
                entry["figs"] = xlsx_drawings(src, os.path.join(PAGES, iid))
            else:
                entry["docimgs"] = docx_images(src, os.path.join(PAGES, iid))
        else:
            raise SystemExit(f"Unexpected file type: {src}")
        entry["size"] = os.path.getsize(out)
        manifest[iid] = entry
        print(f"made {iid}.{ext}  {entry['size'] / 1e6:.2f} MB  pages={entry.get('pages', '-')}")
    # Drop outputs for items no longer in the catalogue.
    for iid in list(manifest):
        if iid not in keep:
            manifest.pop(iid)
    json.dump(manifest, open(MANIFEST, "w", encoding="utf-8"), indent=1, sort_keys=True)
    for f in os.listdir(FILES):
        if os.path.splitext(f)[0] not in keep:
            os.remove(os.path.join(FILES, f))
    for d in os.listdir(PAGES):
        if d not in keep:
            for f in os.listdir(os.path.join(PAGES, d)):
                os.remove(os.path.join(PAGES, d, f))
            try:
                os.rmdir(os.path.join(PAGES, d))
            except OSError as e:  # Windows sometimes holds an empty folder for a moment; the next run removes it
                print(f"could not remove pages/{d} yet: {e.strerror}")
    total = sum(os.path.getsize(os.path.join(dp, f)) for base in (FILES, PAGES) for dp, _, fs in os.walk(base) for f in fs)
    print(f"{len(manifest)} items, files + page images = {total / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
