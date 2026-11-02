# Agent 执行协议（请先阅读）

你是具备文件操作和 Python 执行工具的 Agent。当用户将本仓库链接和一句书单（如 \`书名号122,书名活着\`）发给你时，按以下步骤完成**真实的 DOCX 交付**。

1. 阅读根目录的 \`README.md\`、\`SKILL.md\` 和 \`references/input-schema.md\`。不要把仅回复文章当作完成。
2. 识别 \`书名号\` / \`书籍码\` / \`编号\`、\`书名\`、可选作者。支持 \`122：《活着》余华\` 和多行书单。信息已给出时不要反复追问。
3. 个人信息包含年级、专业、班级、姓名，仅从当前用户输入读取，未知则留空。**不得将某一学生的信息硬编码到公开仓库或其他用户的文件里**。
4. 根据原书材料或高置信度的作品知识撰稿。每本书分别写 \`summary\`（内容概括）和 \`reflection\`（读书感悟），**每部分至少700个汉字**，建议各900–1200字，写成若干自然段。不得编造精确页码、无出处直接引语或读过指定版本的经历。原书可访问时优先阅读。
5. 按 \`references/input-schema.md\` 将两部分保存为 \`batch.json\`。可用 \`scripts/parse_books.py\` 先解析书名，但解析器只生成空白草稿，**不会自动写正文**。
6. 安装依赖 \`python -m pip install -r requirements.txt\`。如无用户学校模板，运行 \`python scripts/init_template.py --output assets/通用经典阅读模板.docx\`，再运行：
   \`\`\`bash
   python scripts/fill_template.py --input batch.json --output-dir output --template assets/通用经典阅读模板.docx
   python scripts/check_documents.py --input batch.json --output-dir output
   \`\`\`
7. 如用户提供自己的学校模板，改用 \`--template /path/to/template.docx\`，严格保留其封面图片和格式；不得把无校徽的通用模板说成该校原版。
8. 能使用 LibreOffice / Poppler 或宿主 DOCX 渲染能力时，将文档渲染成图片逐页查看；不具备工具时坦诚说明。
9. 返回每个**真实存在**的 \`.docx\` 文件下载链接/附件；不要伪造路径。

工具要求：Python 3.9+、\`python-docx\`；渲染可选 LibreOffice 和 Poppler。若当前聊天工具不支持代码/文件执行，说明限制并指引用户切换到合适的 Agent 模式。
