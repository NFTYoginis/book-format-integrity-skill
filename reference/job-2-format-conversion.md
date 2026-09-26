# Job 2: conversion to formats beyond the six-file set

Tags as in Job 1. This is the least evidenced of the three jobs: the shelf's packaging targets KDP (`output-packaging.md`: "Uploads to KDP directly") and no other retailer target is recorded, so most of the "other formats" list is SPECULATIVE. It says so line by line.

## Start from the right master

`INCIDENT I-1`: the six-file convention's Markdown master is "build notes stripped" and has **zero image references** (measured on *Are You Actually Hungry?*, 2026-09-26). An EPUB or DOCX made from it cannot contain a figure. The final-set AYAH EPUB carries 1 image (the cover) and the DOCX carries none.

**Where the book is not live yet, convert image-bearing books from the HTML, not the stripped MD.** For a text-only book the MD master is fine; run the census and say it found no images. **Where a file is already live, do not regenerate it** (`INCIDENT I-14`): the print HTML is a different edition of the text. Insert the images into the shipped file (new `<img>` and `<figure>` blocks, the manifest entries, and a small CSS block, changing nothing else), then prove with a flattened-text diff that no word changed and that every modified file reduces to its shipped bytes once the inserted blocks are removed. On AYAH that insert-only edit changed 0 words; the only inserted text was the 16 figure captions.

The cause is proven for the master (zero references). That the final-set files were built from it, and by pandoc, is inferred from `file0.png` and the package layout; nothing on the shelf records the command.

## The real conversion that was run (2026-09-26)

A scratch conversion of `Detox Book/book-build/book.html` (read-only on the shelf, output kept out of the shelf):

```bash
pandoc prepped.html -f html -t epub3 --resource-path=. -o ayah-rebuilt-fixed.epub \
  --metadata title="Are You Actually Hungry?" --metadata author="Gabe Yoga" --metadata lang=en
```

Five source-side fixes, each with what it removes:

| # | Fix in the prep step | Without it | Tag |
| - | --- | --- | --- |
| 1 | `<svg>` without `xmlns` gets `xmlns="http://www.w3.org/2000/svg"` | 4 extracted `.svg` files fail `epubcheck` (`RSC-005`, 4 errors) | INCIDENT I-4 |
| 2 | Drop a wrapper id that collides with the id pandoc derives from the heading | `Duplicate ID "preface"` (`RSC-005`, 2 errors) | INCIDENT I-5 |
| 3 | Turn the 4 CSS-background part-opener photos into `<img alt="">` | 4 images in the PDF, absent from the EPUB | INCIDENT I-3 |
| 4 | Resample interior images to 1200×1800, keep the cover full size | 10.2 MB; each opener 14.6 MB un-encoded vs Apple's ~10 MB per-XHTML guidance | VENDOR V-3 |
| 5 | Extract each of the 16 labelled figure SVGs to a file and carry its own `aria-label` across as `alt` | 16 informative figures with `alt=""` in the EPUB and `descr=""` in the DOCX, no validator message | INCIDENT I-13 |

Results: `epubcheck` "No errors or warnings detected" (0/0/0/0); census EPUB 18 raster / 20 SVG files / 93 image references, alt described 17 (1 photo + 16 figures), "same images, same order" (SHA-256, source 18 vs EPUB 18). The same source to DOCX: 34 raster files (the 18 plus, inferred from `rsvg-convert` being installed, PNG renditions of the 16 figures) + 20 SVG, 93 image references, 17 with a description. The other 76 references carry an empty alt: 17 are the photo openers and part openers (`alt=""` in the source), and 59 are small sigil SVGs that the source marks `aria-hidden="true"` (measured), so an empty alt is the right output for them. Whether the 17 photo openers are decorative is the author's call.

What was **not** checked: how the EPUB reads on a device or in a reader app (no reader ran); whether the DOCX opens correctly in Word; whether the print design intent survives (title-over-photo becomes photo-above-title). The pandoc route drops the print stylesheet, so component styling (boxes, pull quotes) is not carried. That is a reading-quality question, separate from image integrity.

## Which formats does a book need?

| Format | Need | Basis |
| --- | --- | --- |
| Print PDF for KDP / IngramSpark | already the six-file PDF | publishing-preparation |
| EPUB (Kindle via KDP, Apple Books) | when the book sells as an ebook. KDP accepts EPUB, DOCX or `.kpf` (per publishing-preparation's packaging note); V-2 and V-3 give only the *image* rules for an EPUB, not the requirement to have one. | publishing-preparation `output-packaging.md`; image rules VENDOR V-2, V-3 |
| DOCX | the six-file convention includes it for Kindle Create | publishing-preparation `output-packaging.md` |
| `.kpf` | made only in Amazon's Kindle Create app; cannot be scripted | publishing-preparation `output-packaging.md` (its dated note) |
| Kobo EPUB | **not verified**: the vendor pages returned 403. Search-result snippets mention 300 DPI and size caps; treat as a lead, not a rule. Operator step: open the Kobo Writing Life "File Types & Sizes" article in a browser and paste the limits. | SPECULATIVE V-4 |
| A second print vendor's PDF | no book on the shelf has shipped to one. IngramSpark numbers are carried from publishing-preparation's 2026-09-22 snapshot, not re-fetched here. | SPECULATIVE V-5 |
| Large print | no book on the shelf has one and no vendor page was opened. Enlarging type reflows the whole layout, so every image's placement is a new question and the census applies again. | SPECULATIVE |
| Audio, video, fixed-layout children's book | out of scope | none |

## Producing each from the one master

1. **Book not live yet:** fix the source once (the five fixes above) and regenerate every format from it; never patch one output by hand, because the next regeneration erases the patch. **Book already live:** do not regenerate (`INCIDENT I-14`); insert-only edit of the shipped file, then prove nothing else moved.
2. Run `epubcheck` on every EPUB, and the census across all outputs (Job 3).
2a. **Apple Books:** an image with embedded text is a rejection risk (`VENDOR V-3`). The AYAH figures are 16 labelled SVGs, so the converted and insert-only EPUBs would be exposed there; whether this book is offered on Apple Books is not recorded here, and anyone using this skill for an Apple-bound book should look first.
3. A format whose only check is a vendor's upload previewer: say so, give the operator the step, and do not simulate it.
