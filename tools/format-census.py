#!/usr/bin/env python3
"""format-census.py — count the images each delivery format of ONE book actually carries.

Usage:
  format-census.py --pdf book.pdf --epub book.epub --docx book.docx [--html source.html --src-dir DIR] [--min-ratio 0.5]

Reads each file as a zip/PDF and reports, per format: raster files, vector
files, image references, and alt text split as d/e/m = described / deliberately
empty (alt="") / missing attribute. Compares EPUB and DOCX against the PDF's
raster count and exits 1 if either carries fewer than --min-ratio of it
(default 0.5 - a heuristic tripwire, not a retail standard).

What it can and cannot see (do not read more into the table than this):
  - PDF: raster images via `pdfimages -list`. Vector artwork (SVG figures flattened to
    paths) is NOT counted, so the PDF column is a floor, never a total. `min ppi` is the
    lowest of the x and y effective resolutions. Alt text does not survive into a plain PDF: n/a.
  - EPUB: image files, <img>/<image> refs and inline <svg> in the content documents, and the
    alt split. An <svg> that only wraps an <image> (a pandoc cover page) counts as a reference, not artwork.
  - DOCX: files under word/media, and how many drawings carry a description (alt).
  - HTML source (optional): <img> tags and inline <svg>. CSS background-image artwork is
    visible in the PDF and invisible to every one of these counters.
HTML is read with the standard library's parser, so single-quoted attributes, unquoted
attributes and a ">" inside an attribute value are handled.

With --html + --src-dir + --epub it also compares raster image bytes in reading order
(SHA-256), so "same images, same order" is tested, not assumed. PDF order is not tested:
pdfimages re-encodes, so bytes cannot be matched back to the source.

Exit codes: 0 = no format below threshold; 1 = a genuine FAIL (a format below the ratio,
or the image order differs); 2 = usage error; 3 = the tool could not run (a required
program such as pdfimages is missing, or a file is missing/unreadable). 3 is never a verdict
on the book.
Needs: python3 stdlib, and `pdfimages` (poppler) on PATH only for --pdf.
"""
import argparse, hashlib, os, posixpath, re, shutil, subprocess, sys, zipfile
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

IMG_EXT = re.compile(r"\.(png|jpe?g|gif|webp|svg)$", re.I)


class ToolError(Exception):
    """The census could not run. Exit 3; says nothing about the book."""


class ImgScan(HTMLParser):
    """Collects <img> attributes, <image> hrefs, and inline <svg> (with or without a wrapped <image>)."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.imgs = []          # list of attr dicts; a valueless attribute reads as ""
        self.order = []         # ("img"|"image", target) in document order
        self.svg_art = 0        # inline <svg> that is artwork
        self.svg_wrappers = 0   # inline <svg> that only wraps an <image>
        self._svg = []

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v if v is not None else "") for k, v in attrs}
        if tag == "img":
            self.imgs.append(a)
            if "src" in a: self.order.append(("img", a["src"]))
        elif tag == "svg":
            self._svg.append(False)
        elif tag == "image":
            if self._svg: self._svg[-1] = True
            ref = a.get("href") or a.get("xlink:href")
            if ref: self.order.append(("image", ref))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag == "svg": self.handle_endtag("svg")

    def handle_endtag(self, tag):
        if tag == "svg" and self._svg:
            if self._svg.pop(): self.svg_wrappers += 1
            else: self.svg_art += 1


def scan(text):
    p = ImgScan(); p.feed(text); p.close()
    return p


def alt_split(imgs):
    """(described, deliberately-empty, missing-attribute) for a list of <img> attribute dicts."""
    d = e = m = 0
    for a in imgs:
        if "alt" not in a: m += 1
        elif a["alt"].strip(): d += 1
        else: e += 1
    return f"{d}/{e}/{m}"


def is_svg(src):
    return src.lower().split("?")[0].endswith(".svg")


def parse_pdfimages(text):
    rows = [l.split() for l in text.splitlines()[2:] if l.strip()]
    imgs = [r for r in rows if len(r) > 2 and r[2] == "image"]
    ppis = [int(r[i]) for r in imgs for i in (12, 13) if len(r) > i and r[i].isdigit()]
    return {"raster": len(imgs), "vector": None, "refs": None, "alt": None,
            "min_ppi": min(ppis) if ppis else None,
            "colorspaces": sorted({r[5] for r in imgs if len(r) > 5})}


def pdf_census(path):
    if not shutil.which("pdfimages"):
        raise ToolError("pdfimages (poppler) not found on PATH. Install it (macOS: brew install poppler) and re-run. "
                        "This is a missing tool, not a finding about the book.")
    out = subprocess.run(["pdfimages", "-list", path], capture_output=True, text=True)
    if out.returncode != 0:
        raise ToolError(f"pdfimages could not read {path}: {out.stderr.strip()}")
    return parse_pdfimages(out.stdout)


def zip_open(path):
    try:
        return zipfile.ZipFile(path)
    except (OSError, zipfile.BadZipFile) as e:
        raise ToolError(f"cannot open {path} as a zip: {e}")


def epub_docs(z):
    return [n for n in z.namelist() if n.lower().endswith((".xhtml", ".html", ".htm"))]


def epub_census(path):
    z = zip_open(path)
    files = [n for n in z.namelist() if IMG_EXT.search(n)]
    imgs, art, wrap = [], 0, 0
    for d in epub_docs(z):
        s = scan(z.read(d).decode("utf8", "replace"))
        imgs += s.imgs; art += s.svg_art; wrap += s.svg_wrappers
    raster = [n for n in files if not n.lower().endswith(".svg")]
    return {"raster": len(raster), "vector": art + len(files) - len(raster),
            "refs": len(imgs) + art + wrap, "alt": alt_split(imgs)}


def docx_census(path):
    z = zip_open(path)
    media = [n for n in z.namelist() if n.startswith("word/media/")]
    try:
        root = ET.fromstring(z.read("word/document.xml"))
    except (KeyError, ET.ParseError) as e:
        raise ToolError(f"cannot read word/document.xml in {path}: {e}")
    pr = [el for el in root.iter() if el.tag.endswith("}docPr")]
    d = sum(1 for el in pr if el.get("descr", "").strip())
    e = sum(1 for el in pr if "descr" in el.attrib and not el.get("descr", "").strip())
    svg = [n for n in media if n.lower().endswith(".svg")]
    return {"raster": len(media) - len(svg), "vector": len(svg), "refs": len(pr),
            "alt": f"{d}/{e}/{len(pr) - d - e}"}


def read_text(path):
    try:
        return open(path, encoding="utf8", errors="replace").read()
    except OSError as e:
        raise ToolError(f"cannot read {path}: {e}")


def html_census(path):
    s = scan(read_text(path))
    svg_imgs = [a for a in s.imgs if is_svg(a.get("src", ""))]
    inline = s.svg_art + s.svg_wrappers
    return {"raster": len(s.imgs) - len(svg_imgs), "vector": inline + len(svg_imgs),
            "refs": len(s.imgs) + inline, "alt": alt_split(s.imgs)}


def sha(b):
    return hashlib.sha256(b).hexdigest()[:10]


def source_order(html, srcdir):
    out = []
    for a in scan(read_text(html)).imgs:
        src = a.get("src")
        if not src or is_svg(src): continue
        p = os.path.join(srcdir, src)
        out.append(sha(open(p, "rb").read()) if os.path.exists(p) else "MISSING:" + src)
    return out


def epub_order(path):
    """Raster <img>/<image> bytes in reading order (OPF spine), hashed."""
    z = zip_open(path)
    try:
        opf = next(n for n in z.namelist() if n.endswith(".opf"))
    except StopIteration:
        raise ToolError(f"no .opf package file in {path}")
    o = z.read(opf).decode("utf8", "replace")
    base = posixpath.dirname(opf)
    manifest = {}
    for m in re.finditer(r"<item\b[^>]*>", o):
        t = m.group(0)
        i = re.search(r"""\bid\s*=\s*["']([^"']+)["']""", t); h = re.search(r"""\bhref\s*=\s*["']([^"']+)["']""", t)
        if i and h: manifest[i.group(1)] = h.group(1)
    seq = []
    for idref in re.findall(r"""<itemref\b[^>]*\bidref\s*=\s*["']([^"']+)["']""", o):
        href = manifest.get(idref)
        if not href or not href.lower().endswith((".xhtml", ".html")): continue
        doc = posixpath.normpath(posixpath.join(base, href))
        if doc not in z.namelist(): continue
        for _, ref in scan(z.read(doc).decode("utf8", "replace")).order:
            tgt = posixpath.normpath(posixpath.join(posixpath.dirname(doc), ref))
            if is_svg(tgt): continue
            seq.append(sha(z.read(tgt)) if tgt in z.namelist() else "MISSING:" + ref)
    return seq


def run(a):
    res = {}
    if a.html: res["HTML source"] = html_census(a.html)
    if a.pdf: res["PDF"] = pdf_census(a.pdf)
    if a.epub: res["EPUB"] = epub_census(a.epub)
    if a.docx: res["DOCX"] = docx_census(a.docx)

    print(f"{'format':<12}{'raster':>8}{'vector':>8}{'refs':>6}{'alt d/e/m':>12}  notes")
    for k, v in res.items():
        note = ""
        if k == "PDF":
            note = f"vector not counted; min {v['min_ppi']} ppi; colour {','.join(v['colorspaces'])}"
        n = lambda x: "n/a" if x is None else str(x)
        print(f"{k:<12}{v['raster']:>8}{n(v['vector']):>8}{n(v['refs']):>6}{n(v['alt']):>12}  {note}")

    bad = []
    ref = res.get("PDF", {}).get("raster")
    if ref:
        for k in ("EPUB", "DOCX"):
            if k in res and res[k]["raster"] < a.min_ratio * ref:
                bad.append(f"{k}: {res[k]['raster']} raster vs PDF {ref} (ratio {res[k]['raster']/ref:.2f} < {a.min_ratio})")
    for k in ("EPUB", "DOCX"):
        if k in res and res[k]["alt"] and int(res[k]["alt"].split("/")[2]) > 0:
            extra = " (epubcheck rejects this in EPUB)" if k == "EPUB" else ""
            print(f"note: {k} has {res[k]['alt'].split('/')[2]} images with NO alt attribute{extra}")

    if a.html and a.epub and a.src_dir:
        so, eo = source_order(a.html, a.src_dir), epub_order(a.epub)
        print(f"\norder check (raster <img>, byte-identical match by SHA-256): source {len(so)} vs EPUB {len(eo)}")
        if so == eo:
            print("  same images, same order.")
        else:
            miss = [x for x in so if x not in eo]
            pos = next((i for i, (x, y) in enumerate(zip(so, eo)) if x != y), min(len(so), len(eo))) + 1
            print(f"  DIFFERS: {len(miss)} source image(s) absent from EPUB; first mismatch at position {pos}")
            bad.append("order/content mismatch between source HTML and EPUB")
    if bad:
        print("\nFAIL:")
        for b in bad: print("  " + b)
        return 1
    print("\nOK - no format below the ratio tripwire (counts only; this does not prove order or placement).")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    for k in ("pdf", "epub", "docx", "html"):
        ap.add_argument(f"--{k}")
    ap.add_argument("--min-ratio", type=float, default=0.5)
    ap.add_argument("--src-dir", help="folder the --html <img src> paths are relative to; enables the order check")
    a = ap.parse_args(argv)
    if not (a.pdf or a.epub or a.docx or a.html):
        ap.print_usage(); return 2
    try:
        return run(a)
    except ToolError as e:
        print(f"error: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
