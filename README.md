# Book Format & Interior-Image Integrity

A folder-based skill that takes a finished book and its delivery files and checks that every format carries the same images, in the same order, with the alt text the author approved. It also converts to formats beyond the usual six-file set, and it never touches the prose.

## What it produces

A real run on a real book: the final set for *Are You Actually Hungry?* (files dated 2026-06-15), checked 2026-09-26. The EPUB passes the EPUB validator. The census finds it is missing the pictures.

```
$ epubcheck are-you-actually-hungry.epub
Validating using EPUB version 3.4 rules.
No errors or warnings detected.
Messages: 0 fatals / 0 errors / 0 warnings / 0 infos

$ python3 tools/format-census.py --html book.html --src-dir book-build \
    --pdf are-you-actually-hungry.pdf --epub are-you-actually-hungry.epub --docx are-you-actually-hungry.docx
format        raster  vector  refs   alt d/e/m  notes
HTML source       14      75    89      1/13/0
PDF               22     n/a   n/a         n/a  vector not counted; min 267 ppi; colour gray,rgb
EPUB               1       0     1       0/0/0
DOCX               0       0     0       0/0/0

order check (raster <img>, byte-identical match by SHA-256): source 14 vs EPUB 1
  DIFFERS: 13 source image(s) absent from EPUB; first mismatch at position 2

FAIL:
  EPUB: 1 raster vs PDF 22 (ratio 0.05 < 0.5)
  DOCX: 0 raster vs PDF 22 (ratio 0.00 < 0.5)
  order/content mismatch between source HTML and EPUB
```

The same source, converted again with five source-side fixes (listed in `reference/job-2-format-conversion.md`; the conversion script stays with the book's files and is not in this repo) into a scratch folder. The shipped files were not touched. Here the "HTML source" row is the prepped HTML (the four part-opener photos turned into `<img>`, the 16 figures given their own `alt`), so its counts are higher than in the first block. File paths are shortened in both blocks.

```
$ epubcheck ayah-rebuilt-fixed.epub
No errors or warnings detected.
Messages: 0 fatals / 0 errors / 0 warnings / 0 infos

format        raster  vector  refs   alt d/e/m  notes
HTML source       18      75    93     17/17/0
PDF               22     n/a   n/a         n/a  vector not counted; min 267 ppi; colour gray,rgb
EPUB              18      20    93     17/76/0
DOCX              34      20    93     17/76/0

order check (raster <img>, byte-identical match by SHA-256): source 18 vs EPUB 18
  same images, same order.
```

| | Final-set EPUB (dated 2026-06-15) | Rebuilt EPUB |
| --- | --- | --- |
| `epubcheck` | 0 errors | 0 errors |
| Raster images | 1 (the cover) | 18, same order as the source |
| Figures with alt text | 0 | 16 (the author's own labels, carried across) |
| Size | 2.9 MB | 7.2 MB (interior images capped at 1200×1800) |

The rebuilt EPUB proves the images can survive, but it is **not** a drop-in replacement: it was converted from the print HTML, whose text differs from the shipped EPUB's (4,982 words only in the rebuild, 241 only in the shipped file). For a live book the fix is an insert-only edit of the shipped file, which changed 0 words (incident I-14 in `reference/incident-ledger.md`).

Not checked: how either EPUB reads on a device, whether the DOCX opens correctly in Word, and whether the print design (a title card over a full-bleed photo) survives; in an ebook it becomes a photo above the title. The book is the operator's own.

A second real book, *BikYasa Yoga*, shows the opposite failure: its EPUB has 124 images against 121 in its PDF (and 108 in its DOCX; whether they are the same images was not tested) and fails `epubcheck` with 157 errors, 124 of them images missing the required `alt`. A validator and a count answer different questions; neither alone would have caught both books.

## What this is

Three separate jobs on a finished, revision-passed manuscript:

1. **Interior images.** Inventory every image, decide informative or decorative, check pixels against print and reflowable ebook, prep, and record what happens to a full-bleed or floated image when the layout changes.
2. **Conversion.** Which formats beyond the six-file set a book needs, and how to make each from the one master. The AYAH run found the final-set EPUB carrying 1 image and the DOCX none, and the stripped Markdown master they most likely came from has zero image references (that they were built from it is inferred, not recorded).
3. **Cross-format verification.** Run the census and each format's real validator, side by side, and say what agrees.

Every rule in the Always list carries a tag: **INCIDENT** (a dated event on the real shelf), **VENDOR** (a fetched, dated vendor page) or **SPECULATIVE** (no incident, no cite). Vendor numbers are in `reference/vendor-requirements.md` with the fetch date (most pages show no revision date of their own). The Kobo pages could not be opened (HTTP 403), so Kobo is marked NOT OPENED.

## Setup

1. Point a Claude Code session at this folder, or load it into a Claude Project. `SKILL.md` lets Claude Code trigger it from a request like "do the formats match?" or "why is my EPUB missing the pictures?". It reads `identity.md`, then `rules.md`, then the one `reference/` file the job needs.
2. For the tool: `python3` (standard library only), `pdfimages` from poppler for the PDF column, and `brew install epubcheck` for EPUB validity. Exit code 1 is a genuine FAIL; 3 means the tool could not run (a missing tool or unreadable file), never a verdict on the book. Tests: `python3 tools/test_format_census.py`.
3. Working from the raw files: `identity.md` → `rules.md` → `examples.md`, then the one `reference/` file for the active job.

## First-run prompts

- *"epubcheck passed. Do the PDF and the EPUB have the same images?"*
- *"Check the images in this book for print and for ebook."*
- *"Make an EPUB from this HTML that keeps the figures and their alt text."*
- *"Which formats does this book need beyond the six files?"*

## What it does and doesn't do

It doesn't edit prose, invent alt text or captions, rebuild the six-file package, design covers, write title or jacket copy, or produce audio, video or fixed-layout children's books. Where a check can only be done in a vendor's own upload tool, it says so and gives the operator the step.

## Where this fits

It starts where [Publishing Preparation](https://github.com/NFTYoginis/publishing-preparation-skill) stops. That skill lays out the manuscript and builds the six-file package. This one takes that package and its source as input and checks the images and formats inside it. A defect in the six-file EPUB or DOCX is reported here and fixed there.

## License

MIT. See `LICENSE`.

---

Built by Gabe at The Quiet Ai. The Quiet Scribe Suite (early access) carries your context from one AI tool to the next: [thequietscribe.com](https://thequietscribe.com)
