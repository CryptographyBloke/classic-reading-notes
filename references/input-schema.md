# 输入 JSON 格式

将 Agent 已撰写好的文章保存为 UTF-8 \`batch.json\`。此文件是传给 \`scripts/fill_template.py\` 的输入；书名解析器只能生成空白草稿，**不会产生文章**。

~~~json
{
  "profile": {
    "grade": "24级",
    "major": "网络空间安全",
    "class_name": "示例班",
    "name": "示例同学"
  },
  "books": [
    {
      "code": "122",
      "title": "活着",
      "author": "余华",
      "summary": ["第一段概括……", "第二段概括……"],
      "reflection": ["第一段感悟……", "第二段感悟……"]
    }
  ]
}
~~~

上面的两部分文字**只是格式示例**，长度不达标，正式生成必须各不少于700个汉字。

- \`profile\`：可选对象；四个字段可为空字符串。不要从仓库推断任何人的真实资料。
- \`books\`：至少一个对象；\`title\` 必填，\`code\`、\`author\` 可选；\`summary\` 和 \`reflection\` 必须是**非空字符串数组**。
- 默认统计 Unicode 常用汉字 U+4E00..U+9FFF，不计标点、空格、英文字母和数字；推荐两部分分别写900–1200汉字。
- 生成文件名：\`书籍码_书名_姓名_模板版.docx\`，若某字段缺失则不出现对应片段。
- 使用 UTF-8，无尾随逗号；同批中不同书不得使用相同编号与标题。
- \`--min-han 800\` 可更改字数要求；英文写作可以用 \`--min-han 0 --min-nonspace 700\`。

运行：

~~~bash
python scripts/fill_template.py --input batch.json --template assets/通用经典阅读模板.docx --output-dir output
python scripts/check_documents.py --input batch.json --output-dir output
~~~
