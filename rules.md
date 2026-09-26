# Rules

Every rule in the **Always** list carries a tag; the Never list, the refusal gate, the boundary and the empty-input rules are prohibitions and procedures, not evidence claims, and carry none. The tags: **INCIDENT** (a dated event on the real shelf earned it; ID in `reference/incident-ledger.md`), **VENDOR** (a dated vendor page states it; cite in `reference/vendor-requirements.md`), or **SPECULATIVE** (no incident and no cited page behind it; treat as a hypothesis).

## Always

- **Run the census before saying two formats agree.** `python3 tools/format-census.py` on the PDF, EPUB, DOCX and the source HTML. Say which tool ran and what it printed. `INCIDENT I-1`
- **Run the format's real validator, and never treat its pass as proof the images survived.** `epubcheck` for EPUB. A well-formed EPUB with no images is a valid EPUB. `INCIDENT I-1`
- **Inventory the source's images from the rendered result as well as the markup.** In the AYAH run, pandoc did not carry images set as CSS `background: url(...)`: they showed in the PDF and were absent from its EPUB until made `<img>` (an independent check reproduced this on pandoc 3.9.0.2). Other converters were not tested, and EPUB 3 itself can carry CSS backgrounds, so check per converter; do not assume. `INCIDENT I-3`
- **Make every image a decision: informative gets author-approved alt text, decorative gets an explicit empty `alt=""`.** A missing attribute is a validator error (`epubcheck` `RSC-005`, `INCIDENT I-2`); an empty one is a statement, and KDP's page says to set `alt=""` or `role="presentation"` for decorative images (`VENDOR V-2`). Re-read alt text whenever an image is swapped (`INCIDENT I-7`).
- **Cap interior images for reflowable ebooks against the vendor's own figures.** Compute un-encoded size (width × height × 3 bytes, my reading of Apple's term) against Apple's "about 10 MB … per XHTML file" before choosing a cap. `VENDOR V-3`. Keeping the cover at full size and the JPEG re-encode are engineering choices, not vendor requirements (V-2 sets a ≥1200 px floor for covers and says "lossless format where possible").
- **State the effective resolution of every raster in the print PDF against 300 DPI.** `pdfimages -list` gives x-ppi and y-ppi. Shortfalls are reported, not silently accepted. `VENDOR V-1` · `INCIDENT I-8`
- **Check bleed on the rendered file, not the CSS, by page size.** KDP's page says to format the PDF "0.25" higher and 0.125" wider than your selected trim size" (`VENDOR V-1`), so a 6×9 in trim needs a 6.125×9.25 in page (441×666 pt). Read the page size with `pdfinfo` and compare it with trim plus bleed. **Do not test BleedBox against TrimBox**: a PDF with no boxes set reports them all equal to the MediaBox, so that comparison cannot tell a bleed page from a trim page (an independent check reproduced it on a correct 441×666 pt page). AYAH page 7 measured 432×648 pt, exactly the 6×9 in trim, so it has no bleed area. The rule and dated trim numbers live in publishing-preparation. `INCIDENT I-10`
- **For an Apple-Books-bound book, images must contain no text.** Apple's page rejects from sale "books with images that contain embedded text" (`VENDOR V-3`). Labelled SVG figures such as the AYAH ones are at risk; flag them, do not decide it. This is the first thing the Apple page says, so read it before calling any EPUB Apple-ready.
- **Date and cite every vendor number.** Fetch the vendor page, quote it, date it, and expect an independent check. Where the page cannot be opened, say "not opened" and give the operator the step. `VENDOR`
- **Before any file is offered as a replacement for a live one, prove prose parity with a flattened-text diff, and prefer an insert-only edit of the shipped file over regenerating it.** Report words deleted, changed and inserted; a regenerated file passing `epubcheck` and holding every image can still be a different edition. `INCIDENT I-14`
- **Write conversion scripts down and keep them beside the output.** A converted file with no script cannot be re-made after the source changes. `INCIDENT I-9`
- **Hand defects that belong to the base pipeline back to it.** Name the file, the count, and the cause you can prove versus the cause you infer. `INCIDENT I-1`

## Never

- **No prose edits, no invented alt text, no invented captions.** Find the gap, list the images, ask the author.
- **No rebuilding the six-file set or either of its pipelines.** Take the output as input.
- **No simulated vendor checks.** If only the vendor's upload tool can say it, say that and stop.
- **No "checked" without a tool run.** A file you did not run a tool on is "not opened".
- **No rule stated as fact without a tag.** Untagged means SPECULATIVE until an incident or a cite arrives.
- **No image-count agreement declared from counts alone.** Counts are a tripwire. Order and placement need the order check (EPUB) or a rendered-page look (PDF). `reference/job-3-cross-format-verification.md`
- **No consistency verdict on the "formats agree" refusal gate below without the census output attached.**

## The refusal gate

Asked to call the formats consistent, or ship an EPUB or DOCX, on the strength of a validator pass, a matching page count, or "the PDF looks right":

> *"I won't call these formats consistent. A validator pass says the file is well-formed, not that it kept the images. The shipped Are You Actually Hungry? EPUB passed epubcheck with zero errors and carried 1 of the 22 images its PDF has. Run the census against the PDF and the source, and I'll report what agrees."*

Use it verbatim. Then run the census. If the census passes, say so and state what it does not prove (order in the PDF, placement, how it reads on a device).

## Routing (three jobs, three files)

The routing table lives in `SKILL.md` (kept in one place). In short: images, alt text and pixels are Job 1; making another format is Job 2; "do the formats match?" is Job 3.

## Boundary with publishing-preparation, stated both directions

- **Publishing-preparation owns:** layout, the two render pipelines, page geometry (trim, margins, bleed size, running heads), and the six-file package. The bleed rule and the KDP/IngramSpark trim numbers are its.
- **This skill owns:** the pixels and alt text inside the book, formats beyond the six-file set, and the proof that every format carries the same book.
- **Where they touch:** the full-bleed image. Publishing-preparation says the page must extend 0.125 in past trim. This skill says whether the source image has enough pixels to do that at 300 DPI, and reports what the finished PDF's page boxes measure.
- **A defect in the six-file EPUB or DOCX** (for example an EPUB made from the stripped Markdown master has no figures) is reported here and fixed there.

## Empty-input handling

- **No revision-passed manuscript.** Refuse. Route to `book-ghostwriting-skill`.
- **No finished PDF/EPUB/DOCX yet.** Job 1 and 2 can run on the source. Job 3 needs at least two formats; with one, report its census and say there is nothing to compare.
- **No source HTML, only the delivered files.** Compare the delivered files to each other (census without `--html`). Say the order check was not run and why.
- **No validator installed.** Say which, give the install command, and do not substitute another tool's verdict. `epubcheck` installs with `brew install epubcheck`.
- **A book with no images.** Say so from a census, not from an assumption. Jobs 1 and 3 close in one line.

## Domain grounding

Read directly from real shelf incidents, measured on 2026-09-26 (*Are You Actually Hungry?* shipped set and its `book-build/`; *BikYasa Yoga* shipped set) and from vendor pages fetched the same day. Full list: `reference/incident-ledger.md`. This skill names what happened; it does not invent a process from theory.
