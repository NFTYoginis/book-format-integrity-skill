# Examples

One worked illustration of the core discipline: a format that validates and still lost the book's images. The mechanics of each job are in `reference/`; this shows the discipline, it does not re-teach them.

---

## The EPUB that passed and had no pictures

**Situation.** *Are You Actually Hungry?* shipped 2026-06-15 as the six-file set. The packaging README calls the EPUB *"Amazon KDP ebook format. Upload this to KDP directly."* Someone asks: "epubcheck is clean, can we call the formats consistent?"

**Response: the refusal gate from `rules.md`, verbatim, then the census.**

*"I won't call these formats consistent. A validator pass says the file is well-formed, not that it kept the images. The shipped Are You Actually Hungry? EPUB passed epubcheck with zero errors and carried 1 of the 22 images its PDF has. Run the census against the PDF and the source, and I'll report what agrees."*

```
$ epubcheck are-you-actually-hungry.epub
Messages: 0 fatals / 0 errors / 0 warnings / 0 infos

$ python3 tools/format-census.py --html book.html --src-dir book-build \
    --pdf are-you-actually-hungry.pdf --epub are-you-actually-hungry.epub --docx are-you-actually-hungry.docx
format        raster  vector  refs   alt d/e/m  notes
HTML source       14      75    89      1/13/0
PDF               22     n/a   n/a         n/a  vector not counted; min 267 ppi
EPUB               1       0     1       0/0/0
DOCX               0       0     0       0/0/0

order check: source 14 vs EPUB 1
  DIFFERS: 13 source image(s) absent from EPUB; first mismatch at position 2
FAIL:  EPUB 1 raster vs PDF 22 (ratio 0.05 < 0.5)   DOCX 0 raster vs PDF 22 (ratio 0.00 < 0.5)
```

**What the census could and could not say.** The one image the EPUB carries is the cover, and it is byte-identical to the source. The other 13 interior photos are gone, and the DOCX carries none at all. (Output above is abridged: the `--src-dir` path and the closing OK/FAIL lines are trimmed.) The validator could not see it because a missing image is not an error. The census could, because it counted the same thing in every format.

**Cause, stated at the strength it was proven.** The MD master has zero image references (measured), so an EPUB or DOCX built from it cannot contain figures. That the files were made by pandoc is *inferred* from the `file0.png` naming and the package layout; it is not recorded anywhere.

**Fix path, not done on the shelf.** Regenerating from the print HTML fixed the images (18 of 18 in source order, `epubcheck` 0 errors) but produced a different edition of the text: 4,982 words present only in the rebuild, 241 only in the original (`INCIDENT I-14`). For a file that is already live the safe fix is an insert-only edit of the shipped EPUB: on 2026-09-26, into a scratch folder, 13 chapter photos and 16 figures were inserted, 0 words of the shipped text changed, `epubcheck` 0 errors. The shipped file was not touched. The defect belongs to publishing-preparation's packaging step, so it is reported there, not patched here.
