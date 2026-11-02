# Classic Reading Notes — 经典阅读读书笔记 Agent Skill

> 把这个仓库的链接交给 **能够读取 GitHub、运行 Python、创建和返回文件** 的 AI Agent，再说“书名号122，书名《活着》”，它就可以撰写读书笔记、填入 Word 模板、检查格式，并返回 DOCX 下载文件。
>
> 这是 **Agent 工作流 + Word 生成脚本**，不是在线网页服务。脚本只负责确定性的文件制作；文章由你选用的 AI Agent 撰写，因此不需要本仓库自带 LLM API Key。

## ⭐ 最快使用：直接复制这一段给你的 Agent

~~~text
请读取这个 GitHub 仓库里的 README.md、AGENTS.md、SKILL.md，并严格执行：
https://github.com/CryptographyBloke/classic-reading-notes

书名号122，书名《活着》，作者余华。

请完成：
1. 阅读 Skill 的写作规范，为此书撰写中文“内容概括”和“读书感悟”，各不少于 700 汉字，建议各 900–1200 汉字。
2. 如果有原著或课程资料，先基于资料撰写；没有资料时，只写你有把握的书籍信息，不能杜撰引文、页码或细节。
3. 创建符合 references/input-schema.md 的 batch.json；每本书的 summary、reflection 都要是非空的自然段数组。
4. 安装 requirements.txt 的依赖，调用 scripts/fill_template.py 和 scripts/check_documents.py。
5. 若我上传学校原版 Word 模板，使用该模板；否则调用 scripts/init_template.py 创建通用模板。
6. 可以渲染时逐页检查，没有渲染能力时如实说明。
7. 最后返回实际生成的 .docx 文件，不要只回复正文或伪造下载链接。

个人信息若没有提供，请在年级/专业/班级/姓名栏留空，不要臆造。已经给过的信息不要反复询问。
~~~

**以后已安装本 Skill 的 Agent，通常只需发：**

~~~text
书名号123，书名《小王子》
~~~

其他允许的书单格式：

~~~text
书籍码119，书名《哈姆雷特》，作者莎士比亚
120：《中国建筑史》梁思成
121：《机器学习》周志华
~~~

“书名号”在本项目中是“书籍码”的兼容别名。可以多行提交，**每本输出一个独立 Word 文件**。

**重要边界：** 把链接贴在不支持代码执行的普通聊天中，不能保证自动得到文件。Agent 需要有 GitHub 访问、文件读写和 Python 执行能力；如果没有，需要进入 Work/Code/Agent 模式或按下方手动教程运行。

## 功能与默认格式

- 书名主标题及“内容概括”“读书感悟”：**黑体、四号（14pt）、加粗**。
- 正文：**宋体、小四（12pt）**；首行缩进约两字，1.5 倍行距。
- “内容概括”和“读书感悟”分别 **不少于 700 个汉字**，标点、数字、英文字母不计入汉字数。
- 批量制作独立可编辑 DOCX，保留用户所选的学校模板已有封面、栏目和图片。
- 信息栏包括年级、专业、班级、姓名；均为可选字段，**本仓库不保存真实学生个人信息**。
- 内置文本/格式检查和可选 DOCX → PNG 逐页预览。

## 项目文件

~~~text
classic-reading-notes/
├── README.md
├── AGENTS.md                          # Agent 从仓库入口执行的协议
├── SKILL.md                           # Agent Skill 主说明
├── agents/openai.yaml
├── requirements.txt                   # python-docx
├── scripts/
│   ├── parse_books.py                 # 简短书目 → JSON 草稿
│   ├── fill_template.py               # JSON 内容 + 模板 → DOCX
│   ├── check_documents.py             # 字数/样式/信息核验
│   ├── init_template.py               # 生成不含校徽的通用模板
│   └── render_preview.py              # 可选视觉预览
├── references/
│   ├── input-schema.md
│   └── writing-guidelines.md
└── assets/                             # 可自行放入学校原版 DOCX 模板
~~~

## 手动使用教程（Windows / macOS / Linux）

### 第 1 步：克隆并安装依赖

需要 Python 3.9+、pip。终端运行：

~~~bash
git clone https://github.com/CryptographyBloke/classic-reading-notes.git
cd classic-reading-notes
python -m pip install -r requirements.txt
~~~

Windows 如没有 python 命令可尝试 py -m pip。也可在 GitHub 页面选 Code → Download ZIP 并解压。

### 第 2 步：解析书单

~~~bash
python scripts/parse_books.py --text '书名号122,书名活着,作者余华' --output batch.json
~~~

或把多行书目保存到 books.txt，运行：

~~~bash
python scripts/parse_books.py --input-file books.txt --output batch.json --grade '24级' --major '网络空间安全' --class-name '示例班' --name '示例同学'
~~~

**注意：这一步仅生成 JSON 骨架，绝不自动撰稿。** 如果只有一本书的标题而没有正文，脚本不能凭空生成读书笔记；此时应由 Agent 根据可靠的书籍资料完成写作。

### 第 3 步：由 Agent 完成 batch.json 的正文

格式如下（仅示例，字数不足；正式执行必须各不少于 700 个汉字）：

~~~json
{
  "profile": {
    "grade": "24级",
    "major": "网络空间安全",
    "class_name": "示例班级",
    "name": "示例同学"
  },
  "books": [{
    "code": "122",
    "title": "活着",
    "author": "余华",
    "summary": ["这是第一段内容概括，请由 Agent 写成完整正文。"],
    "reflection": ["这是第一段读书感悟，请由 Agent 写成完整正文。"]
  }]
}
~~~

- summary：内容概括，通常 5–7 自然段；介绍主要人物/主要概念、事件与核心主题。
- reflection：读书感悟，通常 5–7 自然段；针对书中具体内容写思考，不是重复 summary。
- 两部分各推荐 900–1200 汉字。**不要以重复句子凑字数。**
- 作者、书名、事实不能混淆；有原著附件就使用附件，不要伪造直接引语或页码。
- 更多细节参见 references/input-schema.md 和 references/writing-guidelines.md。

### 第 4 步：生成 Word 文件

**无学校模板：使用通用模板（立即可用，无校徽）：**

~~~bash
python scripts/init_template.py --output assets/通用经典阅读模板.docx
python scripts/fill_template.py --input batch.json --output-dir output --template assets/通用经典阅读模板.docx
~~~

**有学校原版 Word 模板：** 把 DOCX 放在本机（例如 assets/my-school.docx），然后：

~~~bash
python scripts/fill_template.py --input batch.json --output-dir output --template assets/my-school.docx
~~~

自定义 Word 必须含以下模板锚点：书名占位标题“《xxx》读书笔记”、**内容概括**、**读书感悟**及**年级：/专业：/班级：/姓名：**。如果原模板不同，先修改兼容规则，不要猜测段落位置。使用学校原件时，它原有的图片和封面将被保留；**通用模板没有校徽，请勿误称原版**。

运行成功后输出类似：

~~~text
output/122_活着_示例同学_模板版.docx
~~~

### 第 5 步：检查文档

~~~bash
python scripts/check_documents.py --input batch.json --output-dir output
~~~

该检查验证 Word 文件存在、书名及个人信息正确、两部分内容、最少汉字数、字号字体及是否残留模板占位符等。若报错请修复后重新生成。

如已安装 LibreOffice 和 Poppler（soffice 和 pdftoppm），还可以：

~~~bash
python scripts/render_preview.py --input 'output/122_活着_示例同学_模板版.docx' --output-dir previews
~~~

逐页确认封面、姓名栏、正文、分页与字体正常。没有这些工具时可以在 Word/WPS 中手动预览；**未渲染时不要声称已完成视觉验证**。

### 第 6 步：交付

Agent 应返回真实生成的 DOCX 附件或有效下载链接；在本地运行时文件就在 output/ 目录。不要把 PDF、图片预览或仅聊天文字冒充 Word 文件。

## 安装为 Skill

- **Claude Code**：将本仓库复制/链接到项目内 .claude/skills/classic-reading-notes/（以对应平台的当前说明为准）。
- **Codex / 使用 AGENTS.md 的代码 Agent**：在此项目目录下运行；Agent 会根据 AGENTS.md 找到 SKILL.md、脚本及规范。
- **ChatGPT 具备文件运行能力的模式**：把上述“最快使用”指令和链接交给 Agent，要求读取仓库并运行脚本。是否能自动克隆取决于工具权限。
- **其他支持 SKILL.md 的宿主**：导入本仓库目录，并保持 scripts、references 目录完整可访问。

## 常见问题

**Q：只给“书名号xxx,书名XXX”，为什么没有 Word？** 需要 Agent 实际读到仓库、有写作模型并能执行 Python。parse_books.py 只负责解析，不负责自动写作。

**Q：必须上传原书 PDF 吗？** 不是必需，但指定版本有助于准确。没原文只能写高置信、通用的概括，不能编造详情。

**Q：汉字没到700，但 Word 里看起来很多字？** 统计仅包含汉字字符，不计标点和阿拉伯数字。建议每部分写 900 汉字以上。

**Q：为什么通用模板没有学校 Logo？** 为了可移植性，通用生成器只写基本封面/身份栏/正文。要完整复现学校版式，必须提供有权使用的原学校 DOCX，并通过 --template 参数指定。

**Q：能不能换模板或字号？** 可以。换模板用 --template；格式变化需根据具体规范调整 scripts/fill_template.py 的排版设置。

**Q：可以批量生成吗？** 可以。一个 batch.json 可放任意多本书，脚本每书生成独立文件，执行时会逐个验证。

## 安全与版权

不要把学生姓名、学号、私密文件、原著全文或未经许可的模板素材提交到公开仓库。AI 撰写后应核查事实；学校封面和材料的再分发需确认授权。仓库脚本不需要第三方 API Key。
