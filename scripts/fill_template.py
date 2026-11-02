#!/usr/bin/env python3
"""Create one formatted Chinese reading-note DOCX per book from batch JSON."""
import argparse
import json
import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt
from docx.text.paragraph import Paragraph

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TEMPLATE = ROOT / "assets" / "通用经典阅读模板.docx"
FIELDS = (("grade", "年级"), ("major", "专业"),
          ("class_name", "班级"), ("name", "姓名"))


class InputError(ValueError):
    pass


def count_han(s):
    return sum("\u4e00" <= ch <= "\u9fff" for ch in s)


def count_nonspace(s):
    return sum(not ch.isspace() for ch in s)


def clean_title(s):
    s = s.strip()
    return s[1:-1].strip() if s.startswith("《") and s.endswith("》") else s


def safe_file(s):
    s = re.sub(r'[\\/:*?"<>|\x00-\x1f]', "_", s)
    return re.sub(r"\s+", " ", s).strip(" .")[:110] or "未命名"


def output_filename(book, profile):
    parts = [book.get("code", ""), clean_title(book["title"]),
             profile.get("name", ""), "模板版"]
    return safe_file("_".join(str(x) for x in parts if x)) + ".docx"


def load_batch(path, min_han=700, min_nonspace=0):
    try:
        d = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as e:
        raise InputError("Cannot parse batch JSON: " + str(e)) from e
    if not isinstance(d, dict):
        raise InputError("JSON root must be an object")
    profile = d.get("profile") or {}
    if not isinstance(profile, dict):
        raise InputError("profile must be an object")
    for key, _ in FIELDS:
        v = profile.get(key, "")
        if v is None:
            v = ""
        if not isinstance(v, str):
            raise InputError("profile." + key + " must be text")
        profile[key] = v.strip()
    books = d.get("books")
    if not isinstance(books, list) or not books:
        raise InputError("books must be a nonempty list")
    parsed, seen = [], set()
    for i, raw in enumerate(books):
        if not isinstance(raw, dict) or not isinstance(raw.get("title"), str):
            raise InputError(f"books[{i}] missing title")
        book = dict(raw)
        book["title"] = clean_title(book["title"])
        book["code"] = str(book.get("code") or "").strip()
        if not book["title"]:
            raise InputError(f"books[{i}] empty title")
        ident = (book["code"], book["title"])
        if ident in seen:
            raise InputError("Duplicate book: " + str(ident))
        seen.add(ident)
        for key in ("summary", "reflection"):
            arr = book.get(key)
            if not isinstance(arr, list) or not arr or any(
                not isinstance(x, str) or not x.strip() for x in arr
            ):
                raise InputError(f"books[{i}].{key}: expected a nonempty list of paragraphs")
            book[key] = [x.strip() for x in arr]
            text = "".join(book[key])
            if count_han(text) < min_han or count_nonspace(text) < min_nonspace:
                raise InputError(f"{book['title']} {key}: too short ({count_han(text)} Han)")
        parsed.append(book)
    names = [output_filename(book, profile).lower() for book in parsed]
    if len(names) != len(set(names)):
        raise InputError("Output filenames collide")
    return profile, parsed


def font(run, family, size, bold=False):
    run.font.name = family
    run.font.size = Pt(size)
    run.bold = bold
    prop = run._element.get_or_add_rPr()
    ff = prop.rFonts
    if ff is None:
        ff = OxmlElement("w:rFonts")
        prop.insert(0, ff)
    for kind in ("ascii", "hAnsi", "eastAsia", "cs"):
        ff.set(qn("w:" + kind), family)


def write_text(p, text, family, size, bold=False):
    p.text = text
    if not p.runs:
        p.add_run(text)
    for run in p.runs:
        font(run, family, size, bold)


def anchor(doc, text):
    matches = [p for p in doc.paragraphs if p.text.strip() == text]
    if len(matches) != 1:
        raise InputError(f"Template must contain exactly one paragraph: {text}")
    return matches[0]


def title_anchor(doc):
    found = [p for p in doc.paragraphs if "读书笔记" in p.text and "《" in p.text]
    if len(found) != 1:
        raise InputError("Cannot uniquely locate 《xxx》读书笔记 in template")
    return found[0]


def index(paragraphs, p):
    for i, v in enumerate(paragraphs):
        if v._p is p._p:
            return i
    raise InputError("Paragraph not in document")


def remove(p):
    if p._p.xpath("./w:pPr/w:sectPr"):
        raise InputError("Refusing to remove a paragraph containing section properties")
    p._p.getparent().remove(p._p)


def new_body_after(p, content):
    element = OxmlElement("w:p")
    p._p.addnext(element)
    result = Paragraph(element, p._parent)
    result.style = "Normal"
    font(result.add_run(content), "宋体", 12, False)
    result.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf = result.paragraph_format
    pf.first_line_indent = Pt(24)
    pf.line_spacing = 1.5
    pf.space_before = Pt(0)
    pf.space_after = Pt(4)
    pf.keep_with_next = False
    return result


def fill_document(template, profile, book):
    doc = Document(str(template))
    title, summary, reflection = title_anchor(doc), anchor(doc, "内容概括"), anchor(doc, "读书感悟")
    ps = list(doc.paragraphs)
    a, b, c = [index(ps, p) for p in (title, summary, reflection)]
    if not (a < b < c):
        raise InputError("Template heading order is invalid")
    for key, label in FIELDS:
        matched = [p for p in doc.paragraphs if re.match(r"^\s*" + label + r"\s*[：:]", p.text)]
        if len(matched) != 1:
            raise InputError(f"Missing or ambiguous profile field: {label}")
        write_text(matched[0], f"{label}：{profile.get(key, '')}", "黑体", 14, True)
    write_text(title, f"《{book['title']}》读书笔记", "黑体", 14, True)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.keep_with_next = True
    for heading in (summary, reflection):
        write_text(heading, heading.text.strip(), "黑体", 14, True)
        heading.paragraph_format.keep_with_next = True
    for p in ps[b+1:c]:
        remove(p)
    # Original prompt beneath last section must also be removed.
    ps = list(doc.paragraphs)
    for p in ps[index(ps, reflection)+1:]:
        remove(p)
    parent = summary
    for text in book["summary"]:
        parent = new_body_after(parent, text)
    parent = reflection
    for text in book["reflection"]:
        parent = new_body_after(parent, text)
    doc.core_properties.title = f"《{book['title']}》读书笔记"
    return doc


def main():
    p = argparse.ArgumentParser(description="Fill a Word reading-note template with authored JSON")
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    p.add_argument("--output-dir", type=Path, default=Path("output"))
    p.add_argument("--min-han", type=int, default=700)
    p.add_argument("--min-nonspace", type=int, default=0)
    a = p.parse_args()
    try:
        if a.min_han < 0 or a.min_nonspace < 0:
            raise InputError("Minimum counts must be nonnegative")
        if not a.template.is_file():
            raise InputError(f"Template not found: {a.template}; run scripts/init_template.py first")
        profile, books = load_batch(a.input, a.min_han, a.min_nonspace)
        a.output_dir.mkdir(parents=True, exist_ok=True)
        for book in books:
            dest = a.output_dir / output_filename(book, profile)
            fill_document(a.template, profile, book).save(dest)
            print(f"OK: {dest} | summary {count_han(''.join(book['summary']))} Han | reflection {count_han(''.join(book['reflection']))} Han")
    except (InputError, ValueError, OSError) as exc:
        p.exit(2, f"ERROR: {exc}\n")


if __name__ == "__main__":
    main()
