# Vendor requirements (image and format numbers)

**Every entry below is a claim about the world.** Fetched 2026-09-26 by WebFetch on the URLs shown; quoted from the page text returned. Individual KDP and Apple pages show no revision date, so "as fetched 2026-09-26" is the dating, except where an entry gives a version date (V-3). an independent check re-opened V-1 to V-3 the same day and found every number unchanged; it also corrected two notes in this file (V-1 fonts, V-3 revision history), fixed below. Re-open the page before relying on a number for a title going to a retailer. Numbers not opened are marked NOT OPENED and are leads, not rules.

## V-1: Amazon KDP, paperback submission guidelines
URL: https://kdp.amazon.com/en_US/help/topic/G201857950 (fetched 2026-09-26)
- "Minimum resolution of 300 DPI. There is no set maximum DPI for images, however, images with excessively high resolutions may result in files timing out during processing, or may cause manufacturing delays. We recommend a maximum resolution of 600 DPI, to keep your total file size under 650MB."
- "If you want your images to bleed to the edges of your pages, extend them 0.125" (3.2 mm) beyond the final trim size from the top, bottom, and outer edges of your manuscript."
- "If your book has images or elements that bleed to the edges of your pages, you must upload your manuscript as a PDF."
- "All images (both cover and manuscript) should be at least 300 DPI."
- "Format your PDF manuscript at 0.25" (6.4 mm) higher and 0.125" (3.2 mm) wider than your selected trim size in order to print the full bleed area." (Interior specifications.) This is the page-size rule the bleed test uses: a 6×9 in trim becomes a 6.125×9.25 in page.
- Fonts: "Embed all fonts on the cover in the native program before publishing." (cover specifications) and "All fonts in the interior files should be embedded in the native program before publishing." (an interior-fonts sentence; an independent read of the raw page places it under Interior specifications → Font, while my fetch labelled it File guidelines, so it is cited here by the sentence, not by heading). The page states embedding for interiors as well as covers. (An earlier version of this note said the sentence was cover-only; that was wrong.) Also: "Flatten transparent objects and layers in the native file before publishing."
- The page states no colour mode for interior images. That absence is why CMYK conversion is SPECULATIVE in Job 1.

## V-2: Amazon KDP, image requirements for reflowable eBooks
URL: https://kdp.amazon.com/en_US/help/topic/G75V4YX5X8GRGXWV (fetched 2026-09-26)
- Pictorial images: "We recommend these type of images occupy at least 60% width of the screen for high quality reading on smaller devices."
- Text-bearing images: "We recommend these type of images occupy at least 80% width of the screen for high quality reading on smaller devices."
- "Cover images should always have a full-page layout and be at least 1200 pixels in width or height."
- "Kindle devices and reading applications do not support TIFF, multi-frame GIFs, or images with transparent areas."
- "Use sRGB color profile for all your images. Kindle does not support CMYK color space."
- "Set the height of inline images in 'EM' units so that it displays and scales proportional to surrounding text content."
- "Provide inline images in lossless format where possible." (Names no format.) The AYAH prep resamples interior photos to JPEG quality 82, which is lossy; that trade is an engineering choice, not something this page endorses.
- "For accessibility, all images must have text in the alt attribute in the HTML tag." "For decorative images, set alt = \"\" or role = \"presentation\" in the image tag so that it can be ignored by assistive technology." "Alt text should be short, concise and specific." This is the page behind Job 1's informative-vs-decorative decision.
- The page states no DPI, no per-file size limit and no preferred JPEG/PNG. (A search-result summary of KDP's guidelines attributed a 300 DPI recommendation to the eBook pages; the reflowable page itself does not say it. Only the page text is used here.)

## V-3: Apple Books Asset Guide, interior image requirements
URL: https://help.apple.com/itc/booksassetguide/en.lproj/itca71ad3c33.html (fetched 2026-09-26; the guide listing read "Apple Books Asset Guide 5.3.1")
- "Images within the EPUB cannot exceed 5.6 million pixels."
- "Apple recommends providing images that are at least 1.5 times the intended viewing size, up to a maximum of 5.6 million pixels."
- "RGB (screen standard)." / "Apple recommends that you set the colorspace on your book images to sRGB."
- "JPEG with .jpg or .jpeg extension (quality unconstrained) or PNG with .png extension."
- "The maximum recommended size is about 10 MB of un-encoded image data per XHTML file."
- **"All text must be created using HTML. Embedding text in images creates issues that cause a large number of customer complaints: customers can't use the dictionary or search the text, and in addition, the book becomes not accessible for persons using the VoiceOver feature. Therefore, books with images that contain embedded text are rejected from sale on Apple Books."** This is the first rule on the page. The guide's general section adds: "All images should be prepared in digital format and should not contain any text. All text must be created using HTML." and "Apple recommends that SVG should be used sparingly."
- "Make sure all images are accessible."
- "Images should be defined using img tags in the HTML." / "use the HTML img tag instead of wrapping images in svg:image."
- **Revision history:** the guide's Revision History (https://help.apple.com/itc/booksassetguide/en.lproj/static.html, fetched 2026-09-26) reads "Version 5.3.1 (February 2025): Added a section on accessibility. Clarified information on book versioning and delivering OPF metadata." the independent check reports further dated entries (September 2023 for 5.3, April 10 2022 for 5.2.14, with 5.2.13 dated December 12 2022, an apparent ordering inconsistency); my own fetch did not return those, so only 5.3.1 is quoted here. The single Interior Image Requirements page carries no date.
- **Exposure of this repo's own worked book:** the AYAH figures are 16 SVGs, each containing labels as text (Job 1, I-13). On this page's rule they would be at risk on Apple Books, and the insert-only fix candidate carries the same 16. Whether this book is offered on Apple Books is not recorded here. The exposure matters to anyone using this skill for an Apple-bound book. Whether Apple would treat an SVG figure's text as "embedded text" is not stated on the page; the safe reading is that it might.
- Un-encoded size is not defined on the page. This skill computes width × height × 3 bytes (8-bit RGB) as its reading of "un-encoded". State that when quoting the number.

## V-4: Kobo Writing Life — NOT OPENED
URLs tried 2026-09-26: `.../articles/360059386271-File-Types-Sizes` and `.../articles/360059385611-EPUB-Best-Practices` on `kobowritinglife.zendesk.com`. Both returned HTTP 403 to the fetch tool.
- A search-result summary (second-hand, not the page) mentioned 300 DPI, "no larger than 5 MB" per image and a 100 MB book limit. **Unverified.** Do not quote as a Kobo requirement.
- **Operator step:** open the two articles in a browser, paste the image and file-size limits into this file with the date, and change this entry from NOT OPENED to fetched.

## V-5: IngramSpark and KDP trim/bleed/barcode — NOT RE-FETCHED
The 2026-09-22 snapshot in `publishing-preparation-skill/reference/retail-technical-requirements.md` is the record for trim, bleed sizes and barcode. This skill cites it and does not restate it. If a number matters, re-check it there.

## V-6: Kindle Previewer (Amazon)
URL: https://kdp.amazon.com/en_US/help/topic/G202131170 (fetched 2026-09-26; an independent check confirmed the quotes verbatim on the raw HTML the same day)
- "Use Kindle Previewer, a free desktop standalone application, as you format your book so you can make sure it looks as intended."
- "Kindle Previewer currently shows you how your book would appear on Fire Tablets, Kindle for Android, Kindle for iOS, and Kindle E-readers."
- "Kindle Previewer opens eBooks in .epub, .htm, .html, .xhtml, .opf, .kpf, .doc, and .docx formats."

## V-7: KDP Online Previewer
URL: https://kdp.amazon.com/en_US/help/topic/G200641240 (fetched 2026-09-26; confirmed verbatim by an independent check)
- "Our Online Previewer tool shows you what your eBook will look like on different devices tablets, phones, and Kindle E-Readers." Its quality check includes "Image Check. The side-panel can detect low quality images that can appear blurry on Kindle devices."
- The page says nothing about republishing effects, review, or how customers holding an older file are affected.

## Tool versions used (not vendor claims)
`epubcheck` 5.4.0 (Homebrew), validating "using EPUB version 3.4 rules" per its own output; `pandoc` from Homebrew; poppler `pdfimages`/`pdffonts`/`pdfinfo`; Ghostscript `gs`. All run locally 2026-09-26.
