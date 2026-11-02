"""End-to-end tests for parsing, DOCX generation and validation."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from parse_books import parse_line
from init_template import build
from fill_template import load_batch, output_filename, fill_document
from check_documents import check


class ReadingNotesTest(unittest.TestCase):
    def test_short_prompts(self):
        samples = [
            ("书名号122,书名活着,作者余华", "122", "活着", "余华"),
            ("书籍码119，书名《哈姆雷特》", "119", "哈姆雷特", ""),
            ("120：《中国建筑史》梁思成", "120", "中国建筑史", "梁思成"),
            ("121：《机器学习》周志华", "121", "机器学习", "周志华"),
        ]
        for raw, code, title, author in samples:
            with self.subTest(raw=raw):
                book = parse_line(raw)
                self.assertEqual((book["code"], book["title"], book["author"]),
                                 (code, title, author))

    def test_document_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            template = root / "generic.docx"
            build(template)
            book = parse_line("书名号122,书名活着,作者余华")
            # Synthetic test paragraphs, NOT a reading-note sample.
            book["summary"] = ["这是格式测试内容。" * 115]
            book["reflection"] = ["这是段落验收文本。" * 115]
            data = {"profile": {"grade": "", "major": "", "class_name": "", "name": ""},
                    "books": [book]}
            payload = root / "batch.json"
            payload.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            profile, books = load_batch(payload)
            output = root / output_filename(books[0], profile)
            fill_document(template, profile, books[0]).save(output)
            self.assertTrue(output.is_file())
            s, r = check(output, profile, books[0], 700, 0)
            self.assertGreaterEqual(s, 700)
            self.assertGreaterEqual(r, 700)


if __name__ == "__main__":
    unittest.main()
