#!/usr/bin/env python3
"""Parse short Chinese book lists into a draft JSON. This does NOT write essays."""
import argparse
import json
import re
from pathlib import Path


def parse_line(line):
    line = line.strip().strip('“”"')
    if not line or line.startswith("#"):
        return None
    # "书名号122,书名活着,作者余华" and "书籍码122，书名《活着》"
    cm = re.search(r"(?:书籍码|书名号|书籍编号|编号)\s*[：:=]?\s*([\w-]+)", line)
    tm = re.search(r"(?:^|[,，;；]\s*)书名(?!号)\s*[：:=]?\s*《?([^》,，;；\n]+)》?", line)
    am = re.search(r"(?:^|[,，;；]\s*)作者\s*[：:=]?\s*([^,，;；\n]+)", line)
    code = cm.group(1).strip() if cm else ""
    author = am.group(1).strip() if am else ""
    if tm:
        title = tm.group(1).strip().strip("《》 ")
    else:
        m = re.match(r"(?:(\d+[A-Za-z]?)\s*[：:]\s*)?《([^》]+)》\s*(.*)$", line)
        if m:
            code = m.group(1) or code
            title = m.group(2).strip()
            author = author or m.group(3).strip()
        else:
            m = re.match(r"(?:(\d+[A-Za-z]?)\s*[：:]\s*)?(.+)$", line)
            if not m:
                raise ValueError("Cannot parse book: " + line)
            code = m.group(1) or code
            title = m.group(2).strip()
    if not title:
        raise ValueError("Missing title: " + line)
    return {"code": code, "title": title, "author": author,
            "summary": [], "reflection": []}


def main():
    p = argparse.ArgumentParser(description="Book lines -> JSON skeleton (no AI writing)")
    p.add_argument("--text")
    p.add_argument("--input-file", type=Path)
    p.add_argument("--output", type=Path, default=Path("batch.json"))
    p.add_argument("--grade", default="")
    p.add_argument("--major", default="")
    p.add_argument("--class-name", default="")
    p.add_argument("--name", default="")
    a = p.parse_args()
    if not a.text and not a.input_file:
        p.error("Use --text or --input-file")
    raw = a.input_file.read_text(encoding="utf-8-sig") if a.input_file else a.text
    chunks = [part for line in raw.splitlines()
              for part in re.split(r"\s*[;；]\s*", line) if part.strip()]
    books = [b for chunk in chunks if (b := parse_line(chunk))]
    if not books:
        p.error("No books found")
    data = {"profile": {"grade": a.grade, "major": a.major,
                         "class_name": a.class_name, "name": a.name},
            "books": books}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Parsed {len(books)} book(s) into {a.output}")
    print("IMPORTANT: Agent must fill summary/reflection before running fill_template.py")


if __name__ == "__main__":
    main()
