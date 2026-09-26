#!/usr/bin/env python3
"""Negative-case tests for format-census.py. Run:  python3 tools/test_format_census.py   (stdlib only)

Each test builds its own tiny inputs in a temp folder. The cases are the ones a real book's
HTML can hit: single-quoted attributes, ">" inside an alt, a missing tool, a genuine FAIL, an
unreadable file. No network, no book files, no pdfimages needed.
"""
import contextlib, importlib.util, io, os, sys, tempfile, unittest, zipfile
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("fc", os.path.join(HERE, "format-census.py"))
fc = importlib.util.module_from_spec(spec); spec.loader.exec_module(fc)

PNG_A, PNG_B = b"\x89PNG-A", b"\x89PNG-B"


def write(path, data, mode="w"):
    with open(path, mode) as f:
        f.write(data)
OPF = """<?xml version="1.0"?><package xmlns="http://www.idpf.org/2007/opf"><manifest>
<item id="c1" href="text/c1.xhtml" media-type="application/xhtml+xml"/></manifest>
<spine><itemref idref="c1"/></spine></package>"""


def make_epub(path, body, media):
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("EPUB/content.opf", OPF)
        z.writestr("EPUB/text/c1.xhtml", f"<html><body>{body}</body></html>")
        for name, data in media.items():
            z.writestr(f"EPUB/media/{name}", data)


def run_main(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = fc.main(argv)
    return code, out.getvalue(), err.getvalue()


class Census(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.d, "img"))
        for n, b in (("a.png", PNG_A), ("b.png", PNG_B)):
            write(os.path.join(self.d, "img", n), b, "wb")

    def p(self, name): return os.path.join(self.d, name)

    def test_single_quoted_attributes_are_not_a_false_fail(self):
        html = "<img src='img/a.png' alt='a described image'><img src='img/b.png' alt=''>"
        write(self.p("s.html"), html)
        make_epub(self.p("b.epub"), "<img src='../media/a.png' alt='a described image'/><img src='../media/b.png' alt=''/>",
                  {"a.png": PNG_A, "b.png": PNG_B})
        code, out, _ = run_main(["--html", self.p("s.html"), "--src-dir", self.d, "--epub", self.p("b.epub")])
        self.assertEqual(code, 0, out)
        self.assertIn("same images, same order", out)
        self.assertIn("1/1/0", out)   # one described, one deliberately empty, none missing

    def test_gt_inside_alt_does_not_truncate_the_tag(self):
        write(self.p("g.html"), '<img src="img/a.png" alt="has > sign">')
        code, out, _ = run_main(["--html", self.p("g.html")])
        self.assertEqual(code, 0)
        self.assertIn("1/0/0", out)   # described, not missing

    def test_missing_alt_is_counted_missing_and_valueless_alt_is_empty(self):
        write(self.p("m.html"), '<img src="img/a.png"><img src="img/b.png" alt>')
        _, out, _ = run_main(["--html", self.p("m.html")])
        self.assertIn("0/1/1", out)

    def test_missing_pdfimages_is_exit_3_not_a_fail(self):
        write(self.p("x.pdf"), b"%PDF-1.4", "wb")
        with mock.patch.object(fc.shutil, "which", return_value=None):
            code, out, err = run_main(["--pdf", self.p("x.pdf")])
        self.assertEqual(code, 3)
        self.assertNotIn("FAIL", out)
        self.assertIn("not found", err)

    def test_genuine_fail_is_still_exit_1(self):
        write(self.p("f.html"), '<img src="img/a.png" alt="a"><img src="img/b.png" alt="b">')
        make_epub(self.p("f.epub"), '<img src="../media/a.png" alt="a"/>', {"a.png": PNG_A})
        code, out, _ = run_main(["--html", self.p("f.html"), "--src-dir", self.d, "--epub", self.p("f.epub")])
        self.assertEqual(code, 1)
        self.assertIn("DIFFERS", out)

    def test_reordered_images_fail(self):
        write(self.p("r.html"), '<img src="img/a.png" alt="a"><img src="img/b.png" alt="b">')
        make_epub(self.p("r.epub"), '<img src="../media/b.png" alt="b"/><img src="../media/a.png" alt="a"/>',
                  {"a.png": PNG_A, "b.png": PNG_B})
        code, _, _ = run_main(["--html", self.p("r.html"), "--src-dir", self.d, "--epub", self.p("r.epub")])
        self.assertEqual(code, 1)

    def test_unreadable_file_is_exit_3(self):
        code, _, err = run_main(["--epub", self.p("does-not-exist.epub")])
        self.assertEqual(code, 3)
        self.assertIn("cannot open", err)

    def test_not_a_zip_is_exit_3(self):
        write(self.p("bad.epub"), "not a zip")
        code, _, _ = run_main(["--epub", self.p("bad.epub")])
        self.assertEqual(code, 3)

    def test_no_arguments_is_usage_exit_2(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(fc.main([]), 2)

    def test_min_ppi_uses_the_lower_of_x_and_y(self):
        listing = ("page num type width height color comp bpc enc interp object ID x-ppi y-ppi size ratio\n"
                   "------\n"
                   "1 0 image 100 100 rgb 3 8 jpeg no 4 0 300 150 10K 1%\n")
        self.assertEqual(fc.parse_pdfimages(listing)["min_ppi"], 150)

    def test_svg_wrapping_an_image_is_a_reference_not_artwork(self):
        make_epub(self.p("w.epub"),
                  '<svg xmlns="http://www.w3.org/2000/svg"><image href="../media/a.png"/></svg><svg><rect/></svg>',
                  {"a.png": PNG_A})
        r = fc.epub_census(self.p("w.epub"))
        self.assertEqual(r["refs"], 2)      # one wrapper + one artwork svg
        self.assertEqual(r["vector"], 1)    # only the artwork svg is vector

    def test_docx_alt_split_and_gt_in_descr(self):
        doc = ('<w:document xmlns:w="w" xmlns:wp="wp"><wp:docPr id="1" descr="ok &gt; fine"/>'
               '<wp:docPr id="2" descr=""/><wp:docPr id="3"/></w:document>')
        with zipfile.ZipFile(self.p("d.docx"), "w") as z:
            z.writestr("word/document.xml", doc)
            z.writestr("word/media/i.png", PNG_A)
        r = fc.docx_census(self.p("d.docx"))
        self.assertEqual(r["alt"], "1/1/1")


if __name__ == "__main__":
    unittest.main(verbosity=2)
