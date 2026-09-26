# Job 1: interior images

Every step is tagged INCIDENT (`I-n`, see `incident-ledger.md`), VENDOR (`V-n`, see `vendor-requirements.md`) or SPECULATIVE.

## 1. Inventory from three places, not one

An image can reach a book through the markup, the stylesheet, or a generator. Count all three, then compare to the rendered PDF.

```bash
pdfimages -list book.pdf | awk 'NR>2' | wc -l          # rasters actually embedded (vector art is not counted)
grep -o -E '<img[^>]*>' source.html | wc -l             # <img> in the markup
grep -o -E "url\(['\"]?[^)'\"#]+" print.css | sort -u   # images that arrive through CSS
python3 tools/format-census.py --html source.html --pdf book.pdf
```

`INCIDENT I-3`: on the *Are You Actually Hungry?* build the PDF had 22 rasters and the HTML had 14 `<img>`. Four of the difference were the part-opener photos, set as CSS backgrounds in `print.css` and absent from any converter's output. The other four are small grayscale rasters on the same four pages, not traced and not opened. Do not assume the count difference is explained; say how much of it is.

## 2. Decide each image: informative or decorative

- **Informative** (a figure, a diagram, a photo the text refers to): needs author-approved alt text. You do not write it. You list the file, page and caption and ask.
- **Decorative** (a mood photo, an ornament): explicit `alt=""`. That is a decision, recorded as one.
- A missing `alt` attribute is neither. `epubcheck` 5.4.0 reports it as `RSC-005 element "img" missing required attribute "alt"`, once per image. `INCIDENT I-2`: the *BikYasa Yoga* shelf EPUB has 124 of them.
- `INCIDENT I-7`: alt text is a claim about an image and goes stale when the image changes. On 2026-06-10 the site still described a green-smoothie cover after the cover had been replaced. Re-read alt text whenever an image is swapped.
- `INCIDENT I-13`: an accessible name can exist in the source and be lost in conversion. The AYAH source has 16 figure SVGs, each with an author-written `role="img" aria-label`. pandoc extracted them and wrote `alt=""` in the EPUB and `descr=""` in the DOCX, so a source that was accessible produced outputs that were not, with no validator message. Carry the label across (Job 2, fix 5). The 14 `<img>` in the same source: 1 has descriptive alt, 13 have `alt=""`; whether the 13 photo openers are decorative is the author's call, not this skill's.

## 3. Pixels against the format

Numbers here come from `vendor-requirements.md` (fetched 2026-09-26; re-check the V-entry before quoting one for a title going to a retailer).

| Going to | Check | Tag |
| --- | --- | --- |
| Print interior | effective ppi ≥ 300 (`pdfimages -list`, x-ppi/y-ppi). Report each shortfall with its page. | VENDOR V-1 |
| Full-bleed in print | the page must be 0.25 in higher and 0.125 in wider than trim (KDP: 6.125×9.25 in for a 6×9 trim, 441×666 pt) and the image must cover it, so ≥ 1838×2775 px for 300 ppi. Report the PDF's measured page size against that. Do not use BleedBox-vs-TrimBox: an unset box reads equal to the MediaBox. | VENDOR V-1 · INCIDENT I-10 |
| Reflowable EPUB, Apple | ≤ 5.6 million pixels per interior image; JPEG or PNG; sRGB. Compute width×height×3 bytes against "about 10 MB of un-encoded image data per XHTML file". | VENDOR V-3 |
| Reflowable EPUB, Apple: text in images | no text inside images ("books with images that contain embedded text are rejected from sale on Apple Books"). Labelled SVG figures like the AYAH ones are at risk; flag, do not decide. | VENDOR V-3 |
| Reflowable EPUB, Kindle | sRGB, no CMYK; no TIFF, multi-frame GIF or transparency; pictorial images ≥ 60% of screen width, text-bearing images ≥ 80%. | VENDOR V-2 |
| A small source | an image cannot be enlarged past its source. The 620×620 author photo caps at about 2 in at 300 ppi. Say the cap; do not upsample. | INCIDENT I-8 |

Measured on the AYAH files (2026-09-26): the 13 chapter openers are 1800×2700 (300 ppi at 6×9), the four part openers are 1601×2400 (267 ppi, below 300), the cover is 1804×2705. Every raster in the PDF is RGB or gray. One 1800×2700 RGB image is 14.6 MB un-encoded, over Apple's ~10 MB per-XHTML guidance; capped at 1200×1800 it is 6.5 MB.

## 4. Prep for a reflowable ebook

- Cap interior images by the vendor's figures and what the layout needs. In the AYAH run: interior images to 1200×1800, quality 82, cover kept at 1804×2705. EPUB 10.2 MB → 7.2 MB, same 18 raster images in the same order, `epubcheck` 0 errors. The 1200-px cap and the JPEG quality are engineering choices checked against the vendor numbers above, not vendor requirements; V-2 also says "Provide inline images in lossless format where possible", and a quality-82 JPEG is lossy.
- Keep the source and the resized copy in separate folders and record which was used. `INCIDENT I-12`: a live image was found on audit to match no source file and no candidate record.
- Keep the render script for any figure generated with positioned labels. `INCIDENT I-9`: truncated labels on three shipped figures could only be fixed by painting over the PNG because the script that made them was never saved.

## 5. What happens to a full-bleed or floated image when the layout changes

| In the print layout | In a reflowable ebook | Do |
| --- | --- | --- |
| `background: url(part-01.jpg)` on a full-bleed page (`INCIDENT I-3`) | gone unless it is an `<img>` | Make it an `<img>` in the prep step, give it an explicit alt decision. |
| `object-fit: cover` crop to the page shape | shown whole | Pre-crop to the aspect you want or accept the whole image. |
| Full-bleed page with a card over it (page 7 of AYAH) | the image becomes an in-flow block above the title | State the placement change. The design intent (title over photo) is not reproduced. |
| Inline SVG figure | pandoc extracts each to a `.svg` file. Without an `xmlns` the file is invalid (`INCIDENT I-4`), and its `aria-label` becomes `alt=""` (`I-13`). | Add `xmlns` and move the label into an `<img alt>` before converting. |
| Floated or side-by-side layout | reflows to a single column | Check each in a reader; the census cannot see placement. |

## 6. Captions and figure numbers

- Captions survived conversion in the AYAH run: 16 `<figcaption>` in the source, 16 in the EPUB (measured 2026-09-26). Verify per book; do not assume.
- **SPECULATIVE:** figure numbering. The AYAH figures are named ("The Noise Map"), not numbered, and no shelf book numbers its figures. Any numbering rule (sequential, by chapter, cross-referenced) is a hypothesis until a numbered book is on the shelf. Do not add numbers the author did not choose.
- **SPECULATIVE:** converting print interiors to CMYK. The design worker's own cover README lists it as a to-do, and KDP's paperback page (V-1) does not state a colour mode for interiors. No incident, no cite. Ask the printer.
