# Job 3: cross-format verification

The claim to prove: the same images, in the same order, with the same alt text, nothing dropped, nothing moved to the wrong place, each output passed by its own real checker. Tags as in Job 1.

## Two kinds of check, never merged

| Kind | What it says | What it cannot say |
| --- | --- | --- |
| **Validity** (`epubcheck`, `pdffonts`, `pdfinfo`) | the file is well-formed / fonts embedded / the page size is X | that anything is present. `INCIDENT I-1`: an EPUB with 1 raster image, where its PDF has 22, passed with zero messages. |
| **Census** (`tools/format-census.py`) | how many images each format carries, in what order (EPUB vs source), how many have alt | how they look, or that placement is right |

Report both, side by side, every time.

## Run order

```bash
epubcheck book.epub                                       # validity, EPUB
pdffonts book.pdf | awk 'NR>2 && $(NF-4)!="yes"'          # any font not embedded (print PDF)
pdfinfo -f 7 -l 7 book.pdf | grep 'Page size'              # page size on a full-bleed page, vs trim + bleed
python3 tools/format-census.py --html source.html --src-dir <dir> \
  --pdf book.pdf --epub book.epub --docx book.docx         # counts + EPUB order; exit 1 = genuine FAIL, 3 = tool/file error
```

Then open at least one page of each format that has a full-bleed or floated image, and look. The census is a tripwire, not a proof.

## What the census does, exactly

- **PDF:** raster images via `pdfimages -list`, with effective ppi (the lower of x and y) and colour space. Vector artwork is not counted, so this is a floor. The PDF's image order is **not** tested: `pdfimages` re-encodes, so bytes cannot be matched back to the source.
- **EPUB:** raster files, SVG files, image references in content documents, alt split as described / deliberately empty / missing. With `--html --src-dir` it hashes each raster image in reading order (OPF spine) and compares with the source's `<img>` order. Byte-identical match only.
- **DOCX:** files in `word/media`, drawings, and whether each carries a description.
- **The threshold:** an EPUB or DOCX below 50% of the PDF's raster count fails. That number is a tuning choice (`--min-ratio`), not a retail standard. On six shelf books it separated 5% (AYAH EPUB) and 0% (AYAH DOCX) from 89% to 104% for every other EPUB and DOCX. That is six books, so treat 0.5 as a starting value.
- **Exit codes:** 0 = no format below the ratio; 1 = a genuine FAIL; 2 = usage error; 3 = the tool could not run (missing `pdfimages`, missing or unreadable file). A 3 is never a verdict on the book. `tools/test_format_census.py` holds the negative-case tests (single-quoted attributes, `>` inside an alt, missing tool, genuine FAIL, reordered images, unreadable file, y-ppi, SVG wrappers, DOCX alt).
- **Known blind spots:** a resized image will not byte-match its source (run the check against the HTML and folder the resized images were made from); CSS-background images are only visible to the PDF column; `pdfimages` lists small grayscale helper images as rasters (4 on the AYAH PDF, untraced), so the PDF count can exceed the true figure count by a few.

## Reading the result

| Census says | Meaning | Do |
| --- | --- | --- |
| EPUB/DOCX ≪ PDF | images lost in conversion (`I-1`) | find where they were dropped: MD master with no refs, CSS backgrounds (`I-3`), unsupported inline SVG (`I-4`). |
| Counts match, order DIFFERS | reordered or substituted images | diff the two sequences; a converter can re-sort. |
| Alt `m` (missing) > 0 in EPUB | `epubcheck` will fail these (`I-2`) | list the images for the author; decorative gets `alt=""`. |
| Alt `e` (empty) high | may be correct (decorative) or a gap | ask the author which. On the AYAH insert-only file: 16 figures described, 13 opener photos empty. |
| PDF min ppi < 300 | print shortfall (`V-1`, `I-8`) | report page and effective ppi. AYAH: 267 on the part openers (1601 px across 6 in). BikYasa: 78 on a 152×34 px raster (a small graphic; content not opened). |
| Page size = trim size on a full-bleed page | no bleed area in the file (`V-1`, `I-10`); KDP's page asks for 0.25 in higher and 0.125 in wider than trim | report; publishing-preparation owns the fix. AYAH page 7: 432×648 pt, exactly 6×9 in. Do **not** infer this from BleedBox = TrimBox: unset boxes read equal to the MediaBox. |

## The real runs on the shelf (2026-09-26)

| Book | Formats | Census | `epubcheck` |
| --- | --- | --- | --- |
| *Are You Actually Hungry?* final set (dated 2026-06-15) | PDF / EPUB / DOCX | **FAIL**: EPUB 1 vs PDF 22, DOCX 0 vs 22, 13 of 14 source images absent from EPUB | 0 errors |
| *BikYasa Yoga* (shelf copies, Jul 14) | PDF / EPUB / DOCX | no format below the 0.5 tripwire: 121 / 124 / 108 raster. The counts differ (DOCX is 13 fewer than the PDF) and whether they are the same images was not tested; there is no source HTML for an order check. Alt missing on 124 EPUB and 122 DOCX images | **157 errors** (124 missing `alt`, 32 invalid language codes, 1 unresolved link) |
| AYAH converted from the print HTML (not a replacement, `I-14`) | EPUB / DOCX | pass, same images in the same order (18 of 18) | 0 errors |
| AYAH final-set EPUB with images inserted | EPUB | 14 raster + 16 SVG figures; 0 words of the shipped text changed, 331 inserted words = the 16 captions | 0 errors |

Read the first two rows together. One file is valid and short of its pictures; the other carries a similar number of images and is invalid. Neither check alone would have caught both.

Whether the BikYasa EPUB on the shelf is the file that went to Amazon is not recorded (an independent checker opened the live Kindle listing; the file uploaded is unknown). Say "the shelf copy", not "the published file".
