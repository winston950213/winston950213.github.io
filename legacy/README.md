# 旧站迁移记录

## 来源

- 旧站：<https://coderdogz.github.io/>
- 旧站仓库：<https://github.com/coderdogz/coderdogz.github.io>
- 归档日期：2026-10-28

## 迁移范围

旧站使用 Hexo + Shoka 主题。仓库中只有构建后的静态文件，没有原始 Markdown 源文件。因此迁移以站点生成的 `feed.json` 作为正文快照，并逐篇与本地静态页面的 `article.post .body` 内容核对。

共迁移 20 篇文章，时间范围为 2021-03-23 至 2022-11-04。旧站的示例文章 `Hello World` 不属于个人文章，未纳入新站。

## 图片

正文共引用 52 个图片位置、50 个唯一文件，来源为：

- `cdn.jsdelivr.net/gh/coderdogz/img`
- `gitee.com/coderdogz/blog_img`

其中 Gitee 仓库提供 22 张，GitHub/jsDelivr 仓库提供 28 张。迁移后的文件全部保存在 `public/assets/images/legacy/`。迁移脚本会校验文件确实是可解码的图片，并保留原始文件名，方便追溯。

## 正文格式处理

- 清理 Hexo 生成的表格型代码块，转换为标准 Markdown fenced code。
- 还原 `span.exturl` 中 Base64 存储的外部链接。
- 修复旧站中包裹代码块的无效 `<pre><code><figure>` 嵌套。
- 将正文中的 H1 降为 H2，避免与文章主标题冲突。
- 恢复两处被旧站转义、实际作为章节标题使用的 HTML。
- 任务清单转换为标准复选框。

`migration-report.json` 记录每篇文章的旧 URL、Markdown 文件、分类、标签、图片数量和核对结果。
