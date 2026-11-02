# Word 模板 / Templates

仓库默认**不分发任何学校的校徽或定制模板**。你可以：

1. 运行 \`python scripts/init_template.py --output assets/通用经典阅读模板.docx\` 创建通用 Word 模板；
2. 或自行把你有权使用的学校原版 DOCX 放在这里（例如 \`assets/学校读书笔记模板.docx\`），再运行 \`scripts/fill_template.py --template assets/学校读书笔记模板.docx\`。

模板须含“《xxx》读书笔记”“内容概括”“读书感悟”和年级、专业、班级、姓名四个信息栏，脚本会保留原有封面图片和布局。个人信息应在每次运行的 JSON 中输入，不要将其写进公开模板。
