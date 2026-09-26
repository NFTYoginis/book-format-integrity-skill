---
name: book-format-integrity
description: Handle the images inside a finished book, convert it to formats beyond the six-file set, and prove every format carries the same book. Use when the user wants to (1) check or prep the images in a book, e.g. "check my images", "are these high enough resolution", "add alt text to my figures", "what happens to my full-bleed photo in the EPUB"; (2) convert a finished book to another format or retailer, e.g. "make an EPUB", "make a Word version", "convert for Kobo/Apple Books", "do I need a large-print edition"; (3) verify formats agree, e.g. "do the formats match", "why is my EPUB missing the pictures", "epubcheck passed but the images are gone", "compare the PDF and the EPUB". Also trigger on "validate my EPUB", "cross-format check", "figure numbering", "image resolution for print". Takes the output of publishing-preparation as input; never touches the prose.
---

# Book Format & Interior-Image Integrity

A verifier and converter for the images inside a finished book and the formats they travel in. It never touches the prose, and it does not rebuild the six-file package that [publishing-preparation-skill](https://github.com/NFTYoginis/publishing-preparation-skill) makes.

**Read first, every session:** [identity.md](identity.md) → [rules.md](rules.md). Both are short. `rules.md` holds the refusal gate and the exact boundary with publishing-preparation; the routing table is the one below.

## Then open only the job the request needs

| Request | Open |
| --- | --- |
| Image resolution, colour, alt text, captions, figure numbers, full-bleed or floated images | `reference/job-1-interior-images.md` |
| Producing an EPUB/DOCX/large-print/retailer variant from the one master | `reference/job-2-format-conversion.md` |
| "Do the formats match?", validator reports, pre-ship checks | `reference/job-3-cross-format-verification.md` |
| Any retailer or print-vendor number | `reference/vendor-requirements.md` (dated, cited) |
| Why a rule exists | `reference/incident-ledger.md` |

`examples.md` is one worked illustration: an EPUB that passed `epubcheck` with zero errors and carried 1 image, where its PDF has 22.

## The tool

`python3 tools/format-census.py --pdf book.pdf --epub book.epub --docx book.docx [--html source.html --src-dir <dir>]` counts what each format carries and compares image bytes in reading order. It exits 1 on a genuine FAIL (a format missing most of the PDF's images, or the order differs) and 3 when the tool itself could not run (missing `pdfimages`, unreadable file), never on the book. Tests: `python3 tools/test_format_census.py`. It needs `pdfimages` (poppler). For EPUB validity install `epubcheck` (`brew install epubcheck`).

## Out of scope

Prose, cover design, title/jacket copy, audio/video, fixed-layout children's books, vendor accounts and uploads.
