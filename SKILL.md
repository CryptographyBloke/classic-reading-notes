---
name: classic-reading-notes
description: Generate editable Chinese classic-reading-note Word DOCX files from short book requests such as “书名号122,书名活着”, “书籍码119，书名哈姆雷特”, or a multi-book list. The agent writes fact-grounded 内容概括 and 读书感悟 (at least 700 Chinese characters each), fills a user-provided school DOCX or included generic template, applies 黑体四号加粗 headings and 宋体小四 body, validates length and formatting, and returns downloadable files. Also use when users want to batch-fill school reading-note templates.
---

# Classic Reading Notes · Agent Instructions

## Trigger and output

Treat \`书名号122,书名活着\` and \`书籍码122，书名《活着》\` as equivalent. Accept \`122：《活着》余华\` and multiple lines. Output one Word DOCX per book, not merely chat text. Read [AGENTS.md](AGENTS.md), [README.md](README.md), [references/input-schema.md](references/input-schema.md) and [references/writing-guidelines.md](references/writing-guidelines.md).

## Workflow

1. Parse books (\`code\`, \`title\`, optional \`author\`). Read reader data from this user's current instructions (\`grade\`, \`major\`, \`class_name\`, \`name\`); leave unspecified fields empty and do not invent identities.
2. If the user provided a book PDF/document, read it. Otherwise use reliable known information; do not invent quotes, plot details, page numbers, or edition-specific facts.
3. Write two distinct sections for each book: \`summary\` = 内容概括; \`reflection\` = 读书感悟. Each must contain **at least 700 Han characters**, excluding punctuation and English words. Aim for 900–1200 characters in 5–7 coherent paragraphs per section. Do not pad with repeated sentences.
4. Create UTF-8 \`batch.json\` according to \`references/input-schema.md\`. \`books[].summary\` and \`books[].reflection\` are **arrays of paragraphs**. The optional \`scripts/parse_books.py\` only creates a blank skeleton; **the agent must fill both arrays with real text**.
5. Install dependencies: \`python -m pip install -r requirements.txt\`.
6. If user provided a compatible school template, pass it using \`--template\`. Otherwise create a generic one using \`python scripts/init_template.py --output assets/通用经典阅读模板.docx\`. The generic file is **not a school-branded template**.
7. Execute:
   \`\`\`bash
   python scripts/fill_template.py --input batch.json --template assets/通用经典阅读模板.docx --output-dir output
   python scripts/check_documents.py --input batch.json --output-dir output
   \`\`\`
   Replace the template path if needed. The generated documents must use 黑体 14pt bold for title/section headings and 宋体 12pt for body, maintain original cover and reader details when using a supplied template.
8. Render to images for visual QA if possible (\`python scripts/render_preview.py --input output/FILE.docx --output-dir previews\` requires LibreOffice + Poppler). If not possible, never claim visual inspection occurred.
9. Return actual DOCX artifact links, one per title. Explain failures clearly; do not fabricate files, source citations, or successful tests.

## Further references

- \`AGENTS.md\`: concise instruction for coding agents.
- \`README.md\`: complete user-facing and agent-facing tutorial.
- \`references/input-schema.md\`: JSON input format and examples.
- \`references/writing-guidelines.md\`: content writing standards.
- \`scripts/parse_books.py\`: short-form parsing, no AI writing.
- \`scripts/init_template.py\`: safe generic template creator.
- \`scripts/fill_template.py\`: DOCX formatter and generator.
- \`scripts/check_documents.py\`: automated document checks.
- \`scripts/render_preview.py\`: optional visual preview.

Never hard-code any person's private profile in this public Skill.
