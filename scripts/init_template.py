#!/usr/bin/env python3
"""Create a generic three-section DOCX template without any school logo."""
import argparse
from pathlib import Path
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def font(run, name="黑体", size=14, bold=True):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    pr = run._element.get_or_add_rPr()
    ff = pr.rFonts
    if ff is None:
        ff = OxmlElement("w:rFonts")
        pr.insert(0, ff)
    for k in ("ascii", "hAnsi", "eastAsia", "cs"):
        ff.set(qn("w:" + k), name)


def para(doc, text, *, size=14, bold=True, center=False, after=0):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if center else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_after = Pt(after)
    font(p.add_run(text), "黑体" if bold else "宋体", size, bold)
    return p


def build(path):
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.top_margin, sec.bottom_margin = Cm(2.3), Cm(2.3)
    sec.left_margin, sec.right_margin = Cm(2.6), Cm(2.6)
    para(doc, "经典阅读个人汇总", size=23, center=True, after=30)
    para(doc, "60 次经典阅读", size=22, center=True, after=25)
    para(doc, "读书笔记", size=20, center=True)
    doc.add_page_break()
    para(doc, "个人信息", size=18, center=True, after=35)
    for label in ("年级：", "专业：", "班级：", "姓名："):
        para(doc, label, after=25)
    doc.add_page_break()
    para(doc, "《xxx》读书笔记", center=True, after=18)
    p = para(doc, "内容概括", after=12)
    p.paragraph_format.keep_with_next = True
    para(doc, "（不少于700字，如果编辑，请把这段话删除）", size=12, bold=False)
    p = para(doc, "读书感悟", after=12)
    p.paragraph_format.keep_with_next = True
    para(doc, "（不少于700字，如果编辑，请把这段话删除）", size=12, bold=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(path)
    print("Template created:", path)


def main():
    p = argparse.ArgumentParser(description="Build a generic blank DOCX; no school logo included")
    p.add_argument("--output", type=Path, default=Path("assets/通用经典阅读模板.docx"))
    a = p.parse_args()
    build(a.output)


if __name__ == "__main__":
    main()
