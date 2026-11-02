#!/usr/bin/env python3
"""Check generated DOCX: title, identity, paragraphs, Han counts, explicit fonts."""
import argparse
from pathlib import Path
from docx import Document
from fill_template import (FIELDS, InputError, count_han, count_nonspace, load_batch,
                           output_filename, anchor, title_anchor, index)


def check_font(p, family, size, bold, label):
    has_text = False
    for r in p.runs:
        if not r.text.strip():
            continue
        has_text = True
        prop = r._element.get_or_add_rPr()
        ff = prop.rFonts
        east = ff.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia') if ff is not None else None
        if east != family or r.font.name != family:
            raise InputError(f"{label}: expected {family} font, found {east}/{r.font.name}")
        if r.font.size is None or abs(r.font.size.pt - size) > 0.1:
            raise InputError(f"{label}: expected font size {size}pt")
        if r.bold is not bold:
            raise InputError(f"{label}: bold mismatch")
    if not has_text:
        raise InputError(f"{label}: empty paragraph")


def content_section(doc, first, second=None):
    ps = list(doc.paragraphs)
    i = index(ps, anchor(doc, first)) + 1
    j = index(ps, anchor(doc, second)) if second else len(ps)
    return ps[i:j]


def check(path, profile, book, min_han, min_nonspace):
    if not path.is_file():
        raise InputError(f"Missing document {path}")
    doc = Document(path)
    title = title_anchor(doc)
    if title.text != f"《{book['title']}》读书笔记":
        raise InputError(f"{path.name}: wrong title")
    check_font(title, "黑体", 14, True, "title")
    for h in ("内容概括", "读书感悟"):
        check_font(anchor(doc, h), "黑体", 14, True, h)
    for key, label in FIELDS:
        found = [p for p in doc.paragraphs if p.text.startswith(label+"：")]
        if len(found) != 1 or found[0].text != f"{label}：{profile.get(key, '')}":
            raise InputError(f"{path.name}: profile {label} mismatch")
    for heading, end, key in (("内容概括","读书感悟","summary"),
                              ("读书感悟",None,"reflection")):
        ps = content_section(doc, heading, end)
        if [p.text for p in ps] != book[key]:
            raise InputError(f"{path.name}: content or paragraph mismatch in {heading}")
        raw = "".join(p.text for p in ps)
        if count_han(raw) < min_han or count_nonspace(raw) < min_nonspace:
            raise InputError(f"{path.name}: word count too short in {heading}")
        for p in ps:
            check_font(p, "宋体", 12, False, heading+" body")
    for p in doc.paragraphs:
        if "不少于700字，如果编辑" in p.text or "《xxx》读书笔记" in p.text:
            raise InputError(f"{path.name}: leftover placeholder")
    return count_han("".join(book["summary"])), count_han("".join(book["reflection"]))


def main():
    p=argparse.ArgumentParser(description="Validate generated Chinese reading notes")
    p.add_argument("--input",required=True,type=Path)
    p.add_argument("--output-dir",type=Path,default=Path("output"))
    p.add_argument("--min-han",type=int,default=700)
    p.add_argument("--min-nonspace",type=int,default=0)
    a=p.parse_args()
    try:
        profile,books=load_batch(a.input,a.min_han,a.min_nonspace)
        for book in books:
            path=a.output_dir/output_filename(book,profile)
            s,r=check(path,profile,book,a.min_han,a.min_nonspace)
            print(f"PASS: {path} | summary {s} Han / reflection {r} Han")
    except (InputError,OSError,ValueError) as err:
        p.exit(2,f"FAIL: {err}\n")


if __name__=="__main__":
    main()
